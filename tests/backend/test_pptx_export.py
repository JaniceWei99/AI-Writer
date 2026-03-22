"""Tests for services/pptx_export.py — Markdown to PPTX conversion."""

import io
import pytest
from pptx import Presentation

from services.pptx_export import markdown_to_pptx, _parse_slides, THEMES


# ── Parser ───────────────────────────────────────────────────────────


class TestParseSlides:
    def test_basic_heading_and_bullets(self):
        md = "## Slide One\n- Bullet A\n- Bullet B"
        slides = _parse_slides(md)
        assert len(slides) == 1
        assert slides[0].title == "Slide One"
        assert slides[0].bullets == ["Bullet A", "Bullet B"]

    def test_numbered_heading(self):
        md = "## 1. Introduction\n- Point"
        slides = _parse_slides(md)
        assert slides[0].title == "Introduction"

    def test_multiple_slides_with_separator(self):
        md = "## First\n- A\n---\n## Second\n- B"
        slides = _parse_slides(md)
        assert len(slides) == 2
        assert slides[0].title == "First"
        assert slides[1].title == "Second"

    def test_multiple_slides_without_separator(self):
        md = "## First\n- A\n## Second\n- B"
        slides = _parse_slides(md)
        assert len(slides) == 2

    def test_speaker_notes(self):
        md = "## Title\n- Bullet\n> Speaker notes here"
        slides = _parse_slides(md)
        assert slides[0].notes == "Speaker notes here"

    def test_speaker_notes_prefix_stripped(self):
        md = "## Title\n- Bullet\n> 演讲备注：This is the note"
        slides = _parse_slides(md)
        assert slides[0].notes == "This is the note"

    def test_ordered_list_as_bullets(self):
        md = "## Title\n1. First\n2. Second"
        slides = _parse_slides(md)
        assert slides[0].bullets == ["First", "Second"]

    def test_empty_input(self):
        slides = _parse_slides("")
        assert slides == []

    def test_only_whitespace(self):
        slides = _parse_slides("   \n  \n  ")
        assert slides == []

    def test_content_before_first_heading(self):
        md = "Some intro text\n## Actual Slide\n- Bullet"
        slides = _parse_slides(md)
        assert len(slides) == 2
        assert slides[0].bullets == ["Some intro text"]
        assert slides[1].title == "Actual Slide"

    def test_asterisk_and_plus_bullets(self):
        md = "## Title\n* Star bullet\n+ Plus bullet"
        slides = _parse_slides(md)
        assert slides[0].bullets == ["Star bullet", "Plus bullet"]

    def test_multi_line_notes(self):
        md = "## Title\n- Bullet\n> Line one\n> Line two"
        slides = _parse_slides(md)
        assert "Line one" in slides[0].notes
        assert "Line two" in slides[0].notes


# ── PPTX builder ─────────────────────────────────────────────────────


class TestMarkdownToPptx:
    def test_returns_bytesio(self):
        md = "## Slide 1\n- Hello"
        buf = markdown_to_pptx(md, "Test")
        assert isinstance(buf, io.BytesIO)
        assert buf.getbuffer().nbytes > 0

    def test_valid_pptx(self):
        md = "## Cover\n- Subtitle\n---\n## Content\n- Bullet\n---\n## 谢谢\n- Q&A"
        buf = markdown_to_pptx(md, "Test Presentation")
        prs = Presentation(buf)
        assert len(prs.slides) == 3

    def test_single_slide(self):
        md = "## Only One\n- Point"
        buf = markdown_to_pptx(md)
        prs = Presentation(buf)
        assert len(prs.slides) == 1

    def test_fallback_when_no_slides(self):
        md = ""
        buf = markdown_to_pptx(md, "Fallback Title")
        prs = Presentation(buf)
        assert len(prs.slides) == 1

    def test_all_themes(self):
        md = "## Slide\n- Bullet"
        for template_name in THEMES:
            buf = markdown_to_pptx(md, template=template_name)
            prs = Presentation(buf)
            assert len(prs.slides) >= 1

    def test_unknown_template_falls_back(self):
        md = "## Slide\n- Bullet"
        buf = markdown_to_pptx(md, template="nonexistent")
        prs = Presentation(buf)
        assert len(prs.slides) >= 1

    def test_speaker_notes_embedded(self):
        md = "## Slide\n- Bullet\n> My speaker note"
        buf = markdown_to_pptx(md)
        prs = Presentation(buf)
        slide = prs.slides[0]
        notes_text = slide.notes_slide.notes_text_frame.text
        assert "My speaker note" in notes_text

    def test_slide_dimensions(self):
        md = "## Slide\n- Bullet"
        buf = markdown_to_pptx(md)
        prs = Presentation(buf)
        # 13.33 inches wide, 7.5 inches tall
        assert prs.slide_width > 0
        assert prs.slide_height > 0

    def test_with_images(self):
        """Content slides with images should have a picture shape."""
        md = "## Cover\n- Subtitle\n---\n## Content Slide\n- Bullet\n---\n## 谢谢\n- Q&A"
        # Create a minimal valid PNG (1x1 pixel)
        import struct, zlib
        def _make_png():
            sig = b'\x89PNG\r\n\x1a\n'
            ihdr_data = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
            ihdr_crc = struct.pack('>I', zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff)
            ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + ihdr_crc
            raw = zlib.compress(b'\x00\x00\x00\x00')
            idat_crc = struct.pack('>I', zlib.crc32(b'IDAT' + raw) & 0xffffffff)
            idat = struct.pack('>I', len(raw)) + b'IDAT' + raw + idat_crc
            iend_crc = struct.pack('>I', zlib.crc32(b'IEND') & 0xffffffff)
            iend = struct.pack('>I', 0) + b'IEND' + iend_crc
            return sig + ihdr + idat + iend

        png_bytes = _make_png()
        # Provide image for slide index 1 (the content slide)
        images = {1: png_bytes}
        buf = markdown_to_pptx(md, images=images)
        prs = Presentation(buf)
        assert len(prs.slides) == 3
        # Content slide (index 1) should have a picture
        content_slide = prs.slides[1]
        from pptx.shapes.picture import Picture
        pictures = [s for s in content_slide.shapes if isinstance(s, Picture)]
        assert len(pictures) == 1

    def test_without_images_no_pictures(self):
        """Without images dict, no picture shapes should be present."""
        md = "## Cover\n- Sub\n---\n## Content\n- Bullet"
        buf = markdown_to_pptx(md)
        prs = Presentation(buf)
        from pptx.shapes.picture import Picture
        for slide in prs.slides:
            pictures = [s for s in slide.shapes if isinstance(s, Picture)]
            assert len(pictures) == 0
