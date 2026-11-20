#!/usr/bin/env python3
"""
Generate publication-quality PDF from FINAL_PROJECT_REPORT.md using Playwright and Chrome.
Enforces the academic report constraint:
- Body (Title, Abstract, Sections 1-7): <= 5 pages
- Appendices (Appendix A-C): Starts on new page (Page 6+)
"""

import sys
import os
import re
from pathlib import Path
import pypdf
from playwright.sync_api import sync_playwright

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME_PATH):
    CHROME_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

DOCS_DIR = Path(__file__).resolve().parent
MD_PATH = DOCS_DIR / "FINAL_PROJECT_REPORT.md"
PDF_PATH = DOCS_DIR / "FINAL_PROJECT_REPORT.pdf"
HTML_PATH = DOCS_DIR / "FINAL_PROJECT_REPORT.html"


def md_to_html(md_text: str) -> str:
    # Separate body and appendices
    appendix_marker = "## Appendices"
    if appendix_marker in md_text:
        body_text, appendix_text = md_text.split(appendix_marker, 1)
        appendix_text = "## Appendices" + appendix_text
    else:
        body_text = md_text
        appendix_text = ""

    def process_content(txt: str) -> str:
        lines = txt.split("\n")
        html_out = []
        in_code = False
        code_lines = []
        in_table = False
        table_rows = []

        def flush_table():
            nonlocal in_table, table_rows, html_out
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
                html_out.append('<div class="table-container"><table>')
                for r_idx, row in enumerate(rows_data):
                    html_out.append('<tr>')
                    tag = 'th' if r_idx == 0 else 'td'
                    for c in row:
                        c_formatted = format_inline(c)
                        html_out.append(f'<{tag}>{c_formatted}</{tag}>')
                    html_out.append('</tr>')
                html_out.append('</table></div>')
            table_rows = []
            in_table = False

        def flush_code():
            nonlocal in_code, code_lines, html_out
            if code_lines:
                code_content = "\n".join(code_lines)
                # escape html
                code_content = code_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                html_out.append(f'<pre class="code-block"><code>{code_content}</code></pre>')
            code_lines = []
            in_code = False

        def format_inline(line: str) -> str:
            # KaTeX-like / math replacements
            line = line.replace(r'$$\text{Score} = 100{,}000 \cdot C_4 + 500 \cdot C_3 + 50 \cdot C_2 + 30 \cdot C_{\text{center}}$$ ',
                                '<div class="math-eq"><i>Score</i> = 100,000·<i>C</i><sub>4</sub> + 500·<i>C</i><sub>3</sub> + 50·<i>C</i><sub>2</sub> + 30·<i>C</i><sub>center</sub></div>')
            line = line.replace(r'$$\text{Score} = 100{,}000 \cdot C_4 + 500 \cdot C_3 + 50 \cdot C_2 + 30 \cdot C_{\text{center}}$$',
                                '<div class="math-eq"><i>Score</i> = 100,000·<i>C</i><sub>4</sub> + 500·<i>C</i><sub>3</sub> + 50·<i>C</i><sub>2</sub> + 30·<i>C</i><sub>center</sub></div>')
            line = re.sub(r'\\text\{Age\}', 'Age', line)
            line = re.sub(r'\\Delta\\text\{Age\}', 'ΔAge', line)
            line = re.sub(r'\\ge\s*', '≥ ', line)
            line = re.sub(r'\\le\s*', '≤ ', line)
            line = re.sub(r'\\pm\s*', '± ', line)
            line = re.sub(r'\\text\{s\}', 's', line)
            line = line.replace(r'\to', '→')
            line = line.replace(r'\cdot', '·')
            # Remove leftover math $ signs
            line = re.sub(r'\$([^\$]+)\$', r'\1', line)

            # Markdown links
            line = re.sub(r'\[(.*?)\]\((.*?)\)', r'<span class="file-ref">\1</span>', line)
            # Bold
            line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
            # Italic
            line = re.sub(r'\*(.*?)\*', r'<em>\1</em>', line)
            # Inline code
            line = re.sub(r'`(.*?)`', r'<code>\1</code>', line)
            return line

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("```"):
                if in_code:
                    flush_code()
                else:
                    if in_table:
                        flush_table()
                    in_code = True
                    code_lines = []
                continue

            if in_code:
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

            # Headers
            if stripped.startswith("# "):
                html_out.append(f'<h1 class="report-title">{format_inline(stripped[2:])}</h1>')
            elif stripped.startswith("## "):
                sec_title = format_inline(stripped[3:])
                if stripped.startswith("## 7."):
                    html_out.append(f'<div class="page-break"></div><h2 class="section-title">{sec_title}</h2>')
                else:
                    html_out.append(f'<h2 class="section-title">{sec_title}</h2>')
            elif stripped.startswith("### "):
                html_out.append(f'<h3 class="subsection-title">{format_inline(stripped[4:])}</h3>')
            elif stripped.startswith("---"):
                html_out.append('<hr class="divider" />')
            elif stripped.startswith("* ") or stripped.startswith("- "):
                html_out.append(f'<li class="list-item">{format_inline(stripped[2:])}</li>')
            elif re.match(r'^\d+\.\s+', stripped):
                num_text = re.sub(r'^\d+\.\s+', '', stripped)
                html_out.append(f'<li class="ordered-item">{format_inline(num_text)}</li>')
            else:
                if stripped.startswith("*(") and stripped.endswith(")*"):
                    html_out.append(f'<p class="contribution-note">{format_inline(stripped)}</p>')
                else:
                    html_out.append(f'<p class="paragraph">{format_inline(stripped)}</p>')

        if in_table:
            flush_table()
        if in_code:
            flush_code()

        return "\n".join(html_out)

    body_html = process_content(body_text)
    appendix_html = process_content(appendix_text) if appendix_text else ""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>ConnectFour Connect Final Project Report</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 18mm 16mm 18mm 16mm;
    @top-center {{
      content: "AILT9019 AI Literacy II · ConnectFour Connect (Group 31)";
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 7.5pt;
      color: #64748b;
    }}
    @bottom-center {{
      content: "Page " counter(page) " of " counter(pages);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 8pt;
      color: #64748b;
    }}
  }}

  *, *:before, *:after {{
    box-sizing: border-box;
  }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 9.2pt;
    line-height: 1.38;
    color: #1e293b;
    margin: 0;
    padding: 0;
    background: #ffffff;
  }}

  .report-title {{
    font-size: 15.5pt;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.25;
    margin: 0 0 6px 0;
    letter-spacing: -0.3px;
  }}

  .section-title {{
    font-size: 11pt;
    font-weight: 700;
    color: #1e3a8a;
    border-bottom: 1.5px solid #cbd5e1;
    padding-bottom: 2px;
    margin: 12px 0 4px 0;
    page-break-after: avoid;
    break-after: avoid;
  }}

  .subsection-title {{
    font-size: 9.8pt;
    font-weight: 700;
    color: #0369a1;
    margin: 8px 0 2px 0;
    page-break-after: avoid;
    break-after: avoid;
  }}

  .contribution-note {{
    font-size: 8.2pt;
    font-style: italic;
    color: #475569;
    background: #f1f5f9;
    padding: 2.5px 8px;
    border-left: 3px solid #0284c7;
    border-radius: 2px;
    margin: 2px 0 5px 0;
  }}

  .paragraph {{
    margin: 0 0 5px 0;
    text-align: justify;
    text-justify: inter-word;
  }}

  .divider {{
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 8px 0;
  }}

  .list-item, .ordered-item {{
    margin: 0 0 3px 18px;
    text-align: justify;
  }}

  .table-container {{
    margin: 6px 0 8px 0;
    page-break-inside: avoid;
    break-inside: avoid;
  }}

  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 8.0pt;
    line-height: 1.28;
  }}

  th {{
    background-color: #0f172a;
    color: #ffffff;
    font-weight: 700;
    text-align: left;
    padding: 4px 6px;
    border: 1px solid #0f172a;
  }}

  td {{
    padding: 3.5px 6px;
    border: 1px solid #cbd5e1;
    vertical-align: top;
  }}

  tr:nth-child(even) td {{
    background-color: #f8fafc;
  }}

  .code-block {{
    background-color: #0f172a;
    color: #f1f5f9;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 7.4pt;
    line-height: 1.25;
    padding: 6px 9px;
    border-radius: 4px;
    margin: 5px 0 7px 0;
    white-space: pre;
    overflow-x: hidden;
    page-break-inside: avoid;
    break-inside: avoid;
  }}

  code {{
    font-family: "Consolas", "Courier New", monospace;
    font-size: 8.2pt;
    background: #f1f5f9;
    color: #0f172a;
    padding: 1px 3px;
    border-radius: 2px;
    border: 1px solid #e2e8f0;
  }}

  .file-ref {{
    color: #0369a1;
    font-weight: 600;
  }}

  .math-eq {{
    text-align: center;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 3px 6px;
    margin: 4px 0;
    font-size: 8.8pt;
  }}

  .page-break {{
    page-break-before: always;
    break-before: page;
  }}

  .appendix-header {{
    background: #e0f2fe;
    border-left: 4px solid #0284c7;
    padding: 4px 8px;
    margin: 10px 0 6px 0;
    font-size: 8.5pt;
    color: #0369a1;
    font-weight: 600;
  }}
