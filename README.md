# Wisteria site
Edit CONFIG / SCHEDULE / TEACHERS / WORKSHOPS at the top of gen.py (copy lives in src/ for CSS and JS), then run `python3 gen.py`.
Output: site/ (PL at root, EN in site/en/). Set CONFIG["HIGHLIGHTS"]=False for the final build. CHECKLIST.md is regenerated on every run.
`python3 test.py` (needs playwright) checks links, menu, forms, map, language switch and takes screenshots.
