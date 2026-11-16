# AutoCon 6 Workshops: unofficial cheat sheet

A one-page site with a TL;DR, prep steps, rooms and material links for every AutoCon 6 workshop (Tucson, 16 to 17 Nov 2026).

Live: https://steinzi.github.io/autocon6-workshops/

## Sharing filtered views

Filters live in the URL, so you can share a filtered view:

- `?slot=D`: Tuesday afternoon only (slots A to D)
- `?topic=ai,telemetry`: workshops matching any of those topics
- `?material=0`: include workshops with no material yet (by default only ones with material show)
- `?oss=1`: hide vendor product tutorials (keeps open source and mostly open)
- `?naf=intent`: workshops covering one NAF Framework block (presentation, observability, orchestration, intent, collector, executor, infrastructure, practices)
- `?q=nokia`: free-text search
- `#c3`: jump straight to one workshop

## How it works

- `data/workshops.json` holds all the content, including the topic tags. Edit it there.
- `python3 build.py` regenerates `index.html` from it.
- GitHub Pages serves `index.html` from `main`.

Sources: the official list at https://networkautomation.forum/autocon6 and what presenters posted in the `#ac6-ws-*` channels of the Network Automation Forum Slack. Attendee names, Zoom passcodes and private details are left out on purpose.
