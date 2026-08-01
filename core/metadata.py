from pathlib import Path


def create_document_metadata(
    document_id=None,
    subject=None,
    content_type=None,
    source_type=None,
    file_name=None,
    file_path=None,
    file_type=None,
    page=None,
    slide=None,
    chunk_id=None
):
    f_name = file_name or "Unknown"
    f_type = file_type or (Path(f_name).suffix.lower() if f_name != "Unknown" else "")

    return {
        "document_id": document_id or "unknown_doc",
        "subject": subject or "General",
        "content_type": content_type or "notes",
        "source_type": source_type or "college_notes",
        "file_name": f_name,
        "file_path": file_path or "",
        "file_type": f_type,
        "page": page,
        "slide": slide,
        "chunk_id": chunk_id or ""
    }


def normalize_metadata(raw_metadata):
    if not isinstance(raw_metadata, dict):
        raw_metadata = {}

    file_name = raw_metadata.get("file_name") or raw_metadata.get("source") or "Unknown"
    file_path = raw_metadata.get("file_path") or ""
    file_type = raw_metadata.get("file_type") or (Path(file_name).suffix.lower() if file_name != "Unknown" else "")

    doc_id = raw_metadata.get("document_id") or "unknown_doc"
    subject = raw_metadata.get("subject") or "General"
    content_type = raw_metadata.get("content_type") or "notes"
    source_type = raw_metadata.get("source_type") or "college_notes"
    page = raw_metadata.get("page")
    slide = raw_metadata.get("slide")
    chunk_id = raw_metadata.get("chunk_id") or ""

    return {
        "document_id": doc_id,
        "subject": subject,
        "content_type": content_type,
        "source_type": source_type,
        "file_name": file_name,
        "file_path": file_path,
        "file_type": file_type,
        "page": page,
        "slide": slide,
        "chunk_id": chunk_id
    }
