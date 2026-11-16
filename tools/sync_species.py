#!/usr/bin/env python3
"""Copy the numeric values from species.json into index.html and lab.html.

Run after editing species.json:  python3 tools/sync_species.py
The pages carry an inline copy (between SPECIES-DATA markers) so they work
without a server and inside the claude.ai artifact as well as on GitHub Pages.
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "species.json").read_text())

def v(sp, k):
    return sp[k]["value"]

compact = {
    key: {
        "name": sp["name"], "s": v(sp, "lambda_S_nm"), "l": v(sp, "lambda_L_nm"),
        "lens": v(sp, "lens_cutoff_nm"), "eta": v(sp, "S_cone_fraction"),
        "w": v(sp, "weber_chromatic_L"), "wY": v(sp, "weber_luminance"),
        "Yfail": v(sp, "colour_limit_cd_m2"),
        "lR": v(sp, "lambda_R_nm"), "rodGain": v(sp, "rod_sensitivity_vs_cones"),
        "rodK": v(sp, "rod_weber_ratio"), "rodSat": v(sp, "rod_saturation_cd_m2"),
    }
    for key, sp in data["species"].items()
}
block = "/*SPECIES-DATA-BEGIN*/ const SPECIES_DATA = " + json.dumps(compact) + "; /*SPECIES-DATA-END*/"
pat = re.compile(r"/\*SPECIES-DATA-BEGIN\*/.*?/\*SPECIES-DATA-END\*/", re.S)

for page in ("index.html", "lab.html"):
    path = ROOT / page
    text = path.read_text()
    if not pat.search(text):
        raise SystemExit(f"{page}: SPECIES-DATA markers not found")
    path.write_text(pat.sub(lambda _: block, text))
    print(f"updated {page}")
