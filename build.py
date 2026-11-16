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


def ul(items):
    return "<ul>" + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>"


def card(w, blocks, topic_labels):
    b = w["code"][0]
    has_links = bool(w.get("links"))
    empty = not (w.get("links") or w.get("prep") or w.get("notes"))
    search = " ".join([w["code"], w["title"], w["org"], w["tldr"], " ".join(w["proctors"]),
                       " ".join(topic_labels[t] for t in w.get("topics", []))]).lower()

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

    out = [f'<article class="ws" id="{w["code"].lower()}" data-block="{b}" data-mat="{int(has_links)}" data-oss="{op}" '
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
    blocks = {b[0]: f"{b[2].split()[0][:3]} {b[3][8:10]} Nov · {b[3][11:16]}–{b[4][11:16]}" for b in BLOCKS}
    updated_dt = datetime.fromisoformat(data["updated"])
    updated = updated_dt.strftime("%a %d %b, %H:%M").replace(" 0", " ")
    counts = {t["id"]: sum(1 for w in ws if t["id"] in w.get("topics", [])) for t in topics}
    n_mat = sum(1 for w in ws if w.get("links"))

    tabs = ['<button type="button" class="tab" data-block="" aria-pressed="true">All</button>']
    for code, short, _, start, end in BLOCKS:
        tabs.append(f'<button type="button" class="tab" data-block="{code}" data-start="{start}" data-end="{end}" aria-pressed="false">'
                    f'<i class="dot b-{code}"></i>{e(short)}<span class="live">Live</span></button>')

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
            .replace("{{TABS}}", "".join(tabs))
            .replace("{{CHIPS}}", chips)
            .replace("{{SECTIONS}}", "\n".join(sections))
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
<title>AutoCon 6 Workshop Guide</title>
<meta name="description" content="What each AutoCon 6 workshop covers, what to set up beforehand, and where the material lives.">
<meta name="theme-color" content="#1b1430">
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
.status{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-top:10px;font-size:13px;color:var(--sub)}
.status button{border:0;background:none;padding:0;text-decoration:underline;text-underline-offset:2px;font-size:13px;color:var(--sub)}
.status button[hidden]{display:none}
#showall{color:var(--ink)!important;font-weight:600}
.wide{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.sr{display:inline-flex;align-items:center;gap:12px}
.fbtn{padding:6px 11px;font-size:13.5px;color:var(--ink)}
@media (max-width:640px){
  .tabs{flex:1 1 100%}
  .tab{padding:7px 9px;font-size:13.5px;gap:6px}
  .tab .live,.tab.is-live .live{display:none}
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
.jump a.off{opacity:.3;pointer-events:none}

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
.info{margin:28px 0 0;padding:14px 16px 14px 34px;background:var(--panel);border:1px solid var(--hair);border-radius:12px;font-size:14px;color:var(--sub)}
.info li+li{margin-top:4px}
footer.site{margin:40px 0 0;padding:24px 0 48px;border-top:1px solid var(--hair);font-size:13.5px;color:var(--sub)}
footer.site a{color:var(--ink)}
</style>
</head>
<body>
<header class="mast">
  <div class="in">
    <div class="kicker">{{CITY}} · Mon 16 &amp; Tue 17 Nov</div>
    <h1>AutoCon 6<b>Workshop Guide</b></h1>
    <p>What each workshop covers, what to set up before you sit down, and where the slides, repos and labs are.</p>
    <div class="stats">
      <span><strong>{{N}}</strong> workshops</span>
      <span><strong>{{NMAT}}</strong> with material posted</span>
      <span><i class="pulse"></i>Updated <time datetime="{{UPDATED_ISO}}">{{UPDATED}}</time> MST</span>
    </div>
  </div>
</header>

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
    <div class="status"><span><span id="count" aria-live="polite"></span> <button type="button" id="showall" hidden></button></span><span class="sr"><button type="button" id="clear" hidden>Clear filters</button><button type="button" class="fbtn" id="fbtn" aria-expanded="false" aria-controls="panel">Filters <span class="n" id="fcount">0</span></button></span></div>
  </div>
</div>

<main class="in">
  <nav class="jump" id="jump" aria-label="Jump to workshop"></nav>
{{SECTIONS}}
  <div class="empty" id="empty">Nothing matches those filters. <button type="button" class="tag" id="clear2">Clear filters</button></div>
  <ul class="info">{{NOTES}}</ul>
  <footer class="site">
    Not an official NAF page. Built from the <a href="{{OFFICIAL}}">AutoCon 6 agenda</a> and what the presenters posted in the #ac6-ws channels on the NAF Slack (the channel links only work if you're in that workspace). Refreshed a few times a day through Wednesday.
    Something wrong or missing? <a href="{{REPO}}/issues">Open an issue</a>.
  </footer>
</main>

<script>
(function(){
  const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
  const cards=$$('.ws'), sections=$$('.blk'), tabs=$$('.tab'), chips=$$('.chip');
  const q=$('#q'), mat=$('#mat'), oss=$('#oss'), count=$('#count'), clear=$('#clear'), empty=$('#empty');
  const fbtn=$('#fbtn'), panel=$('#panel'), fcount=$('#fcount');
  const state={block:'',topics:new Set(),q:'',mat:true,oss:false};

  // jump strip
  const jump=$('#jump');
  cards.forEach(c=>{const a=document.createElement('a');a.href='#'+c.id;a.textContent=c.id.toUpperCase();
    a.className='b-'+c.dataset.block+(c.dataset.mat==='1'?' m':'');a.dataset.for=c.id;a.title=c.querySelector('h3').textContent;jump.appendChild(a);});

  function readURL(){
    const p=new URLSearchParams(location.search);
    state.block=(p.get('slot')||'').toUpperCase().replace(/[^A-D]/g,'').slice(0,1);
    state.topics=new Set((p.get('topic')||'').split(',').filter(Boolean));
    state.q=p.get('q')||''; state.mat=p.get('material')!=='0'; state.oss=p.get('oss')==='1';
  }
  function writeURL(){
    const p=new URLSearchParams();
    if(state.block)p.set('slot',state.block);
    if(state.topics.size)p.set('topic',[...state.topics].join(','));
    if(state.q)p.set('q',state.q);
    if(!state.mat)p.set('material','0');
    if(state.oss)p.set('oss','1');
    const s=p.toString().replace(/%2C/g,',');
    history.replaceState(null,'',(s?'?'+s:location.pathname)+location.hash);
  }
  function apply(){
    const words=state.q.toLowerCase().split(/\s+/).filter(Boolean);
    let shown=0;
    cards.forEach(c=>{
      const t=c.dataset.topics.split(' ');
      const ok=(!state.block||c.dataset.block===state.block)
        &&(!state.topics.size||t.some(x=>state.topics.has(x)))
        &&(!state.mat||c.dataset.mat==='1')
        &&(!state.oss||c.dataset.oss!=='product')
        &&words.every(w=>c.dataset.search.includes(w));
      c.hidden=!ok; if(ok)shown++;
      c.querySelectorAll('.tag').forEach(g=>g.classList.toggle('hit',state.topics.has(g.dataset.topic)));
      const j=jump.querySelector('[data-for="'+c.id+'"]'); if(j)j.classList.toggle('off',!ok);
    });
    sections.forEach(s=>s.hidden=!s.querySelector('.ws:not([hidden])'));
    tabs.forEach(b=>{const on=b.dataset.block===state.block;b.setAttribute('aria-pressed',String(on));
      if(on){const t=b.parentElement;t.scrollLeft=Math.max(0,b.offsetLeft-t.clientWidth/2+b.offsetWidth/2);}});
    chips.forEach(b=>b.setAttribute('aria-pressed',String(state.topics.has(b.dataset.topic))));
    q.value=state.q; mat.checked=state.mat; oss.checked=state.oss;
    const nf=state.topics.size+(state.q?1:0)+(state.oss?1:0);
    fcount.textContent=nf; fbtn.classList.toggle('on',nf>0);
    const any=nf>0||state.block||!state.mat;
    clear.hidden=!any;
    count.textContent=shown===cards.length?'Showing all '+cards.length+' workshops':(state.mat?shown+' with material':shown+' of '+cards.length)+(state.oss&&shown<cards.length?' · open source':'');
    const sa=$('#showall'); sa.hidden=!state.mat; sa.textContent='Show all '+cards.length;
    empty.classList.toggle('show',shown===0);
    writeURL();
  }
  function reset(){state.block='';state.topics.clear();state.q='';state.mat=true;state.oss=false;apply();}
  $('#showall').addEventListener('click',()=>{state.mat=false;apply();});

  tabs.forEach(b=>b.addEventListener('click',()=>{state.block=b.dataset.block;apply();
    const s=state.block&&document.querySelector('.blk[data-block="'+state.block+'"]');
    if(s){const y=s.getBoundingClientRect().top+scrollY-$('#bar').offsetHeight-8;if(scrollY>y||y-scrollY>innerHeight*.6)scrollTo({top:y,behavior:'smooth'});}}));
  chips.forEach(b=>b.addEventListener('click',()=>{const t=b.dataset.topic;state.topics.has(t)?state.topics.delete(t):state.topics.add(t);apply();}));
  document.addEventListener('click',ev=>{const g=ev.target.closest('.tag[data-topic]');if(!g)return;
    const t=g.dataset.topic;state.topics.has(t)?state.topics.delete(t):state.topics.add(t);apply();});
  let tm;q.addEventListener('input',()=>{clearTimeout(tm);tm=setTimeout(()=>{state.q=q.value.trim();apply();},120);});
  mat.addEventListener('change',()=>{state.mat=mat.checked;apply();});
  oss.addEventListener('change',()=>{state.oss=oss.checked;apply();});
  clear.addEventListener('click',reset); $('#clear2').addEventListener('click',reset);
  fbtn.addEventListener('click',()=>{const o=panel.classList.toggle('open');fbtn.setAttribute('aria-expanded',String(o));if(o)q.focus({preventScroll:true});});
  document.addEventListener('keydown',ev=>{if(ev.key==='/'&&document.activeElement!==q){ev.preventDefault();panel.classList.add('open');q.focus();}});

  // live slot
  function markLive(){
    const now=Date.now();
    $$('[data-start]').forEach(el=>{const live=now>=Date.parse(el.dataset.start)&&now<Date.parse(el.dataset.end);el.classList.toggle('is-live',live);});
  }
  markLive(); setInterval(markLive,60000);

  readURL(); apply();
  if(location.hash){const t=document.querySelector(location.hash);if(t)setTimeout(()=>t.scrollIntoView(),50);}
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
