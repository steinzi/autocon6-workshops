#!/usr/bin/env python3
"""Render index.html from data/workshops.json.

    python3 build.py
"""
import html
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
REPO_URL = "https://github.com/steinzi/autocon6-workshops"
SITE_URL = "https://steinzi.com/autocon6-workshops/"
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
BLOCKS = [
    # code, short tab label, long label, start, end (local MST)
    ("A", "Mon AM", "Monday morning", "2026-11-16T09:00:00-07:00", "2026-11-16T13:00:00-07:00"),
    ("B", "Mon PM", "Monday afternoon", "2026-11-16T14:00:00-07:00", "2026-11-16T18:00:00-07:00"),
    ("C", "Tue AM", "Tuesday morning", "2026-11-17T09:00:00-07:00", "2026-11-17T13:00:00-07:00"),
    ("D", "Tue PM", "Tuesday afternoon", "2026-11-17T14:00:00-07:00", "2026-11-17T18:00:00-07:00"),
]

e = html.escape

ICONS = {
    "presentation": '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>',
    "observability": '<circle cx="11" cy="11" r="6"/><path d="m20 20-4.5-4.5"/>',
    "orchestration": '<rect x="4" y="4" width="6.5" height="6.5" rx="1.5"/><rect x="13.5" y="4" width="6.5" height="6.5" rx="1.5"/><rect x="4" y="13.5" width="6.5" height="6.5" rx="1.5"/><rect x="13.5" y="13.5" width="6.5" height="6.5" rx="1.5"/>',
    "intent": '<path d="M12 3 21 12 12 21 3 12Z"/><path d="M3 12h18M12 3v18"/>',
    "collector": '<path d="m6 10 6-5 6 5M6 15l6-5 6 5M6 20l6-5 6 5"/>',
    "executor": '<path d="m6 4 6 5 6-5M6 9l6 5 6-5M6 14l6 5 6-5"/>',
    "infrastructure": '<circle cx="5" cy="6" r="2"/><circle cx="19" cy="6" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="5" cy="18" r="2"/><circle cx="19" cy="18" r="2"/><path d="M6.6 7.2 10.4 10.8M17.4 7.2 13.6 10.8M6.6 16.8l3.8-3.6M17.4 16.8l-3.8-3.6M7 6h10M7 18h10"/>',
    "practices": '<circle cx="6" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="8" r="2"/><path d="M6 7v10M18 10c0 4-6 3-11 7"/>',
}
SHORT = {"practices": "Practices"}
NAF_NAMES = {}


def icon(bid, cls="ic"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[bid]}</svg>'


def glyph(w):
    cells = []
    for bid in ["presentation", "observability", "orchestration", "intent", "collector", "executor", "infrastructure"]:
        st = "core" if bid in w.get("naf_core", []) else "touch" if bid in w.get("naf_touch", []) else ""
        cells.append(f'<i class="g-{bid} {st}"></i>')
    return '<span class="glyph" aria-hidden="true">' + "".join(cells) + "</span>"


def naf_explorer(data, ws, slot_short):
    naf = data["naf"]
    blocks = naf["blocks"]
    core = {b["id"]: [w for w in ws if b["id"] in w.get("naf_core", [])] for b in blocks}
    touch = {b["id"]: [w for w in ws if b["id"] in w.get("naf_touch", [])] for b in blocks}
    area = {"presentation": "pres", "observability": "obs", "orchestration": "orch", "intent": "int",
            "collector": "col", "executor": "exe", "infrastructure": "infra", "practices": "prac"}

    btns = []
    for b in blocks:
        n_c, n_t = len(core[b["id"]]), len(touch[b["id"]])
        wide = b["id"] in ("presentation", "infrastructure", "practices")
        subs = " · ".join(b["subs"])
        extra = '<em>not a framework block</em>' if b["id"] == "practices" else ""
        btns.append(
            f'<button type="button" class="nb nb-{area[b["id"]]}{" nb-wide" if wide else ""}" data-naf="{b["id"]}" aria-pressed="false" '
            f'style="--c:{b["color"]};--on:{b["on"]}" title="{n_c} core, {n_t} touch it">'
            f'{icon(b["id"])}<span class="nb-tx"><b>{e(b["name"])}</b>{extra}<small>{e(subs)}</small></span>'
            f'<span class="nb-n">{n_c + n_t}</span></button>')
    btns.append('<div class="naf-conn" aria-hidden="true"></div>')

    def row(w, bid):
        code = w["code"]
        mat = '<i class="mk mk-mat" title="Material posted"></i>' if w.get("links") else ""
        return (f'<a class="nr" href="#{code.lower()}" data-ws="{code.lower()}" data-core="{" ".join(w.get("naf_core", []))}" '
                f'data-touch="{" ".join(w.get("naf_touch", []))}">'
                f'<span class="ws-code b-{code[0]}">{e(code)}</span>'
                f'<span class="nr-main"><b>{e(w["title"])}</b><small>{e(w.get("naf_note", ""))}</small></span>'
                f'<span class="nr-side">{e(slot_short[code[0]])}{mat}</span></a>')

    panels = []
    # idle panel: coverage bars
    total = len(ws)
    bars = []
    for b in blocks:
        n_c, n_t = len(core[b["id"]]), len(touch[b["id"]])
        bars.append(
            f'<button type="button" class="cov" data-naf="{b["id"]}" style="--c:{b["color"]}">'
            f'<span class="cov-n">{icon(b["id"], "ic-s")}{e(SHORT.get(b["id"], b["name"]))}</span>'
            f'<span class="cov-bar"><i style="width:{n_c / total * 100:.1f}%"></i><i class="t" style="width:{n_t / total * 100:.1f}%"></i></span>'
            f'<span class="cov-v"><b>{n_c}</b>{f" +{n_t}" if n_t else ""}</span></button>')
    full = [w["code"] for w in ws if len(set(w.get("naf_core", [])) & {"intent", "collector", "observability", "orchestration", "executor", "presentation"}) == 6]
    panels.append(
        '<div class="np np-idle" data-panel="">'
        '<h3>How the workshops spread across the framework</h3>'
        f'<div class="covs">{"".join(bars)}</div>'
        '<p class="np-foot"><span class="key key-c"></span>core focus <span class="key key-t"></span>touches it. '
        + (f'Only <a href="#{full[0].lower()}" class="nr-jump" data-ws="{full[0].lower()}">{full[0]}</a> runs the full loop through all six blocks. ' if len(full) == 1 else "")
        + 'Tap any block to filter.</p></div>')
    for b in blocks:
        bid = b["id"]
        c_rows = "".join(row(w, bid) for w in core[bid])
        t_rows = "".join(row(w, bid) for w in touch[bid])
        tier = "Cross-cutting" if bid == "practices" else f'{b["tier"]} layer'
        panels.append(
            f'<div class="np" data-panel="{bid}" hidden style="--c:{b["color"]};--on:{b["on"]}">'
            f'<div class="np-top"><span class="np-ic">{icon(bid)}</span><div><span class="np-tier">{e(tier)}</span><h3>{e(b["name"])}</h3></div>'
            f'<button type="button" class="np-x" data-naf-clear>Clear</button></div>'
            f'<p class="np-desc">{e(b["desc"])}</p>'
            f'<div class="np-subs">{"".join(f"<span>{e(x)}</span>" for x in b["subs"])}</div>'
            + (f'<h4>Core focus <span>{len(core[bid])}</span></h4><div class="nl">{c_rows}</div>' if c_rows else "")
            + (f'<h4>Also touches it <span>{len(touch[bid])}</span></h4><div class="nl">{t_rows}</div>' if t_rows else "")
            + '<div class="np-act"><button type="button" class="np-go" data-go>Jump to the cards ↓</button><button type="button" class="np-all" data-showrel hidden></button></div></div>')

    return (
        '<section class="naf" id="framework" aria-labelledby="naf-h"><div class="in">'
        '<div class="naf-head"><span class="kick">Explore</span><h2 id="naf-h">Workshops by NAF Framework block</h2>'
        f'<p>The NAF <a href="{e(naf["url"])}" target="_blank" rel="noopener">Network Automation Framework</a> splits automation into building blocks. '
        'Tap one to see which workshops dig into it.</p></div>'
        f'<div class="naf-wrap"><div class="naf-dia" id="nafDia" role="group" aria-label="NAF Framework building blocks">{"".join(btns)}</div>'
        f'<div class="naf-panel" id="nafPanel" aria-live="polite">{"".join(panels)}</div></div>'
        '</div></section>')



def ul(items):
    return "<ul>" + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>"


