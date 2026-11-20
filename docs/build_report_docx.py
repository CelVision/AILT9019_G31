#!/usr/bin/env python3
"""
Convert FINAL_PROJECT_REPORT.md into a professional Microsoft Word document (FINAL_PROJECT_REPORT.docx).
Follows standard academic report formatting:
- 1-inch margins
- Professional typography (Calibri / Arial)
- Formatted tables with header styling
- Callouts, code blocks, and section contribution attributions
"""

import re
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls


def set_cell_background(cell, hex_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def build_docx():
    md_path = Path(__file__).resolve().parent / "FINAL_PROJECT_REPORT.md"
    docx_path = Path(__file__).resolve().parent / "FINAL_PROJECT_REPORT.docx"
    text = md_path.read_text(encoding="utf-8")

    doc = Document()

    # Set 1 inch margins
    sections = doc.sections
    for s in sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    # Style definitions
    styles = doc.styles
    normal_style = styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(10.5)
    normal_style.font.color.rgb = RGBColor(30, 41, 59)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(4)

    lines = text.split("\n")
    in_code_block = False
    code_lines = []
    in_table = False
    table_rows = []

    def flush_table():
        nonlocal in_table, table_rows
        if not table_rows:
            in_table = False
            return
        # Parse table rows
        rows_data = []
        for r in table_rows:
            if re.match(r'^\s*\|?\s*:?-+:?\s*\|', r):
                continue # delimiter
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
                        set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
                        p = cell.paragraphs[0]
                        p.text = ""  # clear
                        p.paragraph_format.line_spacing = 1.05
                        p.paragraph_format.space_after = Pt(2)

                        # Parse bold and formatting in cell text
                        cell_lines = clean_text.split('\n')
                        for l_i, c_line in enumerate(cell_lines):
                            if l_i > 0:
                                p = cell.add_paragraph()
                                p.paragraph_format.line_spacing = 1.05
                                p.paragraph_format.space_after = Pt(2)
                            
                            c_line_clean = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', c_line)
                            c_parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', c_line_clean)
                            for part in c_parts:
                                if part.startswith("**") and part.endswith("**"):
                                    r = p.add_run(part[2:-2])
                                    r.font.bold = True
                                elif part.startswith("*") and part.endswith("*"):
                                    r = p.add_run(part[1:-1])
                                    r.font.italic = True
                                elif part.startswith("`") and part.endswith("`"):
                                    r = p.add_run(part[1:-1])
                                    r.font.name = 'Consolas'
                                    r.font.size = Pt(8.5)
                                else:
                                    p.add_run(part)

                        if r_idx == 0:
                            set_cell_background(cell, "0F172A")
                            for p_cell in cell.paragraphs:
                                for run in p_cell.runs:
                                    run.font.bold = True
                                    run.font.color.rgb = RGBColor(255, 255, 255)
                                    run.font.size = Pt(9.5)
                        else:
                            bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
                            set_cell_background(cell, bg)
                            for p_cell in cell.paragraphs:
                                for run in p_cell.runs:
                                    run.font.size = Pt(9.0)

            # Space after table
            p_spacer = doc.add_paragraph()
            p_spacer.paragraph_format.space_before = Pt(2)
            p_spacer.paragraph_format.space_after = Pt(4)

        table_rows = []
        in_table = False

    def flush_code():
        nonlocal in_code_block, code_lines
        if code_lines:
            tbl = doc.add_table(rows=1, cols=1)
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            cell = tbl.cell(0, 0)
            set_cell_background(cell, "0F172A")
            set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
            cell.text = "\n".join(code_lines)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_after = Pt(0)
            for run in p.runs:
                run.font.name = 'Consolas'
                run.font.size = Pt(8.5)
                run.font.color.rgb = RGBColor(241, 245, 249)
            p_sp = doc.add_paragraph()
            p_sp.paragraph_format.space_after = Pt(4)
        code_lines = []
        in_code_block = False

    for line in lines:
        stripped = line.strip()

        # Code block
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

        # Table row
        if stripped.startswith("|") and stripped.endswith("|"):
            in_table = True
            table_rows.append(stripped)
            continue
        elif in_table:
            flush_table()

        if not stripped:
            continue

        # Headers
        if stripped.startswith("# "):
            p = doc.add_paragraph()
            run = p.add_run(stripped[2:])
            run.font.name = 'Calibri'
            run.font.size = Pt(19)
            run.font.bold = True
            run.font.color.rgb = RGBColor(15, 23, 42)
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(6)
        elif stripped.startswith("## "):
            p = doc.add_paragraph()
            run = p.add_run(stripped[3:])
            run.font.name = 'Calibri'
            run.font.size = Pt(14)
            run.font.bold = True
            run.font.color.rgb = RGBColor(30, 58, 138)
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
        elif stripped.startswith("### "):
            p = doc.add_paragraph()
            run = p.add_run(stripped[4:])
            run.font.name = 'Calibri'
            run.font.size = Pt(11.5)
            run.font.bold = True
            run.font.color.rgb = RGBColor(3, 105, 161)
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(2)
        elif stripped.startswith("---"):
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(6)
        elif stripped.startswith("* ") or stripped.startswith("- "):
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(2)
            # Add runs
            content = stripped[2:]
            # Clean bold/links
            content = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', content)
            parts = re.split(r'(\*\*.*?\*\*)', content)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    r = p.add_run(part[2:-2])
                    r.font.bold = True
                else:
                    p.add_run(part)
        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(4)
            content = stripped
            content = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', content)
            parts = re.split(r'(\*\*.*?\*\*|\*.*?\*)', content)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    r = p.add_run(part[2:-2])
                    r.font.bold = True
                elif part.startswith("*") and part.endswith("*"):
                    r = p.add_run(part[1:-1])
                    r.font.italic = True
                else:
                    p.add_run(part)

    if in_table:
        flush_table()
    if in_code_block:
        flush_code()

    doc.save(docx_path)
    print(f"Report DOCX successfully generated at: {docx_path}")


if __name__ == "__main__":
    build_docx()