</style>
</head>
<body>

<!-- MAIN REPORT BODY (Sections 1 to 7) -->
<div id="report-body">
{body_html}
</div>

<!-- APPENDICES (Exempt from 5-page limit, starts on new page) -->
{f'<div class="page-break"></div><div id="report-appendices"><div class="appendix-header">SUPPLEMENTARY APPENDICES (EXEMPT FROM 5-PAGE REPORT LIMIT)</div>{appendix_html}</div>' if appendix_html else ''}

</body>
</html>
"""
    return html


def generate_pdf():
    text = MD_PATH.read_text(encoding="utf-8")
    html_content = md_to_html(text)
    HTML_PATH.write_text(html_content, encoding="utf-8")
    print(f"Generated intermediate HTML at: {HTML_PATH}")

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME_PATH)
        page = browser.new_page()
        page.goto(f"file:///{HTML_PATH.as_posix()}", wait_until="networkidle")

        # Generate Full PDF
        page.pdf(
            path=str(PDF_PATH),
            format="A4",
            print_background=True,
            margin={"top": "16mm", "bottom": "16mm", "left": "15mm", "right": "15mm"},
            display_header_footer=True,
            header_template='<div style="font-size: 7.5pt; font-family: sans-serif; color: #64748b; width: 100%; text-align: center; border-bottom: 0.5px solid #e2e8f0; padding-bottom: 3px;">AILT9019 AI Literacy II · ConnectFour Connect (Group 31) · Final Project Report</div>',
            footer_template='<div style="font-size: 7.5pt; font-family: sans-serif; color: #64748b; width: 100%; text-align: center; padding-top: 3px;">Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>',
        )
        browser.close()

    print(f"PDF successfully exported to: {PDF_PATH}")

    # Inspect page counts using PyPDF
    reader = pypdf.PdfReader(str(PDF_PATH))
    total_pages = len(reader.pages)
    print(f"Total PDF Page Count: {total_pages}")

    # Determine body page count (where does Appendix appear?)
    appendix_page = None
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if "SUPPLEMENTARY APPENDICES" in text or "Appendices" in text and "Appendix A" in text:
            appendix_page = idx + 1
            break

    if appendix_page:
        body_pages = appendix_page - 1
        print(f"Body Page Count (Sections 1-7): {body_pages} pages")
        print(f"Appendices start on page: {appendix_page}")
        if body_pages <= 5:
            print("SUCCESS: Body is within the 5-page limit (<= 5 pages)!")
        else:
            print(f"WARNING: Body is {body_pages} pages (> 5 pages). Tuning typography needed.")
    else:
        print("Could not isolate appendix page marker. Total pages:", total_pages)


if __name__ == "__main__":
    generate_pdf()
