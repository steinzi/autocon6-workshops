#!/usr/bin/env python3
"""Render index.html from data/workshops.json. Usage: python3 build.py"""
import html
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
SLACK_TEAM = "T05GX70T5FY"
SLACK_IDS = {
    "ac6-ws-a1": "C0CH1Q3023S", "ac6-ws-a2": "C0CG77YDUFL",
    "ac6-ws-a3-into-the-unknown": "C0C3ZAGE613", "ac6-ws-a4": "C0C6A85JGAF",
    "ac6-ws-b1": "C0CG9KPSFLH", "ac6-ws-b2": "C0CG2ENQX45", "ac6-ws-b3": "C0CG5D5U19U",
    "ac6-ws-b4": "C0CG9LG5K17", "ac6-ws-c1": "C0CG75JV0E5", "ac6-ws-c2": "C0C47ECQS4R",
    "ac6-ws-c3": "C0CBNG5LAS2", "ac6-ws-c4": "C0CGBF2GGEQ",
    "ac6-ws-d1-ai-for-the-network-forward-engineer": "C0C3GRUCJ8M",
    "ac6-ws-d2": "C0C495T67KN", "ac6-ws-d3": "C0CG1HCCZQB", "ac6-ws-d4": "C0CFELQCWVB",
}
BLOCK_NAMES = {"A": "Monday morning", "B": "Monday afternoon", "C": "Tuesday morning", "D": "Tuesday afternoon"}

e = html.escape


def card(w, blocks):
    has_material = bool(w.get("links"))
    badges = []
    if has_material:
        badges.append('<span class="badge mat">Material</span>')
    if w.get("prep"):
        badges.append('<span class="badge prep">Prep info</span>')
    if not (w.get("links") or w.get("prep") or w.get("notes")):
        badges.append('<span class="badge none">Nothing posted yet</span>')
    badges.append('<span class="badge sold">Sold out</span>' if w.get("sold_out") else '<span class="badge open">Seats listed</span>')

    parts = [f'<article class="card" id="{e(w["code"].lower())}" data-block="{w["code"][0]}" data-material="{int(has_material)}">']
    parts.append(f'<header><span class="code">{e(w["code"])}</span><div class="badges">{"".join(badges)}</div></header>')
    parts.append(f'<h3>{e(w["title"])}</h3>')
    meta = [e(w["org"]), e(blocks[w["code"][0]])]
    if w.get("room"):
        meta.append(f'Room <strong>{e(w["room"])}</strong>')
    parts.append(f'<p class="meta">{" · ".join(meta)}</p>')
    parts.append(f'<p class="tldr"><span>TL;DR</span> {e(w["tldr"])}</p>')
    if w.get("links"):
        parts.append('<ul class="links">' + "".join(
            f'<li><a href="{e(l["url"])}" target="_blank" rel="noopener">{e(l["label"])} ↗</a></li>' for l in w["links"]) + "</ul>")
    if w.get("prep"):
        parts.append('<h4>Before you start</h4><ul>' + "".join(f"<li>{e(p)}</li>" for p in w["prep"]) + "</ul>")
    if w.get("agenda"):
        parts.append('<h4>Agenda</h4><table class="agenda">' + "".join(
            f"<tr><td>{e(t)}</td><td>{e(a)}</td></tr>" for t, a in w["agenda"]) + "</table>")
    if w.get("notes"):
        parts.append('<h4>Notes</h4><ul>' + "".join(f"<li>{e(n)}</li>" for n in w["notes"]) + "</ul>")
    foot = f'Proctors: {e(", ".join(w["proctors"]))} · {e(w["levels"])}'
    ch = w.get("slack")
    if ch:
        url = f"https://app.slack.com/client/{SLACK_TEAM}/{SLACK_IDS.get(ch, '')}"
        foot += f' · <a href="{e(url)}" target="_blank" rel="noopener">#{e(ch)}</a>'
    parts.append(f'<footer>{foot}</footer></article>')
    return "\n".join(parts)


