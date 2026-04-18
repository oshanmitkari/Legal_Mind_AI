"""Utilities for chunking text and persisting document vectors in FAISS."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from json import JSONDecodeError
import os
import re
from typing import Dict, List

import numpy as np


EMBEDDING_DIMENSION = 128
INDEX_FILENAME = "documents.faiss"
METADATA_FILENAME = "documents_metadata.json"


@dataclass
class VectorizedDocument:
    """Result details returned after indexing a document."""

    document_key: str
    chunk_count: int
    vector_ids: List[int]


@dataclass
class RetrievedChunk:
    """A single chunk returned from semantic retrieval."""

    vector_id: int
    document_id: int
    case_id: int
    chunk_index: int
    text: str
    file_path: str
    score: float


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> List[str]:
    """Split extracted text into overlapping chunks for vectorization."""
    cleaned = re.sub(r"\s+", " ", (text or "")).strip()
    if not cleaned:
        return []

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    start = 0
    length = len(cleaned)
    while start < length:
        end = min(start + chunk_size, length)
        chunks.append(cleaned[start:end])
        if end >= length:
            break
        start = end - overlap

    return chunks


def embed_texts(texts: List[str], dimension: int = EMBEDDING_DIMENSION) -> np.ndarray:
    """Generate deterministic placeholder embeddings for each text chunk."""
    vectors = np.zeros((len(texts), dimension), dtype="float32")

    for row, text in enumerate(texts):
        tokens = re.findall(r"\w+", text.lower())
        if not tokens:
            continue

        for token in tokens:
            digest = sha256(token.encode("utf-8")).digest()
            bucket = int.from_bytes(digest[:4], byteorder="big") % dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            weight = 1.0 + (digest[5] / 255.0)
            vectors[row, bucket] += sign * weight

        norm = np.linalg.norm(vectors[row])
        if norm > 0:
            vectors[row] /= norm

    return vectors


def add_document(
    index_directory: str,
    *,
    case_id: int,
    document_id: int,
    file_path: str,
    text: str,
) -> VectorizedDocument:
    """Chunk, embed, and persist a document in the FAISS store."""
    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("No extractable text was found in the PDF.")

    index, metadata = _load_store(index_directory)
    vectors = embed_texts(chunks)

    next_vector_id = int(metadata.get("next_vector_id", 1))
    vector_ids = np.arange(next_vector_id, next_vector_id + len(chunks), dtype=np.int64)
    index.add_with_ids(vectors, vector_ids)

    documents_meta = metadata.setdefault("documents", {})
    document_key = f"doc-{document_id}"
    documents_meta[document_key] = {
        "document_id": document_id,
        "case_id": case_id,
        "file_path": file_path,
        "chunk_count": len(chunks),
        "vector_ids": [int(vector_id) for vector_id in vector_ids],
    }

    chunks_meta = metadata.setdefault("chunks", {})
    for chunk_index, vector_id in enumerate(vector_ids):
        chunks_meta[str(int(vector_id))] = {
            "document_id": document_id,
            "case_id": case_id,
            "file_path": file_path,
            "chunk_index": chunk_index,
            "text": chunks[chunk_index],
        }

    metadata["next_vector_id"] = int(next_vector_id + len(chunks))
    _save_store(index_directory, index, metadata)

    return VectorizedDocument(
        document_key=document_key,
        chunk_count=len(chunks),
        vector_ids=[int(vector_id) for vector_id in vector_ids],
    )


def remove_document(index_directory: str, document_key: str) -> bool:
    """Remove a document's vectors and metadata from the persisted FAISS store."""
    index, metadata = _load_store(index_directory)
    document_meta = metadata.get("documents", {}).pop(document_key, None)
    if not document_meta:
        return False

    vector_ids = np.array(document_meta.get("vector_ids", []), dtype=np.int64)
    if vector_ids.size:
        index.remove_ids(vector_ids)

    chunks_meta = metadata.get("chunks", {})
    for vector_id in document_meta.get("vector_ids", []):
        chunks_meta.pop(str(vector_id), None)

    _save_store(index_directory, index, metadata)
    return True


def search_similar_chunks(
    index_directory: str,
    *,
    query_text: str,
    case_id: int,
    top_k: int = 5,
    candidate_pool: int = 25,
) -> List[RetrievedChunk]:
    """Search the persisted vector store for chunks relevant to a case."""
    cleaned_query = re.sub(r"\s+", " ", (query_text or "")).strip()
    if not cleaned_query:
        return []

    index, metadata = _load_store(index_directory)
    chunks_meta = metadata.get("chunks", {})
    if not chunks_meta:
        return []

    query_vector = embed_texts([cleaned_query])
    search_k = min(max(candidate_pool, top_k), len(chunks_meta))
    distances, ids = index.search(query_vector, search_k)

    results = []
    for score, vector_id in zip(distances[0], ids[0]):
        if int(vector_id) == -1:
            continue

        chunk_meta = chunks_meta.get(str(int(vector_id)))
        if not chunk_meta or int(chunk_meta.get("case_id", -1)) != case_id:
            continue

        results.append(
            RetrievedChunk(
                vector_id=int(vector_id),
                document_id=int(chunk_meta["document_id"]),
                case_id=int(chunk_meta["case_id"]),
                chunk_index=int(chunk_meta["chunk_index"]),
                text=chunk_meta["text"],
                file_path=chunk_meta["file_path"],
                score=float(score),
            )
        )
        if len(results) >= top_k:
            break

    return results


def _load_store(index_directory: str):
    """Load or initialize the FAISS index and metadata files."""
    faiss = _get_faiss()
    os.makedirs(index_directory, exist_ok=True)
    index_path = os.path.join(index_directory, INDEX_FILENAME)
    metadata_path = os.path.join(index_directory, METADATA_FILENAME)

    if os.path.exists(index_path):
        index = faiss.read_index(index_path)
    else:
        index = faiss.IndexIDMap2(faiss.IndexFlatL2(EMBEDDING_DIMENSION))

    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r", encoding="utf-8") as handle:
                metadata = json.load(handle)
        except JSONDecodeError:
            metadata = {
                "dimension": EMBEDDING_DIMENSION,
                "next_vector_id": 1,
                "documents": {},
                "chunks": {},
            }
    else:
        metadata = {
            "dimension": EMBEDDING_DIMENSION,
            "next_vector_id": 1,
            "documents": {},
            "chunks": {},
        }

    return index, metadata


def _save_store(index_directory: str, index, metadata: Dict):
    """Persist both FAISS index bytes and JSON metadata to disk."""
    faiss = _get_faiss()
    index_path = os.path.join(index_directory, INDEX_FILENAME)
    metadata_path = os.path.join(index_directory, METADATA_FILENAME)

    faiss.write_index(index, index_path)
    temp_metadata_path = metadata_path + ".tmp"
    with open(temp_metadata_path, "w", encoding="utf-8") as handle:
        json.dump(metadata, handle, ensure_ascii=True, indent=2)
    os.replace(temp_metadata_path, metadata_path)


def _get_faiss():
    """Import FAISS lazily so the app can boot even if the package is missing."""
    try:
        import faiss
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "FAISS is not installed in the active Python environment. "
            "Install dependencies from backend/requirements.txt to enable PDF vector indexing."
        ) from exc
    return faiss
