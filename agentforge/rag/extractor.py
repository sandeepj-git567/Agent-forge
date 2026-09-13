"""
Document Text Extraction Pipeline for AgentForge AI

Supports PDF, DOCX, Markdown, and Plain Text formats.
Strictly rejects unsupported file formats.
"""
import io
import os
from typing import Any

import docx
import pypdf

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


class DocumentExtractor:
    """Extracts text and metadata from supported document files."""

    @staticmethod
    def extract_text(file_bytes: bytes, filename: str) -> tuple[str, dict[str, Any]]:
        """
        Extract text from file bytes based on file extension.
        
        Returns:
            Tuple[extracted_text, metadata]
        """
        ext = os.path.splitext(filename)[1].lower()

        if ext not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file format '{ext}'. Supported formats: PDF, DOCX, TXT, MD.")

        if not file_bytes:
            raise ValueError(f"File '{filename}' is empty.")

        text_content = ""
        meta: dict[str, Any] = {"filename": filename, "extension": ext, "num_pages": 1}

        if ext == ".pdf":
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            meta["num_pages"] = len(reader.pages)
            extracted_pages = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                extracted_pages.append(page_text)
            text_content = "\n\n".join(extracted_pages)

        elif ext == ".docx":
            doc = docx.Document(io.BytesIO(file_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            text_content = "\n".join(paragraphs)
            meta["num_paragraphs"] = len(paragraphs)

        elif ext in {".txt", ".md"}:
            try:
                text_content = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                text_content = file_bytes.decode("latin-1")

        text_clean = text_content.strip()
        if not text_clean:
            raise ValueError(f"No extractable text content found in '{filename}'.")

        meta["character_count"] = len(text_clean)
        return text_clean, meta


default_extractor = DocumentExtractor()
