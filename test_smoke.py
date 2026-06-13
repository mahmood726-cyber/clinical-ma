"""Minimal smoke tests for clinical-ma static HTML bundle."""
import re
import os

ROOT = os.path.dirname(__file__)


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def test_index_html_present_and_valid():
    html = read("index.html")
    assert "SGLT2 Inhibitors and Heart Failure" in html
    open_divs = len(re.findall(r"<div[\s>]", html))
    close_divs = len(re.findall(r"</div>", html))
    assert open_divs == close_divs, f"Unbalanced divs: {open_divs} open vs {close_divs} close"
    assert "REPLACE_ME" not in html and "__PLACEHOLDER__" not in html  # sentinel:skip-line
    # No BOM
    raw = open(os.path.join(ROOT, "index.html"), "rb").read(3)
    assert raw[:3] != b"\xef\xbb\xbf", "BOM detected in index.html"


def test_dashboard_html_valid():
    html = read("e156-submission/assets/dashboard.html")
    assert "HR 0.77" in html, "Primary result HR not found in dashboard"
    open_divs = len(re.findall(r"<div[\s>]", html))
    close_divs = len(re.findall(r"</div>", html))
    assert open_divs == close_divs, f"Unbalanced divs in dashboard: {open_divs} vs {close_divs}"
    assert "REPLACE_ME" not in html  # sentinel:skip-line
    assert "</script>" not in html.split("<script")[0]  # no </script> before first script tag


def test_paper_md_has_seven_sentences():
    md = read("e156-submission/paper.md")
    # The body paragraph starts after the header lines; count sentence-ending punctuation
    # Body is the paragraph containing the E156 text (no headings, starts with "Do SGLT2")
    body_match = re.search(
        r"Do SGLT2 inhibitors.*?cannot be excluded\.", md, re.DOTALL
    )
    assert body_match, "E156 body paragraph not found in paper.md"
    body = body_match.group(0)
    sentences = re.split(r"(?<=[.?!])\s+", body.strip())
    assert len(sentences) == 7, f"Expected 7 sentences, got {len(sentences)}"


def test_e156_submission_index_html_valid():
    html = read("e156-submission/index.html")
    assert "SGLT2" in html
    assert "71553" in html or "71,553" in html
    open_divs = len(re.findall(r"<div[\s>]", html))
    close_divs = len(re.findall(r"</div>", html))
    assert open_divs == close_divs, f"Unbalanced divs in e156 index: {open_divs} vs {close_divs}"


def test_no_hardcoded_local_paths_in_html():
    files = [
        "index.html",
        "e156-submission/index.html",
        "e156-submission/assets/dashboard.html",
    ]
    pattern = re.compile(r"[Cc]:\\Users\\|/home/[a-zA-Z]")
    for rel in files:
        content = read(rel)
        hits = pattern.findall(content)
        assert not hits, f"Hardcoded local path found in {rel}: {hits}"
