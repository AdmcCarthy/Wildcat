"""Write <site>/plates/index.html: a page that lists the print-grade files `plate render` made, grouped by figure.

Plate writes `<site>/plates/manifest.json` and one folder per figure (PDF at paper size, PNG at a stated dpi). This page links
every file, so the downloads stay discoverable from the story (SubScout 0.6 export pages no longer list them).

Usage: python scripts/build_plates_index.py [site_dir]
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def mb(n: int) -> str:
    return f"{n / 1e6:.1f} MB"


def rows(manifest: dict) -> dict[str, dict[str, list[dict]]]:
    """figure -> state -> files, in manifest order."""
    out: dict[str, dict[str, list[dict]]] = {}
    for f in manifest["files"]:
        out.setdefault(f["figure"], {}).setdefault(f["state"], []).append(f)
    return out


def label(f: dict) -> str:
    if f["format"] == "pdf":
        return f"PDF, {f['w_mm']:.0f} × {f['h_mm']:.0f} mm, vector"
    return f"PNG, {f['px'][0]} × {f['px'][1]} px, {f['dpi']} dpi"


def render(manifest: dict, title: str, source: str) -> str:
    body = []
    for fig, states in rows(manifest).items():
        body.append(f'<section><h2>{html.escape(fig.replace("_", " ").capitalize())}</h2>')
        for state, files in states.items():
            body.append(f"<h3>{html.escape(state)}</h3><ul>")
            for f in files:
                note = " (QA: check)" if f.get("qa") else ""
                body.append(
                    f'<li><a href="{html.escape(f["file"])}" download>{html.escape(f["size"])} · {html.escape(label(f))}</a>'
                    f' <span class="sz">{mb(f["bytes"])}{note}</span></li>'
                )
            body.append("</ul>")
        body.append("</section>")
    return f"""<!doctype html>
<html lang="en-GB" data-type="ledger" data-palette="tide" data-surface="nordic-cool">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · print files</title>
<link rel="stylesheet" href="../runtime/css/tokens.css"><link rel="stylesheet" href="../runtime/css/base.css">
<style>
 body {{ margin: 0; background: var(--ss-surface); color: var(--ss-text); font-family: var(--ss-font-body); }}
 main {{ max-width: 52rem; margin: 0 auto; padding: 2rem 1rem 4rem; }}
 h1 {{ font: 500 2rem/1.15 var(--ss-font-display); margin: 0 0 .5rem; }} h2 {{ margin-top: 2.2rem; }} h3 {{ font-size: 1rem; margin: 1.2rem 0 .3rem; color: var(--ss-text-muted); }}
 ul {{ margin: 0; padding-left: 1.1rem; }} li {{ margin: .2rem 0; }} .sz {{ color: var(--ss-text-muted); font-size: .85rem; }}
 a {{ color: var(--ss-link); }} .lead {{ color: var(--ss-text-muted); }}
</style>
</head>
<body><main>
<p><a href="../">← {html.escape(title)}</a></p>
<h1>Print files</h1>
<p class="lead">Each figure as a vector PDF at paper size (A3 and A1, landscape) and as a PNG at a stated resolution, made with
<a href="https://github.com/AdmcCarthy/Plate">Plate</a> from the same chart code as the page. Source: {html.escape(source)}. Large
sheets: use the PDF; the PNG is a proof and is capped in size.</p>
{"".join(body)}
</main></body></html>
"""


def main(site: Path) -> None:
    manifest = json.loads((site / "plates" / "manifest.json").read_text())
    fm = yaml.safe_load((ROOT / "story.md").read_text(encoding="utf-8").split("---")[1])
    src = next(iter(fm["sources"].values()))["name"]
    (site / "plates" / "index.html").write_text(render(manifest, fm["title"], src), encoding="utf-8")
    print(f"wrote {site / 'plates' / 'index.html'} ({len(manifest['files'])} files)")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "_site")
