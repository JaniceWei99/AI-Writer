"""Extract text content from uploaded files (PDF, Word, TXT, etc.)."""

import io
from pathlib import Path

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md", ".csv", ".json", ".xml", ".html", ".htm"}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def extract_text(filename: str, file_bytes: bytes) -> str:
    """Read file bytes and return plain text content."""
    ext = Path(filename).suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"不支持的文件类型: {ext}，支持: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")

    if len(file_bytes) > MAX_FILE_SIZE:
        raise ValueError("文件大小超过 10 MB 限制")

    if ext == ".pdf":
        return _extract_pdf(file_bytes)
    elif ext in (".docx", ".doc"):
        return _extract_docx(file_bytes)
    else:
        return _extract_plain(file_bytes)


def _extract_pdf(data: bytes) -> str:
    import PyPDF2
    reader = PyPDF2.PdfReader(io.BytesIO(data))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages)


def _extract_docx(data: bytes) -> str:
    import docx
    doc = docx.Document(io.BytesIO(data))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


def _extract_plain(data: bytes) -> str:
    for encoding in ("utf-8", "gbk", "gb2312", "latin-1"):
        try:
            return data.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    return data.decode("utf-8", errors="replace")