def card(w, blocks, topic_labels):
    b = w["code"][0]
    has_links = bool(w.get("links"))
    empty = not (w.get("links") or w.get("prep") or w.get("notes"))
    search = " ".join([w["code"], w["title"], w["org"], w["tldr"], " ".join(w["proctors"]),
                       " ".join(topic_labels[t] for t in w.get("topics", [])),
                       " ".join(NAF_NAMES.get(x, x) for x in w.get("naf_core", []))]).lower()

    flags = []
    op = w.get("openness", "product")
    op_label = {"open": "Open source", "mostly": "Mostly open", "product": "Vendor product"}[op]
    flags.append(f'<span class="flag flag-{op}" title="{e(w.get("openness_note", ""))}">{op_label}</span>')
    if has_links:
        flags.append('<span class="flag flag-mat">Material</span>')
    elif w.get("prep"):
        flags.append('<span class="flag flag-prep">Setup info</span>')
    if empty:
        flags.append('<span class="flag flag-none">Nothing posted yet</span>')
    if w.get("sold_out"):
        flags.append('<span class="flag flag-sold">Sold out</span>')

    when = blocks[b]
    room = f'<span class="room">Room {e(w["room"])}</span>' if w.get("room") else '<span class="room room-tbd">Room not posted</span>'

    out = [f'<article class="ws" id="{w["code"].lower()}" data-block="{b}" data-mat="{int(has_links)}" data-oss="{op}" data-core="{" ".join(w.get("naf_core", []))}" data-touch="{" ".join(w.get("naf_touch", []))}" '
           f'data-topics="{" ".join(w.get("topics", []))}" data-search="{e(search)}">']
    out.append(f'<div class="ws-top"><a class="ws-code b-{b}" href="#{w["code"].lower()}">{e(w["code"])}</a>'
               f'<span class="ws-org">{e(w["org"])}</span><span class="flags">{"".join(flags)}</span></div>')
    out.append(f'<h3>{e(w["title"])}</h3>')
    out.append(f'<p class="ws-when">{e(when)} {room}</p>')
    out.append(f'<p class="ws-sum">{e(w["tldr"])}</p>')
    if has_links:
        out.append('<div class="ws-links">' + "".join(
            f'<a href="{e(l["url"])}" target="_blank" rel="noopener">{e(l["label"])}<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M3.5 2.5h6v6M9.5 2.5l-7 7"/></svg></a>'
            for l in w["links"]) + "</div>")
    core_names = " · ".join(
        f'<button type="button" data-naf="{b}" aria-pressed="false" title="Filter by this NAF block">{e(NAF_NAMES.get(b, b))}</button>' for b in w.get("naf_core", []))
    touch_n = len(w.get("naf_touch", []))
    out.append(f'<div class="ws-naf">{glyph(w)}<span class="ws-naf-t"><span class="lbl">NAF</span>{core_names}'
               + (f'<span class="plus">+{touch_n}</span>' if touch_n else "") + '</span><span class="ws-rel"></span></div>')
    out.append('<div class="ws-tags">' + "".join(
        f'<button type="button" class="tag" data-topic="{t}">{e(topic_labels[t])}</button>' for t in w.get("topics", [])) + "</div>")

    details = []
    if w.get("prep"):
        details.append("<h4>Before you start</h4>" + ul(w["prep"]))
    if w.get("agenda"):
        details.append("<h4>Agenda</h4><table class='agenda'>" + "".join(
            f"<tr><td>{e(t)}</td><td>{e(a)}</td></tr>" for t, a in w["agenda"]) + "</table>")
    if w.get("notes"):
        details.append("<h4>Good to know</h4>" + ul(w["notes"]))
    details.append(f'<h4>People</h4><p>{e(", ".join(w["proctors"]))}</p>')
    details.append(f'<h4>Level</h4><p>{e(w["levels"])}</p>')
    if w.get("naf_note"):
        touches = ", ".join(NAF_NAMES.get(b, b) for b in w.get("naf_touch", []))
        details.append(f'<h4>NAF Framework</h4><p>{e(w["naf_note"])}' + (f' Also touches {e(touches)}.' if touches else "") + '</p>')
    if w.get("openness_note"):
        details.append(f'<h4>{op_label}</h4><p>{e(w["openness_note"])}</p>')
    ch = w.get("slack")
    if ch:
        url = f"https://app.slack.com/client/{SLACK_TEAM}/{SLACK_IDS.get(ch, '')}"
        details.append(f'<h4>Slack</h4><p><a href="{e(url)}" target="_blank" rel="noopener">#{e(ch)}</a></p>')
    label = "Setup, notes &amp; people" if (w.get("prep") or w.get("notes") or w.get("agenda")) else "People &amp; level"
    out.append(f'<details><summary>{label}</summary><div class="ws-more">{"".join(details)}</div></details>')
    out.append("</article>")
    return "\n".join(out)


def main():
    data = json.loads((ROOT / "data" / "workshops.json").read_text())
    ev = data["event"]
    ws = data["workshops"]
    topics = data["topics"]
    topic_labels = {t["id"]: t["label"] for t in topics}
    NAF_NAMES.update({b["id"]: SHORT.get(b["id"], b["name"]) for b in data["naf"]["blocks"]})
    blocks = {b[0]: f"{b[2].split()[0][:3]} {b[3][8:10]} Nov · {b[3][11:16]}–{b[4][11:16]}" for b in BLOCKS}
    updated_dt = datetime.fromisoformat(data["updated"])
    updated = updated_dt.strftime("%a %d %b, %H:%M").replace(" 0", " ")
    counts = {t["id"]: sum(1 for w in ws if t["id"] in w.get("topics", [])) for t in topics}
    n_mat = sum(1 for w in ws if w.get("links"))

    tabs = ['<button type="button" class="tab" data-block="" aria-pressed="true">All<span class="tn"></span></button>']
    for code, short, _, start, end in BLOCKS:
        tabs.append(f'<button type="button" class="tab" data-block="{code}" data-start="{start}" data-end="{end}" aria-pressed="false">'
                    f'<i class="dot b-{code}"></i>{e(short)}<span class="tn"></span><span class="live">Live</span></button>')

    chips = "".join(
        f'<button type="button" class="chip" data-topic="{t["id"]}" aria-pressed="false">{e(t["label"])}<span>{counts[t["id"]]}</span></button>'
        for t in topics if counts[t["id"]])

    sections = []
    for code, _, long, start, end in BLOCKS:
        cards = "\n".join(card(w, blocks, topic_labels) for w in ws if w["code"].startswith(code))
        sections.append(
            f'<section class="blk" data-block="{code}" data-start="{start}" data-end="{end}">'
            f'<h2><i class="dot b-{code}"></i>{e(long)} <span>{e(blocks[code].split(" · ")[1])}</span><em class="live">Happening now</em></h2>'
            f'<div class="grid">{cards}</div></section>')

    page = (TEMPLATE
            .replace("{{UPDATED}}", e(updated))
            .replace("{{UPDATED_ISO}}", e(data["updated"]))
            .replace("{{VENUE}}", e(ev["venue"]))
            .replace("{{CITY}}", e(ev["city"]))
            .replace("{{OFFICIAL}}", e(ev["official_url"]))
            .replace("{{REPO}}", REPO_URL)
            .replace("{{SITE}}", SITE_URL)
            .replace("{{TABS}}", "".join(tabs))
            .replace("{{CHIPS}}", chips)
            .replace("{{SECTIONS}}", "\n".join(sections))
            .replace("{{NAF}}", naf_explorer(data, ws, {b[0]: b[1] for b in BLOCKS}))
            .replace("{{N}}", str(len(ws)))
            .replace("{{NMAT}}", str(n_mat))
            .replace("{{NOTES}}", "".join(f"<li>{e(n)}</li>" for n in ev.get("notes", []))))
    (ROOT / "index.html").write_text(page)
    print(f"wrote index.html ({len(ws)} workshops, {n_mat} with material)")


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>AutoCon 6 Workshop Guide (unofficial)</title>
<meta name="description" content="What each AutoCon 6 workshop covers, what to set up beforehand, and where the material lives.">
<meta name="theme-color" content="#1b1430">
<link rel="icon" type="image/png" href="img/favicon.png">
<link rel="apple-touch-icon" href="img/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:title" content="AutoCon 6 Workshop Guide (unofficial)">
<meta property="og:description" content="TL;DRs, setup steps, rooms and material for all 16 AutoCon 6 workshops.">
<meta property="og:url" content="{{SITE}}">
<meta property="og:image" content="{{SITE}}img/og.jpg">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{{SITE}}img/og.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#eef0f4; --panel:#ffffff; --ink:#12141a; --sub:#566070; --hair:#d9dde5; --soft:#f5f6f9;
  --sun:#ee5a24; --rose:#d6336c; --sky:#1c7ed6; --dusk:#7048e8; --cactus:#2f9e44; --sand:#e8a317;
  --a:var(--sun); --b:var(--rose); --c:var(--sky); --d:var(--dusk);
  --mat-bg:#e3f6e7; --mat-ink:#1f7a33; --prep-bg:#fff2d6; --prep-ink:#8f5b00; --none-bg:#eceef2; --none-ink:#6b7280;
  --sold-bg:#fde7ec; --sold-ink:#b02a4f; --focus:#1c7ed6;
  --oss-bg:#dff3f5; --oss-ink:#0b7285; --oss-line:#8fd3dc; --prod-bg:#f0ecfb; --prod-ink:#5f3dc4;
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  --sans:"Schibsted Grotesk",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
}
@media (prefers-color-scheme:dark){:root{
  --bg:#0d0f14; --panel:#161a22; --ink:#eceff4; --sub:#9aa3b2; --hair:#272d38; --soft:#1c212b;
  --mat-bg:#173322; --mat-ink:#7fdc95; --prep-bg:#3a2c10; --prep-ink:#f5c76a; --none-bg:#22262f; --none-ink:#9aa3b2;
  --sold-bg:#3a1824; --sold-ink:#f49ab3; --focus:#74b9ff;
  --oss-bg:#10323a; --oss-ink:#66d9e8; --oss-line:#1f5c66; --prod-bg:#271f42; --prod-ink:#b8a6f5;
}}
*{box-sizing:border-box}
html{scroll-padding-top:120px;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 var(--sans)}
a{color:inherit}
button{font:inherit;color:inherit;cursor:pointer}
:focus-visible{outline:2px solid var(--focus);outline-offset:2px}
.in{max-width:1180px;margin:0 auto;padding:0 16px}

