#!/usr/bin/env python3
"""Convert filled questionnaire HTML files to PDF via Chrome headless."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "output"
PDF_DIR = ROOT / "output" / "pdf"

CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium",
]


def find_chrome() -> str:
    for p in CHROME_PATHS:
        if Path(p).exists():
            return p
    return "google-chrome"


def html_to_pdf(html_path: Path, pdf_path: Path | None = None) -> Path:
    if pdf_path is None:
        PDF_DIR.mkdir(parents=True, exist_ok=True)
        pdf_path = PDF_DIR / html_path.with_suffix(".pdf").name

    chrome = find_chrome()
    abs_html = str(html_path.resolve())
    abs_pdf = str(pdf_path.resolve())

    subprocess.run(
        [
            chrome,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--print-to-pdf=" + abs_pdf,
            "--no-pdf-header-footer",
            "--print-backgrounds",
            abs_html,
        ],
        check=True,
        capture_output=True,
        timeout=60,
    )
    return pdf_path


def main() -> None:
    files = [Path(a) for a in sys.argv[1:]]
    if not files:
        files = sorted(OUT_DIR.glob("问卷_*.html"))
    if not files:
        print("未找到 HTML 问卷文件", file=sys.stderr)
        sys.exit(1)

    for html_path in files:
        if not html_path.exists():
            print(f"文件不存在: {html_path}", file=sys.stderr)
            continue
        if html_path.suffix.lower() != ".html":
            continue
        pdf = html_to_pdf(html_path)
        print(f"已转换: {html_path.name} → {pdf.name} ({pdf.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
