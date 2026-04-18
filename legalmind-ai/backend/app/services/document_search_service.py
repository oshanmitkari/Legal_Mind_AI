"""Retrieval service for case document search over the FAISS-backed vector store."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.models import Document
from app.utils.vector_store import search_similar_chunks


@dataclass
class RetrievedDocumentSnippet:
    """UI and prompt friendly representation of a retrieved chunk."""

    document_id: int
    filename: str
    document_type: str
    chunk_index: int
    snippet: str
    score: float


def retrieve_case_document_snippets(
    *,
    index_directory: str,
    case_id: int,
    query_text: str,
    top_k: int = 3,
) -> List[RetrievedDocumentSnippet]:
    """Fetch top matching chunks for a case and enrich them with document metadata."""
    raw_results = search_similar_chunks(
        index_directory,
        query_text=query_text,
        case_id=case_id,
        top_k=top_k,
    )
    if not raw_results:
        return []

    document_ids = {item.document_id for item in raw_results}
    documents = {
        document.id: document
        for document in Document.query.filter(Document.id.in_(document_ids)).all()
    }

    snippets = []
    for item in raw_results:
        document = documents.get(item.document_id)
        snippets.append(
            RetrievedDocumentSnippet(
                document_id=item.document_id,
                filename=document.filename if document else item.file_path.rsplit("\\", 1)[-1],
                document_type=document.document_type if document and document.document_type else "General",
                chunk_index=item.chunk_index,
                snippet=item.text[:400].strip(),
                score=item.score,
            )
        )

    return snippets
