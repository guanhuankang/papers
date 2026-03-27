#!/usr/bin/env python3
"""
Regenerate index.html: list every file under papers/ (recursive) as cards + embed read_paper.md.

Usage (from repo root):
  python3 update_index.py
"""

from __future__ import annotations

import html
from pathlib import Path
from urllib.parse import quote


def repo_root() -> Path:
    return Path(__file__).resolve().parent


def href_for_papers_path(rel_under_papers: Path) -> str:
    """Build href like papers/foo/bar%20x.pdf using path segments (spaces OK)."""
    parts = ("papers",) + rel_under_papers.parts
    return "/".join(quote(p, safe="") for p in parts)


def collect_files(papers_dir: Path) -> list[Path]:
    if not papers_dir.is_dir():
        return []
    out: list[Path] = []
    for p in papers_dir.rglob("*"):
        if not p.is_file():
            continue
        if p.name.startswith("."):
            continue
        out.append(p.relative_to(papers_dir))
    # 按文件名排序，同名的再按完整相对路径
    return sorted(out, key=lambda p: (p.name.lower(), str(p).lower()))


def card_kind_for_path(rel: Path) -> str:
    ext = rel.suffix.lower()
    if ext == ".html" or ext == ".htm":
        return "html"
    if ext == ".pdf":
        return "pdf"
    return "other"


def badge_label(kind: str) -> str:
    return {"html": "HTML", "pdf": "PDF"}.get(kind, "文件")


def build_papers_html(papers_dir: Path) -> str:
    rel_files = collect_files(papers_dir)
    if not rel_files:
        return (
            '<div class="cards"><article class="card card-other"><p class="empty">'
            "<code>papers/</code> 下暂无文件，或目录不存在。</p></article></div>"
        )

    cards: list[str] = []
    for rel in rel_files:
        kind = card_kind_for_path(rel)
        href = href_for_papers_path(rel)
        name = rel.name
        if rel.parent == Path("."):
            folder_label = "papers/"
        else:
            folder_label = f"papers/{rel.parent.as_posix()}/"

        cards.append(
            f'        <article class="card card-{kind}">\n'
            f'          <span class="badge">{html.escape(badge_label(kind))}</span>\n'
            f'          <h3 class="card-title"><a href="{href}">{html.escape(name)}</a></h3>\n'
            f'          <p class="card-folder">{html.escape(folder_label)}</p>\n'
            "        </article>"
        )

    return "        <div class=\"cards\">\n" + "\n".join(cards) + "\n        </div>"


def load_read_paper(root: Path) -> str:
    path = root / "read_paper.md"
    if not path.is_file():
        return "# read_paper.md not found\n"
    return path.read_text(encoding="utf-8")


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Papers</title>
  <style>
    :root {{
      --orange: #e95420;
      --aubergine: #2c001e;
      --bg: #f7f7f8;
      --card: #fff;
      --border: #e5d9d4;
      --text: #1b1b1b;
      --muted: #6b7280;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.65;
      font-size: 17px;
    }}
    .container {{
      max-width: min(1200px, 100%);
      margin: 0 auto;
      padding: 32px clamp(16px, 4vw, 40px) 48px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 1.75rem;
      color: var(--aubergine);
    }}
    .sub {{
      margin: 0 0 28px;
      color: var(--muted);
      font-size: 0.95rem;
    }}
    .hint {{
      margin: -12px 0 28px;
      color: var(--muted);
      font-size: 0.85rem;
    }}
    h2 {{
      margin: 36px 0 16px;
      font-size: 1.2rem;
      color: var(--aubergine);
      border-bottom: 2px solid var(--orange);
      padding-bottom: 6px;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 14px;
    }}
    .card {{
      border-radius: 12px;
      padding: 14px 16px 16px;
      border: 1px solid var(--border);
      border-left-width: 4px;
      box-shadow: 0 4px 14px rgba(44, 0, 30, 0.07);
      transition: box-shadow 0.15s ease, transform 0.12s ease;
    }}
    .card:hover {{
      box-shadow: 0 8px 22px rgba(44, 0, 30, 0.11);
      transform: translateY(-1px);
    }}
    .card-html {{
      background: linear-gradient(145deg, #fff8f3 0%, #fff 55%);
      border-left-color: var(--orange);
    }}
    .card-pdf {{
      background: linear-gradient(145deg, #f4f0fa 0%, #fff 55%);
      border-left-color: #5c2d91;
    }}
    .card-other {{
      background: var(--card);
      border-left-color: #8b8b9a;
    }}
    .badge {{
      display: inline-block;
      font-size: 0.68rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      padding: 3px 8px;
      border-radius: 6px;
      margin-bottom: 8px;
    }}
    .card-html .badge {{
      background: rgba(233, 84, 32, 0.14);
      color: #b83f12;
    }}
    .card-pdf .badge {{
      background: rgba(92, 45, 145, 0.12);
      color: #4a2478;
    }}
    .card-other .badge {{
      background: rgba(139, 139, 154, 0.15);
      color: #55556a;
    }}
    .card-title {{
      margin: 0;
      font-size: 0.98rem;
      font-weight: 600;
      line-height: 1.35;
    }}
    .card-title a {{
      color: var(--aubergine);
      text-decoration: none;
      word-break: break-word;
    }}
    .card-html .card-title a {{ color: #7a2e0d; }}
    .card-pdf .card-title a {{ color: #3d1f66; }}
    .card-title a:hover {{ text-decoration: underline; }}
    .card-folder {{
      margin: 8px 0 0;
      font-size: 0.78rem;
      color: var(--muted);
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }}
    .empty {{ margin: 0; color: var(--muted); }}
    .md-wrap {{
      margin-top: 8px;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      overflow-x: auto;
    }}
    .md-wrap pre {{
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 13px;
      line-height: 1.55;
      color: var(--text);
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Papers</h1>
      <p class="sub"><code>papers/</code> 下全部文件（含子目录）；下方为 <code>read_paper.md</code> 原文。</p>
      <p class="hint">更新列表请运行：<code>python3 update_index.py</code></p>
    </header>

    <main>
      <section aria-labelledby="papers-h">
        <h2 id="papers-h">论文与资源</h2>
        {papers_section}
      </section>

      <section aria-labelledby="spec-h">
        <h2 id="spec-h">read_paper.md</h2>
        <div class="md-wrap">
          <pre>{read_paper_escaped}</pre>
        </div>
      </section>
    </main>
  </div>
</body>
</html>
"""


def main() -> None:
    root = repo_root()
    papers_dir = root / "papers"
    papers_html = build_papers_html(papers_dir)
    md = load_read_paper(root)
    # pre 内放原文：用 escape 防止 &lt; 等破坏 HTML
    md_escaped = html.escape(md)

    out = HTML_TEMPLATE.format(
        papers_section=papers_html,
        read_paper_escaped=md_escaped,
    )
    (root / "index.html").write_text(out, encoding="utf-8")
    n = len(collect_files(papers_dir))
    print(f"Wrote index.html ({n} files under papers/).")


if __name__ == "__main__":
    main()
