"""Markdown → PDF 导出服务"""

import io
import os
import re

from fpdf import FPDF

# CJK 字体搜索路径（按优先级）
_FONT_PATHS = [
    "/mnt/c/Windows/Fonts/simhei.ttf",
    "/mnt/c/Windows/Fonts/msyh.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]


def _clean_inline(text: str) -> str:
    """去除行内 Markdown 格式标记。"""
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    return text


def markdown_to_pdf(md_text: str, title: str = "") -> io.BytesIO:
    """将 Markdown 文本转为 PDF 并写入 BytesIO 缓冲区。"""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # 尝试加载 CJK 字体
    font_name = "Helvetica"
    for path in _FONT_PATHS:
        if os.path.exists(path):
            try:
                pdf.add_font("CJK", "", path)
                font_name = "CJK"
                break
            except Exception:
                continue

    pdf.set_font(font_name, "", 11)

    if title:
        pdf.set_font(font_name, "", 18)
        pdf.multi_cell(0, 12, title)
        pdf.ln(4)
        pdf.set_font(font_name, "", 11)

    for line in md_text.split("\n"):
        stripped = line.strip()

        if stripped.startswith("### "):
            pdf.set_font(font_name, "", 13)
            pdf.multi_cell(0, 8, _clean_inline(stripped[4:]))
            pdf.ln(2)
            pdf.set_font(font_name, "", 11)
        elif stripped.startswith("## "):
            pdf.set_font(font_name, "", 15)
            pdf.multi_cell(0, 10, _clean_inline(stripped[3:]))
            pdf.ln(3)
            pdf.set_font(font_name, "", 11)
        elif stripped.startswith("# "):
            pdf.set_font(font_name, "", 18)
            pdf.multi_cell(0, 12, _clean_inline(stripped[2:]))
            pdf.ln(4)
            pdf.set_font(font_name, "", 11)
        elif re.match(r"^[-*_]{3,}$", stripped):
            pdf.ln(3)
            y = pdf.get_y()
            pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
            pdf.ln(3)
        elif stripped.startswith("> "):
            text = _clean_inline(stripped[2:])
            pdf.set_x(pdf.l_margin + 10)
            pdf.set_text_color(100, 100, 100)
            pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - 10, 7, text)
            pdf.set_text_color(0, 0, 0)
        elif re.match(r"^[-*+]\s", stripped):
            text = _clean_inline(re.sub(r"^[-*+]\s+", "", stripped))
            x = pdf.get_x()
            pdf.cell(6, 7, "- ")
            pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - 6, 7, text)
        elif re.match(r"^\d+\.\s", stripped):
            m = re.match(r"^(\d+\.)\s+(.*)", stripped)
            if m:
                num, text = m.groups()
                text = _clean_inline(text)
                pdf.cell(10, 7, num + " ")
                pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - 10, 7, text)
        elif stripped == "":
            pdf.ln(4)
        else:
            pdf.multi_cell(0, 7, _clean_inline(stripped))

    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf
