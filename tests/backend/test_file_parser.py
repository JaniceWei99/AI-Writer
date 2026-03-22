"""Tests for services/file_parser.py — extract_text for various formats."""

import io
import pytest
from services.file_parser import extract_text, SUPPORTED_EXTENSIONS, MAX_FILE_SIZE


# ── Plain text / TXT ─────────────────────────────────────────────────


class TestPlainText:
    def test_utf8(self):
        text = "Hello, 你好世界"
        result = extract_text("test.txt", text.encode("utf-8"))
        assert result == text

    def test_gbk(self):
        text = "你好世界"
        result = extract_text("test.txt", text.encode("gbk"))
        assert result == text

    def test_empty_file(self):
        result = extract_text("empty.txt", b"")
        assert result == ""

    def test_markdown(self):
        md = "# Title\n\nSome content"
        result = extract_text("readme.md", md.encode("utf-8"))
        assert "# Title" in result

    def test_csv(self):
        csv = "name,age\nAlice,30"
        result = extract_text("data.csv", csv.encode("utf-8"))
        assert "Alice" in result

    def test_json(self):
        json_str = '{"key": "value"}'
        result = extract_text("data.json", json_str.encode("utf-8"))
        assert '"key"' in result

    def test_xml(self):
        xml = "<root><item>hello</item></root>"
        result = extract_text("data.xml", xml.encode("utf-8"))
        assert "<item>hello</item>" in result

    def test_html(self):
        html = "<html><body><p>text</p></body></html>"
        result = extract_text("page.html", html.encode("utf-8"))
        assert "<p>text</p>" in result

    def test_htm_extension(self):
        html = "<p>content</p>"
        result = extract_text("page.htm", html.encode("utf-8"))
        assert "content" in result


# ── PDF ──────────────────────────────────────────────────────────────


class TestPDF:
    def _make_pdf(self, text: str) -> bytes:
        from PyPDF2 import PdfWriter
        from PyPDF2.generic import NameObject, ArrayObject, NumberObject, TextStringObject
        from reportlab.pdfgen import canvas as rl_canvas

        buf = io.BytesIO()
        c = rl_canvas.Canvas(buf)
        c.drawString(72, 720, text)
        c.save()
        return buf.getvalue()

    def test_extract_pdf(self):
        pytest.importorskip("reportlab")
        pdf_bytes = self._make_pdf("Hello PDF World")
        result = extract_text("doc.pdf", pdf_bytes)
        assert "Hello PDF World" in result


# ── DOCX ─────────────────────────────────────────────────────────────


class TestDocx:
    def _make_docx(self, text: str) -> bytes:
        import docx
        doc = docx.Document()
        doc.add_paragraph(text)
        buf = io.BytesIO()
        doc.save(buf)
        return buf.getvalue()

    def test_extract_docx(self):
        docx_bytes = self._make_docx("Hello Docx World")
        result = extract_text("doc.docx", docx_bytes)
        assert "Hello Docx World" in result

    def test_doc_extension_uses_docx_parser(self):
        docx_bytes = self._make_docx("Doc extension")
        result = extract_text("doc.doc", docx_bytes)
        assert "Doc extension" in result


# ── Validation ───────────────────────────────────────────────────────


class TestValidation:
    def test_unsupported_extension(self):
        with pytest.raises(ValueError, match="不支持的文件类型"):
            extract_text("image.png", b"fake")

    def test_file_too_large(self):
        big = b"x" * (MAX_FILE_SIZE + 1)
        with pytest.raises(ValueError, match="10 MB"):
            extract_text("big.txt", big)

    def test_supported_extensions_set(self):
        for ext in (".pdf", ".docx", ".doc", ".txt", ".md", ".csv", ".json", ".xml", ".html", ".htm"):
            assert ext in SUPPORTED_EXTENSIONS
