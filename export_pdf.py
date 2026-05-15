"""
Export Draft 1.ipynb to PDF.

Step 1: Execute the notebook and convert to HTML (nbconvert).
Step 2: Inject compression CSS (font, spacing, margins).
Step 3: Print the HTML to PDF via Playwright + headless Chromium.

Output: docs/Report/Draft 1.pdf
"""

import asyncio
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent / 'docs' / 'Report'
NOTEBOOK = ROOT / 'Draft 1.ipynb'
HTML_OUT = ROOT / 'Draft 1.html'
PDF_OUT  = ROOT / 'Draft 1.pdf'

# CSS injected before printing — tune these to adjust page count.
COMPRESSION_CSS = """
<style>
/* Override Jupyter CSS variables — cascade to all var() references */
:root {
    --jp-content-font-size1: 11px;
    --jp-content-font-size2: 1.15em;
    --jp-content-font-size3: 1.3em;
    --jp-content-font-size4: 1.5em;
    --jp-content-font-size5: 1.8em;
    --jp-ui-font-size1: 10px;
}

@page { margin: 12mm 15mm; }

body { font-size: 11px !important; line-height: 1.3 !important; }

/* Prose */
.jp-RenderedHTMLCommon p {
    margin: 0 0 0.35em 0 !important;
    line-height: 1.35 !important;
}

/* Headings — keep with following content, never strand at page bottom */
.jp-RenderedHTMLCommon h1,
.jp-RenderedHTMLCommon h2,
.jp-RenderedHTMLCommon h3 {
    margin-top: 0.5em !important;
    margin-bottom: 0.2em !important;
    break-after: avoid !important;
    page-break-after: avoid !important;
}
.jp-RenderedHTMLCommon h1:first-child,
.jp-RenderedHTMLCommon h2:first-child,
.jp-RenderedHTMLCommon h3:first-child {
    margin-top: 0.3em !important;
}

/* Keep each notebook cell from splitting mid-content */
.jp-Cell {
    padding: 1px 0 !important;
    break-inside: avoid !important;
    page-break-inside: avoid !important;
}
.jp-MarkdownCell   { padding: 1px 0 !important; }
.jp-OutputArea     { padding: 1px 0 !important; }
.jp-OutputArea-output {
    padding: 2px 0 !important;
    break-inside: avoid !important;
    page-break-inside: avoid !important;
}
.jp-MarkdownOutput { padding: 1px 0 !important; }

.jp-RenderedHTMLCommon ul,
.jp-RenderedHTMLCommon ol { margin: 0.2em 0 0.2em 1.2em !important; }
.jp-RenderedHTMLCommon li { margin-bottom: 0.1em !important; }

/* Tables — already styled inline; don't let Jupyter override */
.jp-RenderedHTMLCommon table {
    border-collapse: collapse !important;
    font-size: 8pt !important;
}
.jp-RenderedHTMLCommon th,
.jp-RenderedHTMLCommon td { padding: 2px 5px !important; }

/* Constrain figure height so charts don't consume a full page each */
img { max-height: 260px !important; width: auto !important; max-width: 100% !important; }

/* Hide the --- horizontal rules used as section separators in Results */
hr { display: none !important; }

/* Remove prompt gutters */
.jp-InputPrompt, .jp-OutputPrompt { display: none !important; }
</style>
"""


def execute_to_html():
    print("Step 1: Executing notebook and converting to HTML...")
    result = subprocess.run(
        [
            sys.executable, '-m', 'jupyter', 'nbconvert',
            '--execute',
            '--to', 'html',
            '--no-input',
            '--output-dir', str(ROOT),
            '--ExecutePreprocessor.kernel_name=ecc3479-venv',
            '--ExecutePreprocessor.timeout=600',
            str(NOTEBOOK),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr[-3000:])
        sys.exit("nbconvert HTML export failed.")
    if not HTML_OUT.exists():
        sys.exit("nbconvert succeeded but HTML file not found.")
    print(f"  HTML written: {HTML_OUT}")


def inject_css():
    print("Step 2: Injecting compression CSS...")
    html = HTML_OUT.read_text(encoding='utf-8')
    html = re.sub(r'(</head>)', COMPRESSION_CSS + r'\1', html, count=1)
    HTML_OUT.write_text(html, encoding='utf-8')


async def html_to_pdf():
    print("Step 3: Printing HTML to PDF via headless Chromium...")
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(HTML_OUT.as_uri(), wait_until='networkidle')
        await page.pdf(
            path=str(PDF_OUT),
            format='A4',
            print_background=True,
        )
        await browser.close()


def count_pdf_pages():
    data = PDF_OUT.read_bytes()
    return len(re.findall(rb'/Type\s*/Page[^s]', data))


def main():
    print(f"Source  : {NOTEBOOK}")
    print(f"Output  : {PDF_OUT}")
    print()

    execute_to_html()
    inject_css()
    asyncio.run(html_to_pdf())

    if PDF_OUT.exists():
        size_kb = PDF_OUT.stat().st_size // 1024
        pages   = count_pdf_pages()
        print(f"\nDone. PDF written ({size_kb} KB, {pages} pages): {PDF_OUT}")
        HTML_OUT.unlink(missing_ok=True)
    else:
        sys.exit("PDF not found after conversion.")


if __name__ == '__main__':
    main()
