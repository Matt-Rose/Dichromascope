#!/usr/bin/env python3
"""Stamp the current UTC time into index.html and lab.html as the build identifier.

Runs from the pre-commit hook (.githooks/pre-commit; enable once per clone with
`git config core.hooksPath .githooks`). The pages show the stamp and compare it
with the published copy to offer a reload when a newer build is live.
"""
import datetime, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
pat = re.compile(r'/\*BUILD-BEGIN\*/.*?/\*BUILD-END\*/', re.S)
for page in ("index.html", "lab.html"):
    p = ROOT / page
    text = p.read_text()
    if not pat.search(text):
        raise SystemExit(f"{page}: BUILD markers not found")
    p.write_text(pat.sub(f'/*BUILD-BEGIN*/ const BUILD = "{stamp}"; /*BUILD-END*/', text))
print("build", stamp)
