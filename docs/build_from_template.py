#!/usr/bin/env python3
"""
Build AILT9019_Final_Report_G31.docx and FINAL_PROJECT_REPORT.docx directly from
AILT9019_Final_Report_Template.docx.
Maintains all official course template properties:
- Page margins: 0.85in top/bottom, 0.95in left/right
- Typography: Calibri
- Navy Titles: 1F3864
- Grey Requirement Lines: 595959
- Formatted tables, code blocks, lists
- Five-page body limit target
"""

import os
import re
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

DOCS_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = DOCS_DIR / "AILT9019_Final_Report_Template.docx"
MD_PATH = DOCS_DIR / "FINAL_PROJECT_REPORT.md"
DOCX_OUT_1 = DOCS_DIR / "AILT9019_Final_Report_G31.docx"
DOCX_OUT_2 = DOCS_DIR / "FINAL_PROJECT_REPORT.docx"

NAVY_COLOR = RGBColor(0x1F, 0x38, 0x64)
GREY_COLOR = RGBColor(0x59, 0x59, 0x59)
BODY_COLOR = RGBColor(0x1E, 0x29, 0x3B)
CODE_BG = "0F172A"


def set_cell_background(cell, hex_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)


def set_cell_margins(cell, top=70, bottom=70, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def build_docx():
    if TEMPLATE_PATH.exists():
        doc = Document(TEMPLATE_PATH)
        # Clear existing paragraphs in template
        p_elements = [p._p for p in doc.paragraphs]
        for p in p_elements:
            p.getparent().remove(p)
    else:
        doc = Document()
        for s in doc.sections:
            s.top_margin = Inches(0.85)
            s.bottom_margin = Inches(0.85)
            s.left_margin = Inches(0.95)
            s.right_margin = Inches(0.95)

    md_text = MD_PATH.read_text(encoding="utf-8")
    lines = md_text.split("\n")

    in_code_block = False
    code_lines = []
    in_table = False
    table_rows = []

    def flush_table():
        nonlocal in_table, table_rows
        if not table_rows:
            in_table = False
            return

        rows_data = []
        for r in table_rows:
            if re.match(r'^\s*\|?\s*:?-+:?\s*\|', r):
                continue
            cells = [c.strip() for c in r.strip('|').split('|')]
            rows_data.append(cells)

        if rows_data:
            cols_count = max(len(r) for r in rows_data)
            table = doc.add_table(rows=len(rows_data), cols=cols_count)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            table.autofit = True

            for r_idx, row in enumerate(rows_data):
                for c_idx, cell_value in enumerate(row):
                    if c_idx < cols_count:
                        cell = table.cell(r_idx, c_idx)
                        clean_text = cell_value.replace('<br>', '\n').replace('\\ge', '≥').replace('\\le', '≤').replace('\\text{s}', 's')
                        set_cell_margins(cell, top=60, bottom=60, left=90, right=90)
                        p = cell.paragraphs[0]
                        p.text = ""
                        p.paragraph_format.line_spacing = 1.05
                        p.paragraph_format.space_after = Pt(1.5)

                        cell_lines = clean_text.split('\n')
                        for l_i, c_line in enumerate(cell_lines):
                            if l_i > 0:
                                p = cell.add_paragraph()
                                p.paragraph_format.line_spacing = 1.05
                                p.paragraph_format.space_after = Pt(1.5)

                            c_line_clean = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', c_line)
                            c_parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', c_line_clean)
                            for part in c_parts:
                                if part.startswith("**") and part.endswith("**"):
                                    r = p.add_run(part[2:-2])
                                    r.font.name = 'Calibri'
                                    r.font.bold = True
                                elif part.startswith("*") and part.endswith("*"):
                                    r = p.add_run(part[1:-1])
                                    r.font.name = 'Calibri'
                                    r.font.italic = True
                                elif part.startswith("`") and part.endswith("`"):
                                    r = p.add_run(part[1:-1])
                                    r.font.name = 'Consolas'
                                    r.font.size = Pt(8.5)
                                else:
                                    r = p.add_run(part)
                                    r.font.name = 'Calibri'

                        if r_idx == 0:
                            set_cell_background(cell, "1F3864")
                            for p_cell in cell.paragraphs:
                                for run in p_cell.runs:
                                    run.font.bold = True
                                    run.font.color.rgb = RGBColor(255, 255, 255)
                                    run.font.size = Pt(9.0)
                        else:
                            bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
                            set_cell_background(cell, bg)
                            for p_cell in cell.paragraphs:
                                for run in p_cell.runs:
                                    run.font.size = Pt(8.5)

            p_sp = doc.add_paragraph()
            p_sp.paragraph_format.space_before = Pt(1)
            p_sp.paragraph_format.space_after = Pt(3)

        table_rows = []
        in_table = False

    def flush_code():
        nonlocal in_code_block, code_lines
        if code_lines:
            tbl = doc.add_table(rows=1, cols=1)
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            cell = tbl.cell(0, 0)
            set_cell_background(cell, CODE_BG)
            set_cell_margins(cell, top=70, bottom=70, left=100, right=100)
            cell.text = "\n".join(code_lines)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_after = Pt(0)
            for run in p.runs:
                run.font.name = 'Consolas'
                run.font.size = Pt(7.5)
                run.font.color.rgb = RGBColor(241, 245, 249)
            p_sp = doc.add_paragraph()
            p_sp.paragraph_format.space_after = Pt(3)
        code_lines = []
        in_code_block = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code_block:
                flush_code()
            else:
                if in_table:
                    flush_table()
                in_code_block = True
                code_lines = []
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            in_table = True
            table_rows.append(stripped)
            continue
        elif in_table:
            flush_table()

        if not stripped:
            continue

        # Markdown headers
        if stripped.startswith("# AILT9019"):
            p = doc.add_paragraph()
            run = p.add_run("AILT9019 · AI Literacy II")
            run.font.name = 'Calibri'
            run.font.size = Pt(12)
            run.font.bold = True
            run.font.color.rgb = NAVY_COLOR
            p.paragraph_format.space_after = Pt(2)
        elif stripped.startswith("## Final Report:"):
            p = doc.add_paragraph()
            run = p.add_run(stripped[3:])
            run.font.name = 'Calibri'
            run.font.size = Pt(18)
            run.font.bold = True
            run.font.color.rgb = NAVY_COLOR
            p.paragraph_format.space_after = Pt(2)
        elif stripped.startswith("## ") and re.match(r'^##\s+(\d+\.|Appendix)', stripped):
            # Section header
            p = doc.add_paragraph()
            run = p.add_run(stripped[3:])
            run.font.name = 'Calibri'
            run.font.size = Pt(15)
            run.font.bold = True
            run.font.color.rgb = NAVY_COLOR
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(2)
        elif stripped.startswith("### "):
            p = doc.add_paragraph()
            run = p.add_run(stripped[4:])
            run.font.name = 'Calibri'
            run.font.size = Pt(11)
            run.font.bold = True
            run.font.color.rgb = RGBColor(3, 105, 161)
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(2)
        elif stripped.startswith("---"):
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(4)
        elif stripped.startswith("*") and stripped.endswith("*") and not stripped.startswith("**"):
            # Grey template requirement line
            p = doc.add_paragraph()
            run = p.add_run(stripped[1:-1])
            run.font.name = 'Calibri'
            run.font.size = Pt(9.5)
            run.font.italic = False
            run.font.color.rgb = GREY_COLOR
            p.paragraph_format.space_after = Pt(3)
        elif stripped.startswith("* ") or stripped.startswith("- "):
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(2)
            content = stripped[2:]
            content = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', content)
            parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', content)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    r = p.add_run(part[2:-2])
                    r.font.name = 'Calibri'
                    r.font.bold = True
                elif part.startswith("*") and part.endswith("*"):
                    r = p.add_run(part[1:-1])
                    r.font.name = 'Calibri'
                    r.font.italic = True
                elif part.startswith("`") and part.endswith("`"):
                    r = p.add_run(part[1:-1])
                    r.font.name = 'Consolas'
                    r.font.size = Pt(8.5)
                else:
                    r = p.add_run(part)
                    r.font.name = 'Calibri'
                    r.font.size = Pt(9.5)
        elif re.match(r'^\d+\.\s+', stripped):
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.space_after = Pt(2)
            num_content = re.sub(r'^\d+\.\s+', '', stripped)
            num_content = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', num_content)
            parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', num_content)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    r = p.add_run(part[2:-2])
                    r.font.name = 'Calibri'
                    r.font.bold = True
                elif part.startswith("*") and part.endswith("*"):
                    r = p.add_run(part[1:-1])
                    r.font.name = 'Calibri'
                    r.font.italic = True
                elif part.startswith("`") and part.endswith("`"):
                    r = p.add_run(part[1:-1])
                    r.font.name = 'Consolas'
                    r.font.size = Pt(8.5)
                else:
                    r = p.add_run(part)
                    r.font.name = 'Calibri'
                    r.font.size = Pt(9.5)
        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.15
            content = stripped
            content = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', content)
            parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', content)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    r = p.add_run(part[2:-2])
                    r.font.name = 'Calibri'
                    r.font.bold = True
                    r.font.size = Pt(9.5)
                elif part.startswith("*") and part.endswith("*"):
                    r = p.add_run(part[1:-1])
                    r.font.name = 'Calibri'
                    r.font.italic = True
                    r.font.size = Pt(9.5)
                elif part.startswith("`") and part.endswith("`"):
                    r = p.add_run(part[1:-1])
                    r.font.name = 'Consolas'
                    r.font.size = Pt(8.5)
                else:
                    r = p.add_run(part)
                    r.font.name = 'Calibri'
                    r.font.size = Pt(9.5)

    if in_table:
        flush_table()
    if in_code_block:
        flush_code()

    doc.save(DOCX_OUT_1)
    doc.save(DOCX_OUT_2)
    print(f"Report DOCX generated at: {DOCX_OUT_1}")
    print(f"Report DOCX generated at: {DOCX_OUT_2}")


if __name__ == "__main__":
    build_docx()
