from pathlib import Path
from pypdf import PdfReader
from docx import Document

def extract_text(path: Path) -> list[tuple[int, str]]:
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return [(1, path.read_text(encoding="utf-8", errors="replace"))]
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        return [(index + 1, page.extract_text() or "")
                for index, page in enumerate(reader.pages)]
    if suffix == ".docx":
        doc = Document(str(path))
        text = "\\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return [(1, text)]
    raise ValueError("Unsupported document type")