/* masthead */
.mast{position:relative;color:#fff;overflow:hidden;
  background:linear-gradient(180deg,#1b1430 0%,#3d1d4f 45%,#9c2f52 78%,#ee5a24 100%)}
.mast:after{content:"";position:absolute;left:0;right:0;bottom:0;height:70px;
  background:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 70' preserveAspectRatio='none'><path d='M0 70 L0 52 L90 40 L170 50 L260 28 L330 42 L420 22 L500 38 L600 18 L690 36 L760 26 L860 44 L950 30 L1040 46 L1120 34 L1200 44 L1200 70Z' fill='%23140f22' opacity='.55'/><path d='M0 70 L0 60 L120 54 L230 62 L340 50 L470 60 L590 48 L720 58 L840 52 L980 62 L1100 54 L1200 58 L1200 70Z' fill='%23140f22'/></svg>") bottom/100% 100% no-repeat}
.mast .in{position:relative;z-index:1;padding-top:40px;padding-bottom:84px}
.mast-in{display:grid;grid-template-columns:minmax(0,1fr) minmax(240px,400px);gap:8px 28px;align-items:end}
.mast-art{position:relative;margin-bottom:-84px;align-self:end}
.mast-art img{display:block;width:100%;height:auto;filter:drop-shadow(0 18px 28px rgba(10,5,25,.45))}
.stamp{position:absolute;top:14%;left:-6%;transform:rotate(-12deg);font:700 15px/1 var(--mono);letter-spacing:.18em;text-transform:uppercase;
  color:#ffe066;border:3px solid #ffe066;border-radius:6px;padding:7px 10px 6px;background:rgba(27,20,48,.55);box-shadow:0 0 0 2px rgba(27,20,48,.35);
  -webkit-backdrop-filter:blur(2px);backdrop-filter:blur(2px)}
.unof{display:inline-block;margin-right:10px;padding:3px 6px;border:1px solid rgba(255,224,102,.7);border-radius:4px;color:#ffe066;opacity:1}
.gta{margin-top:20px;display:inline-flex;flex-direction:column;gap:8px;padding:12px 14px;border-radius:14px;
  background:linear-gradient(135deg,rgba(255,42,122,.22),rgba(0,212,255,.14));border:1px solid rgba(255,120,180,.45);box-shadow:0 0 30px -8px rgba(255,42,122,.55)}
.gta-head{display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-size:13.5px;opacity:.95}
.gta-tag{font:800 13px/1 var(--sans);letter-spacing:.02em;padding:4px 7px;border-radius:5px;color:#1b1430;background:linear-gradient(90deg,#ff7eb6,#ffd8a8)}
.gta-clock{display:flex;gap:8px}
.gta-clock span{display:flex;flex-direction:column;align-items:center;min-width:58px;padding:7px 6px 6px;border-radius:9px;background:rgba(10,5,25,.45);border:1px solid rgba(255,255,255,.12)}
.gta-clock b{font:600 26px/1 var(--mono);letter-spacing:-.02em;color:#fff;text-shadow:0 0 12px rgba(255,126,182,.7)}
.gta-clock i{font:500 10px/1 var(--mono);font-style:normal;text-transform:uppercase;letter-spacing:.1em;opacity:.7;margin-top:5px}
.gta-done{font-weight:600;font-size:15px}
.gta-done[hidden],.gta-clock[hidden]{display:none}
@media (max-width:760px){
  .mast-in{grid-template-columns:1fr}
  .mast-art{width:min(300px,78vw);justify-self:center;margin-top:8px;margin-bottom:-72px}
  .stamp{font-size:12px;left:-4%;top:10%}
  .gta{display:flex}
  .gta-clock span{min-width:0;flex:1}
  .gta-clock b{font-size:22px}
}
.kicker{font:600 12px/1 var(--mono);letter-spacing:.14em;text-transform:uppercase;opacity:.8}
.mast h1{margin:10px 0 8px;font-size:clamp(34px,7vw,64px);line-height:.98;font-weight:800;letter-spacing:-.035em}
.mast h1 b{display:block;font-weight:800;color:#ffd8a8}
.mast p{margin:0;max-width:640px;font-size:17px;opacity:.9}
.stats{display:flex;flex-wrap:wrap;gap:8px 18px;margin-top:18px;font-size:14px}
.stats span{display:inline-flex;align-items:center;gap:6px;opacity:.92}
.stats strong{font-family:var(--mono)}
.pulse{width:8px;height:8px;border-radius:50%;background:#8ce99a;box-shadow:0 0 0 0 rgba(140,233,154,.6);animation:p 2s infinite}
@keyframes p{70%{box-shadow:0 0 0 8px rgba(140,233,154,0)}100%{box-shadow:0 0 0 0 rgba(140,233,154,0)}}
@media (prefers-reduced-motion:reduce){.pulse{animation:none}}

/* control bar */
.bar{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--bg) 88%,transparent);
  backdrop-filter:saturate(1.4) blur(10px);-webkit-backdrop-filter:saturate(1.4) blur(10px);border-bottom:1px solid var(--hair)}
.bar .in{padding-top:10px;padding-bottom:10px}
.row{display:flex;gap:8px;align-items:center}
.tabs{display:flex;gap:4px;padding:3px;background:var(--panel);border:1px solid var(--hair);border-radius:12px;overflow-x:auto;scrollbar-width:none;flex:1 1 auto;min-width:0}
.tabs::-webkit-scrollbar{display:none}
.tab{flex:0 0 auto;display:inline-flex;align-items:center;gap:7px;border:0;background:none;padding:7px 12px;border-radius:9px;font-weight:600;font-size:14px;white-space:nowrap;color:var(--sub)}
.tab[aria-pressed="true"]{background:var(--ink);color:var(--panel)}
.tab .live{display:none;font:600 10px/1 var(--mono);text-transform:uppercase;letter-spacing:.06em;padding:3px 5px;border-radius:4px;background:var(--cactus);color:#fff}
.tab.is-live .live{display:inline-block}
.tab .tn{font:600 11px/1 var(--mono);opacity:.55}
.tab .tn:empty{display:none}
.tab.zero{opacity:.45}
.dot{display:inline-block;width:9px;height:9px;border-radius:3px;flex:0 0 auto}
.b-A{--k:var(--a)} .b-B{--k:var(--b)} .b-C{--k:var(--c)} .b-D{--k:var(--d)}
.dot{background:var(--k)}
.fbtn{flex:0 0 auto;display:inline-flex;align-items:center;gap:6px;border:1px solid var(--hair);background:var(--panel);padding:8px 12px;border-radius:10px;font-weight:600;font-size:14px}
.fbtn .n{display:none;min-width:18px;height:18px;padding:0 5px;border-radius:9px;background:var(--sun);color:#fff;font:600 11px/18px var(--mono);text-align:center}
.fbtn.on .n{display:inline-block}
.panel{display:none;padding-top:10px}
.panel.open{display:block}
.search{position:relative;flex:1 1 260px}
.search input{width:100%;border:1px solid var(--hair);background:var(--panel);color:var(--ink);border-radius:10px;padding:9px 12px 9px 36px;font:inherit;font-size:15px}
.search svg{position:absolute;left:11px;top:50%;width:16px;height:16px;transform:translateY(-50%);stroke:var(--sub);fill:none;stroke-width:2}
.toggle{display:inline-flex;align-items:center;gap:8px;font-size:14px;font-weight:600;white-space:nowrap;user-select:none}
.toggle input{appearance:none;width:34px;height:20px;border-radius:10px;background:var(--hair);position:relative;margin:0;cursor:pointer;transition:background .15s}
.toggle input:before{content:"";position:absolute;top:2px;left:2px;width:16px;height:16px;border-radius:50%;background:#fff;transition:transform .15s;box-shadow:0 1px 2px rgba(0,0,0,.25)}
.toggle input:checked{background:var(--cactus)}
.toggle input:checked:before{transform:translateX(14px)}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.chip{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--hair);background:var(--panel);padding:6px 10px;border-radius:999px;font-size:13.5px;font-weight:500}
.chip span{font:600 11px/1 var(--mono);color:var(--sub)}
.chip[aria-pressed="true"]{background:var(--ink);border-color:var(--ink);color:var(--panel)}
.chip[aria-pressed="true"] span{color:inherit;opacity:.7}
.chip.zero{opacity:.45}
.status{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-top:10px;font-size:13px;color:var(--sub)}
.status button{border:0;background:none;padding:0;text-decoration:underline;text-underline-offset:2px;font-size:13px;color:var(--sub)}
.status button[hidden]{display:none}
#showall{color:var(--ink)!important;font-weight:600}
.status button,#count{white-space:nowrap}
.wide{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.sr{display:inline-flex;align-items:center;gap:12px}
.fbtn{padding:6px 11px;font-size:13.5px;color:var(--ink)}
@media (max-width:640px){
  .tabs{flex:1 1 100%}
  .tab{padding:7px 9px;font-size:13.5px;gap:6px}
  .tab .live,.tab.is-live .live,.tab .tn{display:none}
  .status .wk{display:none}
  .sr{gap:10px}
  .tab.is-live .dot{box-shadow:0 0 0 2px var(--panel),0 0 0 4px var(--cactus)}
  .chips{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;margin-right:-16px;padding-right:16px}
  .chips::-webkit-scrollbar{display:none}
  .chip{flex:0 0 auto}
  .mast .in{padding-top:28px;padding-bottom:72px}
}
@media (min-width:860px){.fbtn{display:none}.panel{display:block}}

/* jump strip */
.jump{display:flex;gap:4px;flex-wrap:wrap;margin:18px 0 0}
.jump a{font:600 12px/1 var(--mono);text-decoration:none;padding:6px 7px;border-radius:6px;background:var(--panel);border:1px solid var(--hair);color:var(--sub);position:relative}
.jump a.m{color:var(--ink);border-color:color-mix(in srgb,var(--k) 55%,var(--hair))}
.jump a.m:after{content:"";position:absolute;top:-3px;right:-3px;width:7px;height:7px;border-radius:50%;background:var(--cactus);border:2px solid var(--bg)}
.jump a.off{opacity:.35}
.jump a.off:hover,.jump a.off:focus-visible{opacity:.8}

/* sections */
.blk{margin-top:28px}
.blk[hidden]{display:none}
.blk h2{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:0 0 12px;font-size:21px;font-weight:700;letter-spacing:-.015em}
.blk h2 .dot{width:12px;height:12px;border-radius:4px}
.blk h2 span{font:500 13px/1 var(--mono);color:var(--sub)}
.blk h2 .live{display:none;font:600 11px/1 var(--mono);font-style:normal;text-transform:uppercase;letter-spacing:.06em;padding:5px 7px;border-radius:5px;background:var(--cactus);color:#fff}
.blk.is-live h2 .live{display:inline-block}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:14px}
@media (max-width:420px){.grid{grid-template-columns:1fr}}

/* workshop card */
.ws{position:relative;display:flex;flex-direction:column;background:var(--panel);border:1px solid var(--hair);border-radius:14px;padding:16px 16px 6px;overflow:hidden}
.ws:before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--k)}
.ws[hidden]{display:none}
.ws:target{box-shadow:0 0 0 2px var(--k)}
.ws{--k:var(--a)} .ws[data-block="B"]{--k:var(--b)} .ws[data-block="C"]{--k:var(--c)} .ws[data-block="D"]{--k:var(--d)}
.ws-top{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.ws-code{font:600 13px/1 var(--mono);text-decoration:none;color:#fff;background:var(--k);padding:5px 7px;border-radius:6px}
.ws-org{font-size:13.5px;font-weight:600;color:var(--sub)}
.flags{display:flex;gap:4px;flex-wrap:wrap;margin-left:auto}
.flag{font-size:11.5px;font-weight:600;padding:3px 8px;border-radius:999px;white-space:nowrap}
.flag-mat{background:var(--mat-bg);color:var(--mat-ink)} .flag-prep{background:var(--prep-bg);color:var(--prep-ink)}
.flag-none{background:var(--none-bg);color:var(--none-ink)} .flag-sold{background:var(--sold-bg);color:var(--sold-ink)}
.flag-open{background:var(--oss-bg);color:var(--oss-ink)} .flag-mostly{background:transparent;color:var(--oss-ink);box-shadow:inset 0 0 0 1px var(--oss-line)}
.flag-product{background:var(--prod-bg);color:var(--prod-ink)}
.flags .flag-open,.flags .flag-mostly,.flags .flag-product{order:-1}
.ws h3{margin:10px 0 4px;font-size:17px;line-height:1.3;font-weight:700;letter-spacing:-.01em}
.ws-when{margin:0 0 10px;font:500 12.5px/1.5 var(--mono);color:var(--sub)}
.room{margin-left:6px;padding-left:8px;border-left:1px solid var(--hair);color:var(--ink)}
.room-tbd{color:var(--sub);opacity:.75}
.ws-sum{margin:0 0 12px;font-size:15px}
.ws-links{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 12px}
.ws-links a{display:inline-flex;align-items:center;gap:6px;padding:7px 11px;border-radius:9px;background:var(--mat-bg);color:var(--mat-ink);font-weight:600;font-size:14px;text-decoration:none;word-break:break-word}
.ws-links a:hover{filter:brightness(.96)}
.ws-links svg{width:11px;height:11px;stroke:currentColor;stroke-width:1.8;fill:none;flex:0 0 auto}
.ws-tags{display:flex;flex-wrap:wrap;gap:4px;margin:0 0 8px}
.tag{border:0;background:var(--soft);color:var(--sub);font-size:12px;font-weight:500;padding:3px 8px;border-radius:6px}
.tag:hover,.tag.hit{background:var(--ink);color:var(--panel)}
details{margin-top:auto;border-top:1px dashed var(--hair)}
summary{list-style:none;padding:10px 0;font-size:13.5px;font-weight:600;color:var(--sub);display:flex;align-items:center;gap:6px;cursor:pointer}
summary::-webkit-details-marker{display:none}
summary:before{content:"";width:7px;height:7px;border-right:2px solid currentColor;border-bottom:2px solid currentColor;transform:rotate(-45deg);transition:transform .15s;margin-right:2px}
details[open] summary:before{transform:rotate(45deg)}
.ws-more{padding:0 0 12px;font-size:14px}
.ws-more h4{margin:12px 0 4px;font:600 11px/1 var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--sub)}
.ws-more h4:first-child{margin-top:0}
.ws-more ul{margin:0;padding-left:18px}
.ws-more p{margin:0}
.ws-more a{color:var(--sky)}
.agenda{border-collapse:collapse;font-size:13.5px}
.agenda td{padding:2px 10px 2px 0;vertical-align:top}
.agenda td:first-child{font-family:var(--mono);color:var(--sub);white-space:nowrap}

.empty{display:none;margin:40px 0;padding:28px;border:1px dashed var(--hair);border-radius:14px;text-align:center;color:var(--sub)}
.empty.show{display:block}
.empty p{margin:0}
.relax{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin-top:14px}
.relax button{border:1px solid var(--hair);background:var(--panel);color:var(--ink);font-size:13.5px;font-weight:600;padding:7px 12px;border-radius:999px}
.relax button:hover{border-color:var(--ink)}
.relax button[data-reset]{background:none;color:var(--sub);font-weight:500}
.note{position:fixed;z-index:30;left:50%;bottom:max(16px,env(safe-area-inset-bottom));transform:translateX(-50%);width:max-content;max-width:calc(100% - 32px);display:flex;align-items:center;gap:12px;padding:9px 14px;border-radius:10px;background:var(--ink);color:var(--panel);font-size:13.5px;line-height:1.4;box-shadow:0 6px 20px rgba(0,0,0,.18)}
.note[hidden]{display:none}
.note button{flex:0 0 auto;border:0;background:none;padding:0;color:inherit;font:inherit;font-weight:700;text-decoration:underline;text-underline-offset:2px}
.info{margin:28px 0 0;padding:14px 16px 14px 34px;background:var(--panel);border:1px solid var(--hair);border-radius:12px;font-size:14px;color:var(--sub)}
.info li+li{margin-top:4px}
/* NAF explorer */
.naf{padding:30px 0 6px}
.naf-head{max-width:760px}
.kick{font:600 11px/1 var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--sub)}
.naf-head h2{margin:8px 0 6px;font-size:clamp(23px,3.6vw,32px);font-weight:800;letter-spacing:-.025em;line-height:1.1}
.naf-head p{margin:0;color:var(--sub);font-size:15px}
.naf-head a{color:var(--ink)}
.naf-wrap{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr);gap:18px;margin-top:18px;align-items:start}
@media (min-width:921px){.naf-wrap .naf-dia{position:sticky;top:16px}}
@media (max-width:920px){.naf-wrap{grid-template-columns:1fr}}
.np-act{display:flex;gap:8px;margin-top:14px;flex-wrap:wrap}
.np-all{flex:0 0 auto;border:1px solid var(--hair);background:var(--panel);color:var(--ink);border-radius:10px;padding:10px 12px;font-size:14px;font-weight:600}
.np-all[hidden]{display:none}
.np-go{display:block;flex:1 1 200px;border:1px solid var(--c);background:color-mix(in srgb,var(--c) 12%,var(--panel));color:var(--ink);border-radius:10px;padding:10px;font-size:14px;font-weight:600}
.np-go:hover{background:color-mix(in srgb,var(--c) 22%,var(--panel))}
.naf-dia{--rg:24px;--cg:12px;--wire:#b4bcc9;position:relative;isolation:isolate;display:grid;grid-template-columns:repeat(6,minmax(0,1fr));
  grid-template-areas:"pres pres pres pres pres pres" "obs obs orch orch int int" "col col conn conn exe exe" "infra infra infra infra infra infra" "prac prac prac prac prac prac";
  gap:var(--rg) var(--cg);padding:18px;background-color:var(--panel);border:1px solid var(--hair);border-radius:16px;
  background-image:radial-gradient(color-mix(in srgb,var(--hair) 80%,transparent) 1px,transparent 1.2px);background-size:14px 14px}
@media (prefers-color-scheme:dark){.naf-dia{--wire:#3d4553}}
.nb-pres{grid-area:pres}.nb-obs{grid-area:obs}.nb-orch{grid-area:orch}.nb-int{grid-area:int}.nb-col{grid-area:col}.nb-exe{grid-area:exe}.nb-infra{grid-area:infra}.nb-prac{grid-area:prac;margin-top:4px}
.naf-conn{grid-area:conn;position:relative}
.nb{--ic:color-mix(in srgb,var(--c) 70%,#000);position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;text-align:center;
  min-height:100px;padding:14px 8px 12px;border-radius:12px;border:1.5px solid color-mix(in srgb,var(--c) 60%,var(--hair));
  background:color-mix(in srgb,var(--c) 13%,var(--panel));color:var(--ink);transition:background-color .15s,color .15s,border-color .15s,box-shadow .15s}
@media (prefers-color-scheme:dark){.nb{--ic:var(--c);background:color-mix(in srgb,var(--c) 11%,var(--panel))}}
.nb:hover{border-color:var(--c);box-shadow:0 6px 18px -12px var(--c)}
.nb .ic{width:26px;height:26px;stroke:var(--ic);fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;flex:0 0 auto}
.nb-tx{display:flex;flex-direction:column;gap:2px;min-width:0}
.nb-tx b{font-size:15px;font-weight:700;letter-spacing:-.01em;line-height:1.2}
.nb-tx small{font-size:11.5px;color:var(--sub);line-height:1.35}
.nb-tx em{font:500 10px/1.2 var(--mono);font-style:normal;text-transform:uppercase;letter-spacing:.08em;color:var(--sub)}
.nb-n{position:absolute;top:7px;right:7px;min-width:22px;height:22px;padding:0 6px;border-radius:11px;background:var(--panel);border:1px solid color-mix(in srgb,var(--c) 50%,var(--hair));font:600 11.5px/20px var(--mono);color:var(--ink)}
.nb-wide{flex-direction:row;justify-content:flex-start;text-align:left;min-height:0;padding:13px 48px 13px 16px;gap:14px}
.nb-prac{border-style:dashed;background:var(--panel)}
.nb[aria-pressed="true"]{background:var(--c);color:var(--on);border-color:var(--c);box-shadow:0 10px 26px -12px var(--c)}
.nb[aria-pressed="true"] .ic{stroke:var(--on)}
.nb[aria-pressed="true"] small,.nb[aria-pressed="true"] em{color:var(--on);opacity:.85}
.nb[aria-pressed="true"] .nb-n{background:var(--on);color:var(--c);border-color:transparent}
.naf-dia.has-sel .nb:not([aria-pressed="true"]),.naf-dia.hovering .nb:not(.hl-core):not(.hl-touch){background:var(--panel);border-color:var(--hair);color:var(--sub);box-shadow:none}
.naf-dia.has-sel .nb:not([aria-pressed="true"]) .ic,.naf-dia.hovering .nb:not(.hl-core):not(.hl-touch) .ic{stroke:var(--sub)}
.naf-dia.hovering .nb.hl-core{background:var(--c);color:var(--on);border-color:var(--c)}
.naf-dia.hovering .nb.hl-core .ic{stroke:var(--on)} .naf-dia.hovering .nb.hl-core small,.naf-dia.hovering .nb.hl-core em{color:var(--on);opacity:.85}
.naf-dia.hovering .nb.hl-touch{background:color-mix(in srgb,var(--c) 24%,var(--panel));border-color:var(--c);color:var(--ink)}
.naf-dia.hovering .nb.hl-touch .ic{stroke:var(--ic)} .naf-dia.hovering .nb.hl-touch small{color:var(--sub);opacity:1}
.nb-obs::before,.nb-orch::before,.nb-int::before{content:"";position:absolute;left:50%;top:calc(-1*var(--rg) - 2px);height:var(--rg);border-left:2px solid var(--wire);z-index:-1}
.nb-obs::after,.nb-int::after,.nb-col::after,.nb-exe::after{content:"";position:absolute;left:50%;bottom:calc(-1*var(--rg) - 2px);height:var(--rg);border-left:2px solid var(--wire);z-index:-1}
.nb-orch::after{content:"";position:absolute;top:50%;left:calc(-1*var(--cg) - 2px);right:calc(-1*var(--cg) - 2px);border-top:2px solid var(--wire);z-index:-1}
.naf-conn::before{content:"";position:absolute;left:50%;top:calc(-1*var(--rg));bottom:50%;border-left:2px dashed var(--wire)}
.naf-conn::after{content:"";position:absolute;top:50%;left:calc(-1*var(--cg));right:calc(-1*var(--cg));border-top:2px dashed var(--wire)}
@media (max-width:560px){
  .naf-dia{--rg:18px;--cg:8px;padding:12px}
  .nb{min-height:86px;padding:12px 4px 10px;gap:4px}
  .nb .nb-tx small{display:none}
  .nb-tx b{font-size:12.5px}
  .nb .ic{width:22px;height:22px}
  .nb-wide{padding:11px 40px 11px 12px;gap:10px}
  .nb-wide .nb-tx small{display:block;font-size:11px}
  .nb-n{top:5px;right:5px;min-width:19px;height:19px;padding:0 4px;font-size:10.5px;line-height:17px}
}
.np{background:var(--panel);border:1px solid var(--hair);border-top:4px solid var(--c);border-radius:16px;padding:18px}
.np[hidden]{display:none}
.np-idle{--c:var(--ink)}
.np h3{margin:0;font-size:18px;font-weight:700;letter-spacing:-.01em;line-height:1.2}
.covs{display:grid;gap:2px;margin:12px 0 8px}
.cov{display:grid;grid-template-columns:minmax(118px,auto) 1fr 44px;align-items:center;gap:10px;border:0;background:none;padding:7px 6px;border-radius:8px;text-align:left}
.cov:hover{background:var(--soft)}
.cov-n{display:flex;align-items:center;gap:8px;font-size:13.5px;font-weight:600;white-space:nowrap}
.ic-s{width:16px;height:16px;stroke:color-mix(in srgb,var(--c) 70%,#000);fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;flex:0 0 auto}
@media (prefers-color-scheme:dark){.ic-s{stroke:var(--c)}}
.cov-bar{display:flex;height:10px;border-radius:5px;background:var(--soft);overflow:hidden}
.cov-bar i{display:block;height:100%;background:var(--c)}
.cov-bar i.t{background:color-mix(in srgb,var(--c) 38%,transparent)}
.cov-v{font:500 12px/1 var(--mono);color:var(--sub);text-align:right;white-space:nowrap}
.cov-v b{color:var(--ink);font-weight:600}
.np-foot{margin:6px 0 0;font-size:13px;color:var(--sub);line-height:1.6}
.key{display:inline-block;width:10px;height:10px;border-radius:3px;margin:0 4px 0 8px;vertical-align:-1px;background:var(--ink)}
.key-c{margin-left:0}
.key-t{background:color-mix(in srgb,var(--ink) 30%,transparent)}
.np-top{display:flex;align-items:center;gap:12px}
.np-ic{display:grid;place-items:center;width:44px;height:44px;border-radius:12px;background:var(--c);flex:0 0 auto}
.np-ic .ic{width:24px;height:24px;stroke:var(--on);fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.np-tier{font:600 10.5px/1 var(--mono);text-transform:uppercase;letter-spacing:.1em;color:var(--sub)}
.np-top h3{font-size:22px;margin-top:4px}
.np-x{margin-left:auto;border:1px solid var(--hair);background:var(--panel);border-radius:8px;padding:6px 11px;font-size:13px;font-weight:600;color:var(--sub)}
.np-x:hover{color:var(--ink);border-color:var(--sub)}
.np-desc{margin:12px 0 10px;font-size:14.5px}
.np-subs{display:flex;flex-wrap:wrap;gap:5px}
.np-subs span{font-size:12px;font-weight:600;padding:3px 9px;border-radius:999px;background:color-mix(in srgb,var(--c) 15%,var(--panel));border:1px solid color-mix(in srgb,var(--c) 40%,var(--hair))}
.np h4{display:flex;align-items:center;gap:8px;margin:18px 0 8px;font:600 11px/1 var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--sub)}
.np h4 span{padding:3px 6px;border-radius:5px;background:var(--soft);color:var(--ink)}
.nl{display:grid;gap:6px}
.nr{display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:10px;align-items:start;padding:10px;border-radius:10px;border:1px solid var(--hair);text-decoration:none;color:var(--ink);background:var(--panel);transition:border-color .12s,background-color .12s}
.nr:hover,.nr:focus-visible{border-color:var(--c);background:color-mix(in srgb,var(--c) 7%,var(--panel))}
.nr .ws-code{margin-top:1px}
.nr-main{min-width:0;display:flex;flex-direction:column;gap:3px}
.nr-main b{font-size:14px;line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.nr-main small{font-size:12.5px;color:var(--sub);line-height:1.4}
.nr-side{display:flex;align-items:center;gap:6px;font:500 11.5px/1.4 var(--mono);color:var(--sub);white-space:nowrap}
.nr.off{border-style:dashed;opacity:.6}
.nr.off .nr-side:after{content:"hidden";font-style:italic}
.mk-mat{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--cactus)}
.nr-jump{color:var(--ink);font-weight:700}
.ws-naf{display:flex;align-items:center;gap:8px;margin:0 0 10px;flex-wrap:wrap}
.glyph{display:grid;grid-template-columns:repeat(6,4px);grid-auto-rows:4px;grid-template-areas:"p p p p p p" "o o r r i i" "c c . . e e" "n n n n n n";gap:2px;padding:4px;border:1px solid var(--hair);border-radius:6px;background:var(--soft);flex:0 0 auto}
.glyph i{display:block;border-radius:1.5px;background:var(--hair)}
.g-presentation{grid-area:p;--c:#f5c518}.g-observability{grid-area:o;--c:#00e676}.g-orchestration{grid-area:r;--c:#00d4ff}.g-intent{grid-area:i;--c:#ff6d2e}
.g-collector{grid-area:c;--c:#f43f5e}.g-executor{grid-area:e;--c:#6366f1}.g-infrastructure{grid-area:n;--c:#64748b}
.glyph i.core{background:var(--c)}
.glyph i.touch{background:color-mix(in srgb,var(--c) 40%,var(--hair))}
.ws-naf-t{display:flex;align-items:center;flex-wrap:wrap;gap:2px 5px;font-size:12.5px;color:var(--sub)}
.ws-naf-t .lbl{font:600 10.5px/1 var(--mono);letter-spacing:.08em;margin-right:1px}
.ws-naf-t button{border:0;background:none;padding:0;font-size:12.5px;font-weight:600;color:var(--ink);text-decoration:underline;text-decoration-color:var(--hair);text-underline-offset:3px}
.ws-naf-t button:hover{text-decoration-color:currentColor}
.ws-naf-t button.hit{text-decoration:none;background:var(--ink);color:var(--panel);padding:1px 6px;border-radius:5px}
.ws-naf-t .plus{font:500 11px/1 var(--mono);color:var(--sub);margin-left:2px}
.ws-rel{margin-left:auto;font:600 10.5px/1 var(--mono);text-transform:uppercase;letter-spacing:.06em;padding:4px 7px;border-radius:5px;background:var(--ink);color:var(--panel)}
.ws-rel:empty{display:none}
.ws.rel-touch .ws-rel{background:transparent;color:var(--sub);box-shadow:inset 0 0 0 1px var(--hair)}
.ws.flash{animation:fl 1.8s ease-out}
@keyframes fl{0%,30%{box-shadow:0 0 0 3px var(--k)}100%{box-shadow:0 0 0 0 transparent}}
.status .nafchip{display:inline-flex;align-items:center;gap:5px;text-decoration:none;background:var(--ink);color:var(--panel);padding:4px 10px;border-radius:999px;font-size:12.5px;font-weight:600}
.status .nafchip[hidden]{display:none}
footer.site{margin:40px 0 0;padding:24px 0 48px;border-top:1px solid var(--hair);font-size:13.5px;color:var(--sub)}
footer.site a{color:var(--ink)}
</style>
</head>
<body>
<header class="mast">
  <div class="in mast-in">
    <div class="mast-txt">
      <div class="kicker"><span class="unof">Unofficial</span>Tucson · 16 &amp; 17 Nov</div>
      <h1>AutoCon 6<b>Workshop Guide</b></h1>
      <p>What each workshop covers, what to set up before you sit down, and where the slides, repos and labs are.</p>
      <div class="stats">
        <span><strong>{{N}}</strong> workshops</span>
        <span><strong>{{NMAT}}</strong> with material posted</span>
        <span><i class="pulse"></i>Updated <time datetime="{{UPDATED_ISO}}">{{UPDATED}}</time> MST</span>
      </div>
      <div class="gta" id="gta" role="timer" aria-live="off">
        <div class="gta-head"><span class="gta-tag">GTA VI</span><span>drops Thu 19 Nov. Attention span remaining:</span></div>
        <div class="gta-clock" id="gtaClock"><span><b data-u="d">-</b><i>days</i></span><span><b data-u="h">--</b><i>hrs</i></span><span><b data-u="m">--</b><i>min</i></span><span><b data-u="s">--</b><i>sec</i></span></div>
        <div class="gta-done" id="gtaDone" hidden>It's out. If you see me at the conference, no you didn't.</div>
      </div>
    </div>
    <div class="mast-art">
      <img src="img/logo.webp" width="840" height="863" alt="The guide's mascot: a guy in a cowboy hat giving two thumbs up, framed by orange corner brackets" fetchpriority="high">
      <span class="stamp">Unofficial</span>
    </div>
  </div>
</header>

{{NAF}}

<div class="bar" id="bar">
  <div class="in">
    <div class="row">
      <div class="tabs" role="group" aria-label="Time slot">{{TABS}}</div>
    </div>
    <div class="panel" id="panel">
      <div class="wide">
        <label class="search"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
          <input id="q" type="search" placeholder="Search titles, vendors, people…" autocomplete="off" aria-label="Search workshops"></label>
        <label class="toggle"><input type="checkbox" id="mat"> Has material</label>
        <label class="toggle" title="Hide workshops that are mainly a tutorial for a commercial product"><input type="checkbox" id="oss"> Free &amp; open source</label>
      </div>
      <div class="chips" role="group" aria-label="Topics">{{CHIPS}}</div>
    </div>
    <div class="status"><span><span id="count" aria-live="polite"></span> <button type="button" id="showall" hidden></button></span><span class="sr"><button type="button" id="nafchip" class="nafchip" data-naf-clear hidden>NAF: <span></span> ✕</button><button type="button" id="clear" hidden>Reset<span class="wk"> filters</span></button><button type="button" class="fbtn" id="fbtn" aria-expanded="false" aria-controls="panel">Filters <span class="n" id="fcount">0</span></button></span></div>
  </div>
</div>

<main class="in">
  <nav class="jump" id="jump" aria-label="Jump to workshop"></nav>
{{SECTIONS}}
  <div class="empty" id="empty"><p>Nothing matches all of those filters together.</p><div class="relax" id="relax"></div></div>
  <ul class="info">{{NOTES}}</ul>
  <footer class="site">
    Not an official NAF page. Built from the <a href="{{OFFICIAL}}">AutoCon 6 agenda</a> and what the presenters posted in the #ac6-ws channels on the NAF Slack (the channel links only work if you're in that workspace). Refreshed a few times a day through Wednesday.
    Something wrong or missing? <a href="{{REPO}}/issues">Open an issue</a>.
  </footer>
</main>
<div class="note" id="note" role="status" hidden><span></span><button type="button" id="undo">Undo</button></div>

<script>
(function(){
  const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
  const cards=$$('.ws'), sections=$$('.blk'), tabs=$$('.tab'), chips=$$('.chip'), N=cards.length;
  const q=$('#q'), mat=$('#mat'), oss=$('#oss'), count=$('#count'), clear=$('#clear'), showall=$('#showall');
  const empty=$('#empty'), relaxBox=$('#relax'), note=$('#note'), undo=$('#undo');
  const fbtn=$('#fbtn'), panel=$('#panel'), fcount=$('#fcount'), bar=$('#bar'), jump=$('#jump');
  const dia=$('#nafDia'), nbs=$$('.nb'), panes=$$('.np'), nafchip=$('#nafchip');
  const NAME={}; nbs.forEach(b=>NAME[b.dataset.naf]=b.querySelector('b').textContent);
  const TOPICS=new Set(chips.map(c=>c.dataset.topic));
  const state={block:'',topics:new Set(),q:'',mat:true,oss:false,naf:''};
  const has=(list,x)=>(' '+list+' ').includes(' '+x+' ');
  const relTo=(c,id)=>has(c.dataset.core,id)||has(c.dataset.touch,id);
  const topOf=el=>el.getBoundingClientRect().top+scrollY;
  const pl=(n,w)=>n+' '+w+(n===1?'':'s');

  // jump strip
  cards.forEach(c=>{const a=document.createElement('a');a.href='#'+c.id;a.textContent=c.id.toUpperCase();
    a.className='b-'+c.dataset.block+(c.dataset.mat==='1'?' m':'');a.dataset.for=c.id;a.dataset.t=c.querySelector('h3').textContent;jump.appendChild(a);});

  // Every filter is AND-ed with the others; topics are OR-ed among themselves.
  // fails(c) lists the active filters that hide card c, so [] means visible.
  function fails(c){
    const f=[];
    if(state.block&&c.dataset.block!==state.block)f.push('block');
    if(state.topics.size&&!c.dataset.topics.split(' ').some(t=>state.topics.has(t)))f.push('topics');
    const w=state.q.toLowerCase().split(/\s+/).filter(Boolean);
    if(w.length&&!w.every(x=>c.dataset.search.includes(x)))f.push('q');
    if(state.mat&&c.dataset.mat!=='1')f.push('mat');
    if(state.oss&&c.dataset.oss==='product')f.push('oss');
    if(state.naf&&!relTo(c,state.naf))f.push('naf');
    return f;
  }
  const without=(f,k)=>f.length===0||(f.length===1&&f[0]===k); // visible once filter k is dropped
  const onlyBy=(f,k)=>f.length===1&&f[0]===k;                    // hidden by filter k and nothing else
  const DROP={block:()=>state.block='',topics:()=>state.topics.clear(),q:()=>state.q='',mat:()=>state.mat=false,oss:()=>state.oss=false,naf:()=>state.naf=''};
  const DID={block:'showing every time slot',topics:'cleared the topic filter',q:'cleared the search',mat:'included workshops without material',oss:'included vendor product workshops',naf:'cleared the NAF filter'};
  const RELAX={mat:n=>'Show '+n+' without material',oss:n=>'Show '+pl(n,'vendor workshop'),block:n=>'Show '+n+' in other time slots',
    topics:n=>'Show '+n+' with other topics',q:n=>'Show '+n+' without the search',naf:n=>'Show '+n+' outside '+NAME[state.naf]};
  const changed=()=>!!(state.block||state.topics.size||state.q||!state.mat||state.oss||state.naf);
  const snap=()=>({...state,topics:new Set(state.topics)});

  function readURL(){
    const p=new URLSearchParams(location.search);
    state.block=(p.get('slot')||'').toUpperCase().replace(/[^A-D]/g,'').slice(0,1);
    state.topics=new Set((p.get('topic')||'').split(',').filter(t=>TOPICS.has(t)));
    state.q=(p.get('q')||'').trim(); state.mat=p.get('material')!=='0'; state.oss=p.get('oss')==='1';
    const n=p.get('naf')||''; state.naf=NAME[n]?n:'';
  }
  function writeURL(){
    const p=new URLSearchParams();
    if(state.block)p.set('slot',state.block);
    if(state.topics.size)p.set('topic',[...state.topics].join(','));
    if(state.q)p.set('q',state.q);
    if(!state.mat)p.set('material','0');
    if(state.oss)p.set('oss','1');
    if(state.naf)p.set('naf',state.naf);
    const s=p.toString().replace(/%2C/g,',');
    history.replaceState(null,'',(s?'?'+s:location.pathname)+location.hash);
  }

  let F=new Map(), nt, prev=null;
  const cnt=pred=>cards.filter(c=>pred(F.get(c),c)).length;
  function apply(){
    note.hidden=true; prev=null; // any new filter change makes an earlier undo stale
    F=new Map(cards.map(c=>[c,fails(c)]));
    let shown=0;
    cards.forEach(c=>{
      const ok=!F.get(c).length; c.hidden=!ok; if(ok)shown++;
      c.querySelectorAll('.tag').forEach(g=>g.classList.toggle('hit',state.topics.has(g.dataset.topic)));
      const rc=!!state.naf&&has(c.dataset.core,state.naf), rt=!rc&&!!state.naf&&has(c.dataset.touch,state.naf);
      c.classList.toggle('rel-core',rc); c.classList.toggle('rel-touch',rt);
      c.querySelector('.ws-rel').textContent=rc?'Core: '+NAME[state.naf]:rt?'Touches '+NAME[state.naf]:'';
      c.querySelectorAll('.ws-naf button').forEach(b=>{const on=b.dataset.naf===state.naf;b.classList.toggle('hit',on);b.setAttribute('aria-pressed',String(on));});
      const j=jump.querySelector('[data-for="'+c.id+'"]');
      if(j){j.classList.toggle('off',!ok);j.title=j.dataset.t+(ok?'':' (hidden by your filters, click to show it)');}
    });
    sections.forEach(s=>s.hidden=!s.querySelector('.ws:not([hidden])'));

    // facet counts: what you would see if you picked this option, given every other filter
    tabs.forEach(b=>{const k=b.dataset.block, on=k===state.block, n=cnt((f,c)=>without(f,'block')&&(!k||c.dataset.block===k));
      b.setAttribute('aria-pressed',String(on)); b.querySelector('.tn').textContent=n; b.classList.toggle('zero',!n&&!on);
      b.title=n?'':'Nothing here with your other filters';
      if(on){const t=b.parentElement;t.scrollLeft=Math.max(0,b.offsetLeft-t.clientWidth/2+b.offsetWidth/2);}});
    chips.forEach(b=>{const t=b.dataset.topic, on=state.topics.has(t), n=cnt((f,c)=>without(f,'topics')&&has(c.dataset.topics,t));
      b.setAttribute('aria-pressed',String(on)); b.querySelector('span').textContent=n; b.classList.toggle('zero',!n&&!on);});
    if(q.value.trim()!==state.q)q.value=state.q;
    mat.checked=state.mat; oss.checked=state.oss;

    // NAF explorer
    nbs.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.naf===state.naf)));
    dia.classList.toggle('has-sel',!!state.naf);
    panes.forEach(p=>p.hidden=p.dataset.panel!==state.naf);
    nafchip.hidden=!state.naf; nafchip.querySelector('span').textContent=NAME[state.naf]||'';
    if(state.naf){
      const pn=$('.np[data-panel="'+state.naf+'"]'), rel=cards.filter(c=>relTo(c,state.naf)), vis=rel.filter(c=>!c.hidden).length;
      pn.querySelectorAll('.nr').forEach(r=>{const c=document.getElementById(r.dataset.ws), off=!!c&&c.hidden;
        r.classList.toggle('off',off); r.title=off?'Hidden by your other filters. Click to show it.':'';});
      const go=pn.querySelector('[data-go]'), all=pn.querySelector('[data-showrel]');
      go.textContent=!vis?'No cards match your other filters':vis===rel.length?'Jump to the '+(vis===1?'card':vis+' cards')+' ↓':'Jump to '+vis+' of '+rel.length+' cards ↓';
      go.disabled=!vis; all.hidden=vis===rel.length; all.textContent='Show all '+rel.length;
    }

    // status row
    const inPanel=state.topics.size+(state.q?1:0)+(state.mat?1:0)+(state.oss?1:0);
    fcount.textContent=inPanel; fbtn.classList.toggle('on',inPanel>0);
    clear.hidden=!changed();
    count.innerHTML=(shown===N?'All '+N:shown+' of '+N)+'<span class="wk"> workshops</span>';
    const more=cnt(f=>onlyBy(f,'mat'));
    showall.hidden=!shown||!more; showall.textContent='+'+more+' without material';

    // empty state: offer to drop whichever single filter would bring results back
    empty.classList.toggle('show',!shown);
    relaxBox.textContent='';
    if(!shown){
      ['mat','oss','block','topics','q','naf'].forEach(k=>{const n=cnt(f=>onlyBy(f,k));if(!n)return;
        const b=document.createElement('button');b.type='button';b.dataset.relax=k;b.textContent=RELAX[k](n);relaxBox.appendChild(b);});
      const r=document.createElement('button');r.type='button';r.dataset.reset='';r.textContent='Reset filters';relaxBox.appendChild(r);
    }
    writeURL();
  }

  // small toast when we change filters for the user, with undo
  function notify(msg,before){note.firstChild.textContent=msg;prev=before;undo.hidden=!before;note.hidden=false;clearTimeout(nt);nt=setTimeout(()=>note.hidden=true,6000);}
  undo.addEventListener('click',()=>{if(!prev)return;Object.assign(state,prev,{topics:new Set(prev.topics)});prev=null;note.hidden=true;apply();toResults();});

  function reset(){state.block='';state.topics.clear();state.q='';state.mat=true;state.oss=false;state.naf='';apply();}
  // If the user has scrolled down into the results, bring the top of the results back under the bar.
  function toResults(){const y=topOf(jump)-bar.offsetHeight-8;if(scrollY>y+2)scrollTo({top:y,behavior:'smooth'});}
  // For clicks on a card: keep that card where it was on screen while the list re-flows around it.
  function anchored(el,fn){const t0=el.getBoundingClientRect().top;fn();
    if(el.offsetParent){const d=el.getBoundingClientRect().top-t0;if(Math.abs(d)>1)scrollTo(0,scrollY+d);}else toResults();}
  // Show one card: drop only the filters that hide it, and say so.
  function reveal(c){
    const f=fails(c); if(!f.length){note.hidden=true;return;}
    const before=snap(); f.forEach(k=>DROP[k]()); apply();
    notify('Showing '+c.id.toUpperCase()+': '+f.map(k=>DID[k]).join(' and ')+'.',before);
  }
  function goTo(c,smooth=true){
    history.replaceState(null,'',location.pathname+location.search+'#'+c.id);
    scrollTo({top:topOf(c)-bar.offsetHeight-12,behavior:smooth?'smooth':'auto'});
    c.classList.remove('flash'); void c.offsetWidth; c.classList.add('flash');
  }
  const toggleTopic=t=>{state.topics.has(t)?state.topics.delete(t):state.topics.add(t);};

  // control bar
  tabs.forEach(b=>b.addEventListener('click',()=>{state.block=b.dataset.block;apply();toResults();}));
  chips.forEach(b=>b.addEventListener('click',()=>{toggleTopic(b.dataset.topic);apply();toResults();}));
  let tm;q.addEventListener('input',()=>{clearTimeout(tm);tm=setTimeout(()=>{const v=q.value.trim();if(v===state.q)return;state.q=v;apply();toResults();},150);});
  mat.addEventListener('change',()=>{state.mat=mat.checked;apply();toResults();});
  oss.addEventListener('change',()=>{state.oss=oss.checked;apply();toResults();});
  showall.addEventListener('click',()=>{state.mat=false;apply();toResults();});
  clear.addEventListener('click',()=>{reset();toResults();});
  fbtn.addEventListener('click',()=>{const o=panel.classList.toggle('open');fbtn.setAttribute('aria-expanded',String(o));if(o)q.focus({preventScroll:true});});
  document.addEventListener('keydown',ev=>{if(ev.key==='/'&&!/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)){ev.preventDefault();panel.classList.add('open');fbtn.setAttribute('aria-expanded','true');q.focus();}});

  document.addEventListener('click',ev=>{
    const t=ev.target;
    // topic tag on a card
    const g=t.closest('.ws .tag[data-topic]');
    if(g){anchored(g,()=>{toggleTopic(g.dataset.topic);apply();});return;}
    // NAF block: on a card it filters in place, in the diagram/coverage list it toggles and shows the panel
    const nb=t.closest('[data-naf]');
    if(nb){
      const id=nb.dataset.naf;
      if(nb.closest('.ws')){anchored(nb,()=>{state.naf=state.naf===id?'':id;apply();});return;}
      state.naf=state.naf===id?'':id; apply();
      if(state.naf){const pn=$('#nafPanel'),r=pn.getBoundingClientRect();if(r.top>innerHeight-140)scrollTo({top:topOf(pn)-16,behavior:'smooth'});}
      return;
    }
    const nc=t.closest('[data-naf-clear]');
    if(nc){state.naf='';apply();if(nc.id==='nafchip')toResults();return;}
    if(t.closest('[data-showrel]')){
      const rel=cards.filter(c=>relTo(c,state.naf)), drop=new Set(rel.flatMap(fails));
      if(drop.size){const before=snap();drop.forEach(k=>DROP[k]());apply();
        notify('Showing all '+rel.length+' '+NAME[state.naf]+' workshops: '+[...drop].map(k=>DID[k]).join(' and ')+'.',before);}
    }
    if(t.closest('[data-go],[data-showrel]')){const f=$('.ws:not([hidden])')||empty;scrollTo({top:topOf(f)-bar.offsetHeight-12,behavior:'smooth'});return;}
    const rx=t.closest('[data-relax]');
    if(rx){DROP[rx.dataset.relax]();apply();toResults();return;}
    if(t.closest('[data-reset]')){reset();toResults();return;}
    // any in-page link to a workshop (jump strip, NAF rows, card codes): reveal it if filtered out, then scroll to it
    const a=t.closest('a[href^="#"]');
    if(a){const c=document.getElementById(a.getAttribute('href').slice(1));
      if(c&&c.classList.contains('ws')){ev.preventDefault();reveal(c);goTo(c);}}
  });
  addEventListener('hashchange',()=>{const c=document.getElementById(location.hash.slice(1));if(c&&c.classList.contains('ws')){reveal(c);goTo(c);}});

  const hl=(core,touch)=>{nbs.forEach(b=>{const k=b.dataset.naf;b.classList.toggle('hl-core',core.includes(k));b.classList.toggle('hl-touch',!core.includes(k)&&touch.includes(k));});
    dia.classList.toggle('hovering',core.length+touch.length>0);};
  const onRow=ev=>{const r=ev.target.closest('.nr');r?hl(r.dataset.core.split(' ').filter(Boolean),r.dataset.touch.split(' ').filter(Boolean)):hl([],[]);};
  $('#nafPanel').addEventListener('pointerover',onRow);
  $('#nafPanel').addEventListener('focusin',onRow);
  $('#nafPanel').addEventListener('pointerleave',()=>hl([],[]));
  $('#nafPanel').addEventListener('focusout',ev=>{if(!$('#nafPanel').contains(ev.relatedTarget))hl([],[]);});

  // live slot
  function markLive(){
    const now=Date.now();
    $$('[data-start]').forEach(el=>{const live=now>=Date.parse(el.dataset.start)&&now<Date.parse(el.dataset.end);el.classList.toggle('is-live',live);});
  }
  markLive(); setInterval(markLive,60000);

  // GTA VI countdown: midnight local time, Thu 19 Nov 2026
  const gtaAt=new Date(2026,10,19,0,0,0).getTime(), clock=$('#gtaClock'), done=$('#gtaDone');
  const pad=n=>String(n).padStart(2,'0');
  function tick(){
    let t=Math.max(0,Math.floor((gtaAt-Date.now())/1000));
    if(!t){clock.hidden=true;done.hidden=false;return;}
    const d=Math.floor(t/86400),h=Math.floor(t%86400/3600),m=Math.floor(t%3600/60),s=t%60;
    clock.querySelector('[data-u=d]').textContent=d; clock.querySelector('[data-u=h]').textContent=pad(h);
    clock.querySelector('[data-u=m]').textContent=pad(m); clock.querySelector('[data-u=s]').textContent=pad(s);
  }
  tick(); setInterval(tick,1000);

  readURL(); apply();
  // shared link to one workshop (#c3): make sure it is visible even if the default filters would hide it
  if(location.hash){const el=document.getElementById(location.hash.slice(1));
    if(el){if(el.classList.contains('ws'))reveal(el);setTimeout(()=>el.classList.contains('ws')?goTo(el,false):el.scrollIntoView(),60);}}
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
