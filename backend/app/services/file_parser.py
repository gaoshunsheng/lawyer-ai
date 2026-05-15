from __future__ import annotations


async def parse_file(content: bytes, filename: str, content_type: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext == "pdf":
        from io import BytesIO
        from PyPDF2 import PdfReader
        try:
            reader = PdfReader(BytesIO(content))
            return "\n".join(page.extract_text() or "" for page in reader.pages[:20])
        except Exception:
            return ""
    elif ext in ("doc", "docx"):
        from io import BytesIO
        from docx import Document
        try:
            doc = Document(BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs[:100])
        except Exception:
            return ""
    elif content_type and content_type.startswith("text/"):
        return content.decode("utf-8", errors="replace")
    return ""
