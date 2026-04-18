"""Document ingestion service for file storage, extraction, and vector indexing."""
from __future__ import annotations

from dataclasses import dataclass
import os

import fitz
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.models import db, Document
from app.utils.vector_store import add_document, remove_document


@dataclass
class DocumentIngestionResult:
    """Summary returned after a document has been stored and indexed."""

    document: Document
    text_length: int
    chunk_count: int


def ingest_pdf_document(
    *,
    upload_file: FileStorage,
    case_id: int,
    upload_folder: str,
    index_directory: str,
    document_type: str = "General",
) -> DocumentIngestionResult:
    """Save, extract, index, and persist a PDF document for a case."""
    filename = secure_filename(upload_file.filename or "")
    case_upload_dir = os.path.join(upload_folder, f"case_{case_id}")
    os.makedirs(case_upload_dir, exist_ok=True)

    filepath = os.path.join(case_upload_dir, filename)
    upload_file.save(filepath)

    try:
        text_content = extract_pdf_text(filepath)
        document = Document(
            case_id=case_id,
            filename=filename,
            file_path=filepath,
            document_type=document_type,
            text_content=text_content,
        )
        db.session.add(document)
        db.session.flush()

        vectorized = add_document(
            index_directory,
            case_id=case_id,
            document_id=document.id,
            file_path=filepath,
            text=text_content,
        )
        document.faiss_index_id = vectorized.document_key
        db.session.commit()
    except Exception:
        db.session.rollback()
        if os.path.exists(filepath):
            os.remove(filepath)
        raise

    return DocumentIngestionResult(
        document=document,
        text_length=len(text_content),
        chunk_count=vectorized.chunk_count,
    )


def delete_document_assets(*, document: Document, index_directory: str) -> None:
    """Delete document file and remove vectors from the persisted store."""
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    if document.faiss_index_id:
        remove_document(index_directory, document.faiss_index_id)

    db.session.delete(document)
    db.session.commit()


def extract_pdf_text(filepath: str) -> str:
    """Extract plain text from a PDF using PyMuPDF."""
    text = ""
    try:
        with fitz.open(filepath) as pdf:
            for page_num in range(pdf.page_count):
                page = pdf[page_num]
                text += page.get_text() + "\n"
    except Exception as exc:
        raise Exception(f"PDF extraction failed: {str(exc)}") from exc

    if not text.strip():
        raise Exception("No extractable text found in the PDF")

    return text