def main():
    data = json.loads((ROOT / "data" / "workshops.json").read_text())
    ev = data["event"]
    blocks = ev["blocks"]
    updated = datetime.fromisoformat(data["updated"]).strftime("%a %d %b, %H:%M MST")
    ws = data["workshops"]
    n_mat = sum(1 for w in ws if w.get("links"))

    sections = []
    for b, name in BLOCK_NAMES.items():
        cards = "\n".join(card(w, blocks) for w in ws if w["code"].startswith(b))
        sections.append(f'<section class="block" data-block="{b}"><h2>{e(name)} <small>{e(blocks[b])}</small></h2><div class="grid">{cards}</div></section>')

    toc = "".join(
        f'<a href="#{w["code"].lower()}" class="{"has" if w.get("links") else ""}">{e(w["code"])}</a>' for w in ws)
    notes = "".join(f"<li>{e(n)}</li>" for n in ev.get("notes", []))

    page = TEMPLATE.format(
        updated=e(updated), city=e(ev["city"]), venue=e(ev["venue"]), days=e(ev["workshop_days"]),
        official=e(ev["official_url"]), notes=notes, toc=toc, sections="\n".join(sections),
        n=len(ws), n_mat=n_mat,
    )
    (ROOT / "index.html").write_text(page)
    print(f"wrote index.html ({len(ws)} workshops, {n_mat} with material)")


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AutoCon 6 Workshops</title>
<meta name="description" content="Unofficial cheat sheet for the AutoCon 6 workshops: TL;DRs, prep steps, rooms and material links.">
<style>
:root {{
  --bg:#f7f6f2; --fg:#1d1d1b; --muted:#6b6a65; --card:#fff; --line:#e4e2dc;
  --accent:#0f6e6e; --mat:#1f7a3a; --mat-bg:#e5f4e4; --prep:#8a5a00; --prep-bg:#f9eeda;
  --none:#8a8984; --none-bg:#f0efec; --sold:#9b2c2c; --sold-bg:#fbebeb; --open-bg:#e7f1fb; --open:#1d5b99;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg:#141413; --fg:#ecebe6; --muted:#a3a29c; --card:#1e1e1c; --line:#33322f;
  --accent:#5cc2c2; --mat:#8fd89f; --mat-bg:#1f3524; --prep:#f0c26b; --prep-bg:#3a2e17;
  --none:#a3a29c; --none-bg:#2a2a27; --sold:#f2a3a3; --sold-bg:#3d2020; --open-bg:#1c2c3d; --open:#9cc6f0;
}} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg); font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif; }}
a {{ color:var(--accent); }}
.wrap {{ max-width:1100px; margin:0 auto; padding:0 16px; }}
.hero {{ padding:32px 0 16px; }}
.hero h1 {{ margin:0 0 4px; font-size:clamp(1.8rem,5vw,2.6rem); letter-spacing:-.02em; }}
.hero p {{ margin:4px 0; color:var(--muted); }}
.stamp {{ display:inline-block; margin-top:8px; padding:4px 10px; border-radius:999px; background:var(--card); border:1px solid var(--line); font-size:.85rem; }}
.info {{ margin:12px 0 0; padding-left:18px; color:var(--muted); font-size:.92rem; }}
nav.toc {{ position:sticky; top:0; z-index:5; background:var(--bg); border-bottom:1px solid var(--line); padding:10px 0; }}
nav.toc .wrap {{ display:flex; flex-wrap:wrap; gap:6px; align-items:center; }}
nav.toc a {{ text-decoration:none; font:600 .85rem ui-monospace,monospace; padding:4px 8px; border-radius:6px; border:1px solid var(--line); color:var(--fg); background:var(--card); }}
nav.toc a.has {{ border-color:var(--mat); color:var(--mat); }}
nav.toc label {{ margin-left:auto; font-size:.85rem; color:var(--muted); display:flex; gap:6px; align-items:center; }}
section.block h2 {{ margin:32px 0 12px; font-size:1.3rem; }}
section.block h2 small {{ color:var(--muted); font-weight:500; font-size:.9rem; margin-left:6px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:14px; }}
@media (max-width:400px) {{ .grid {{ grid-template-columns:1fr; }} }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:16px; display:flex; flex-direction:column; scroll-margin-top:60px; }}
.card header {{ display:flex; justify-content:space-between; align-items:center; gap:8px; flex-wrap:wrap; }}
.code {{ font:700 .95rem ui-monospace,monospace; color:var(--accent); }}
.badges {{ display:flex; gap:4px; flex-wrap:wrap; }}
.badge {{ font-size:.72rem; font-weight:600; padding:2px 8px; border-radius:999px; }}
.mat {{ background:var(--mat-bg); color:var(--mat); }} .prep {{ background:var(--prep-bg); color:var(--prep); }}
.none {{ background:var(--none-bg); color:var(--none); }} .sold {{ background:var(--sold-bg); color:var(--sold); }}
.open {{ background:var(--open-bg); color:var(--open); }}
.card h3 {{ margin:8px 0 4px; font-size:1.05rem; line-height:1.35; }}
.meta {{ margin:0 0 10px; color:var(--muted); font-size:.88rem; }}
.tldr {{ margin:0 0 10px; }}
.tldr span {{ font:700 .72rem ui-monospace,monospace; background:var(--fg); color:var(--bg); padding:1px 6px; border-radius:4px; margin-right:4px; vertical-align:2px; }}
.card h4 {{ margin:10px 0 4px; font-size:.8rem; text-transform:uppercase; letter-spacing:.05em; color:var(--muted); }}
.card ul {{ margin:0; padding-left:18px; font-size:.92rem; }}
.card ul.links {{ list-style:none; padding:0; display:flex; flex-wrap:wrap; gap:6px; }}
.card ul.links a {{ display:inline-block; padding:5px 10px; border-radius:8px; background:var(--mat-bg); color:var(--mat); text-decoration:none; font-weight:600; font-size:.88rem; word-break:break-word; }}
.agenda {{ font-size:.88rem; border-collapse:collapse; }}
.agenda td {{ padding:1px 8px 1px 0; vertical-align:top; }}
.agenda td:first-child {{ font-family:ui-monospace,monospace; color:var(--muted); white-space:nowrap; }}
.card footer {{ margin-top:auto; padding-top:12px; font-size:.78rem; color:var(--muted); word-break:break-word; }}
body.only-mat .card[data-material="0"] {{ display:none; }}
.foot {{ margin:40px 0; color:var(--muted); font-size:.85rem; }}
</style>
</head>
<body>
<div class="wrap hero">
  <h1>AutoCon 6 Workshops</h1>
  <p>{days} · {venue}, {city}</p>
  <p>An unofficial cheat sheet: TL;DR, prep steps, rooms and links for all {n} workshops. {n_mat} have material posted so far.</p>
  <span class="stamp">Last updated {updated}</span>
  <ul class="info">{notes}</ul>
</div>
<nav class="toc"><div class="wrap">{toc}<label><input type="checkbox" id="onlymat"> Only with material</label></div></nav>
<main class="wrap">
{sections}
<p class="foot">Not official. Compiled from the <a href="{official}">AutoCon 6 website</a> and what presenters posted in the workshop Slack channels (the Slack links work for Network Automation Forum members). Check the official site and your workshop's channel for anything that changes.</p>
</main>
<script>
const cb=document.getElementById('onlymat');
try{{cb.checked=localStorage.getItem('onlymat')==='1';}}catch(e){{}}
const apply=()=>{{document.body.classList.toggle('only-mat',cb.checked);try{{localStorage.setItem('onlymat',cb.checked?'1':'0');}}catch(e){{}}}};
cb.addEventListener('change',apply);apply();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
