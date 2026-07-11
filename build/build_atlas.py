#!/usr/bin/env python3
"""Build the KAIROS Atlas static site.

Reads the KAIROS panel TSV (one row per variant x population, with onset / s / sweep /
selection / tier / literature) and produces:

  index.html        self-contained page (data injected inline, works offline / on Pages)
  data/atlas.json   the same records as a downloadable JSON

Run:  python build/build_atlas.py
The GitHub Action runs this on every push and deploys the result to GitHub Pages.
"""
import csv, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "build" / "panel.tsv"          # source data (KAIROS panel export)
TEMPLATE = ROOT / "index_template.html"
OUT_HTML = ROOT / "index.html"
OUT_JSON = ROOT / "data" / "atlas.json"
YPG = 28.0                                      # years per generation


def num(x):
    try:
        v = float(x)
        return None if v != v else v            # drop NaN
    except (TypeError, ValueError):
        return None


def ci(x):
    m = re.findall(r"-?\d+\.?\d*", x or "")
    return [float(m[0]), float(m[1])] if len(m) >= 2 else None


def grade(sel, tier, freq, recent):
    """DEMO reliability grade, derived from the panel fields, following the KAIROS policy
    DIRECTION (green = in-domain, unambiguously selected, recent/calibrated tier). The production
    Atlas replaces this with the grade emitted by the live KAIROS reliability index."""
    if not sel:
        return "—", "na"
    if freq is not None and (freq >= 0.97 or freq <= 0.03):
        return "C", "red"
    if not recent:
        return "B", "yellow"
    if freq is not None and (freq >= 0.90 or freq <= 0.05):
        return "B", "yellow"
    return "A", "green"


def records():
    rows = list(csv.DictReader(open(PANEL), delimiter="\t"))
    out = []
    for r in rows:
        tier = r["tier"]
        sel = r["selected"] == "yes"
        freq = num(r["freq"])
        recent = tier.startswith("recent")
        g, band = grade(sel, tier, freq, recent)
        lk = num(r["lit_onset_kya"])
        out.append({
            "gene": r["gene"], "rsid": r["rsid"], "chrom": r["chrom"],
            "pop": r["pop"], "superpop": r["superpop"], "ne": int(float(r["ne"])),
            "freq": freq, "n_car": int(r["n_car"]), "sel_p": num(r["sel_p"]),
            "selected": sel, "sweep": r["sweep"], "p_soft": num(r["p_soft"]),
            "tier": tier, "onset_gen": num(r["onset_gen"]), "onset_ci": ci(r["onset_ci"]),
            "onset_yr": num(r["onset_yr"]), "s": num(r["s"]), "s_ci": ci(r["s_ci"]),
            "lit_s": num(r["lit_s"]), "lit_onset_kya": lk,
            "lit_onset_gen": (lk * 1000 / YPG if lk else None),
            "grade": g, "band": band,
        })
    return out


def main():
    data = records()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(data, indent=1))
    html = TEMPLATE.read_text()
    if "__ATLAS_DATA__" not in html:
        raise SystemExit("index_template.html is missing the __ATLAS_DATA__ placeholder")
    OUT_HTML.write_text(html.replace("__ATLAS_DATA__", json.dumps(data, separators=(",", ":"))))
    from collections import Counter
    bands = dict(Counter(d["band"] for d in data))
    print(f"built {len(data)} records -> index.html + data/atlas.json | bands {bands}")


if __name__ == "__main__":
    main()
