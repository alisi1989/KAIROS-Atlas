#!/usr/bin/env python3
"""Validate a KAIROS Atlas submission (a `kairos infer --json` record).

Run it on your file BEFORE opening a pull request:

    python build/validate_submission.py submissions/EUR/GBR/rs4988235.json

or validate every submission at once (what CI does):

    python build/validate_submission.py --all

It checks the things that can be verified from the JSON alone — schema, required
fields, and internal consistency (carrier count vs frequency, point estimate inside
its interval, grade/band pairing). It does NOT need KAIROS installed and pulls in no
third-party packages.

What it deliberately does NOT hard-gate: the exact model hashes. It prints the model
files + sha256 a record references so a maintainer can confirm provenance against the
released KAIROS MANIFEST; pinning hashes here would reject legitimate records whenever
the models are re-frozen. Provenance is a maintainer-review step, not an auto-reject.

Exit code 0 = all validated files pass; 1 = at least one failed.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUB_DIR = ROOT / "submissions"

SCHEMA = "kairos.infer.v2"
FREQ_TOL = 2e-3            # |derived_freq - n_carriers/n_haplotypes| must be within this
GRADE_BAND = {"A": "green", "B": "yellow", "C": "red"}


class Report:
    """Collects errors (fatal) and warnings (informational) for one file."""

    def __init__(self, path):
        self.path = path
        self.errors = []
        self.warnings = []
        self.info = []

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def note(self, msg):
        self.info.append(msg)

    @property
    def ok(self):
        return not self.errors


def _num(x):
    return x if isinstance(x, (int, float)) and not isinstance(x, bool) else None


def _require(d, key, rep, where):
    if key not in d:
        rep.err(f"{where}: missing required field '{key}'")
        return None
    return d[key]


def validate(path: Path) -> Report:
    rep = Report(path)
    try:
        doc = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        rep.err(f"not valid JSON: {e}")
        return rep
    if not isinstance(doc, dict):
        rep.err("top-level JSON must be an object")
        return rep

    # --- schema + top-level shape -------------------------------------------------
    schema = doc.get("schema")
    if schema != SCHEMA:
        rep.err(f"schema is {schema!r}, expected {SCHEMA!r} "
                f"(re-run with a current KAIROS: `kairos infer ... --json`)")
    for key in ("focal", "demography", "selection_test", "onset",
                "selection_coefficient", "reliability", "models", "analysis_status"):
        _require(doc, key, rep, "top level")

    status = doc.get("analysis_status") or {}
    selected = status.get("selected")
    if not isinstance(selected, bool):
        rep.err("analysis_status.selected must be true/false")

    # --- focal: carrier count vs frequency ---------------------------------------
    focal = doc.get("focal") or {}
    bp = _num(focal.get("bp"))
    n_car = focal.get("n_carriers")
    n_hap = focal.get("n_haplotypes")
    freq = _num(focal.get("derived_freq"))
    if not focal.get("chrom"):
        rep.err("focal.chrom is empty")
    if bp is None or bp <= 0:
        rep.err("focal.bp must be a positive position")
    if not focal.get("rsid"):
        rep.err("focal.rsid is empty")
    if not isinstance(n_car, int) or not isinstance(n_hap, int):
        rep.err("focal.n_carriers and focal.n_haplotypes must be integers")
    elif n_hap <= 0:
        rep.err("focal.n_haplotypes must be > 0")
    elif not (0 <= n_car <= n_hap):
        rep.err(f"focal.n_carriers ({n_car}) must be in [0, n_haplotypes={n_hap}]")
    elif freq is not None:
        expected = n_car / n_hap
        if abs(freq - expected) > FREQ_TOL:
            rep.err(f"focal.derived_freq ({freq:.4f}) inconsistent with "
                    f"n_carriers/n_haplotypes ({n_car}/{n_hap}={expected:.4f})")
    if freq is not None and not (0.0 <= freq <= 1.0):
        rep.err(f"focal.derived_freq ({freq}) out of [0, 1]")

    # --- demography ---------------------------------------------------------------
    demog = doc.get("demography") or {}
    ne = _num(demog.get("ne"))
    if ne is None or ne <= 0:
        rep.err("demography.ne must be a positive effective size")

    # --- onset: point inside its interval (only when a date was produced) --------
    onset = doc.get("onset") or {}
    o_pt = _num(onset.get("reported_gen"))
    o_lo = _num(onset.get("lower_gen"))
    o_hi = _num(onset.get("upper_gen"))
    if o_pt is not None and o_lo is not None and o_hi is not None:
        if not (o_lo <= o_pt <= o_hi):
            rep.err(f"onset.reported_gen ({o_pt:.1f}) is outside its interval "
                    f"[{o_lo:.1f}, {o_hi:.1f}]")

    # --- selection coefficient: point inside its interval ------------------------
    sc = doc.get("selection_coefficient") or {}
    s_pt = _num(sc.get("s"))
    s_lo = _num(sc.get("lower"))
    s_hi = _num(sc.get("upper"))
    if s_pt is not None and s_lo is not None and s_hi is not None:
        if not (s_lo <= s_pt <= s_hi):
            rep.err(f"selection_coefficient.s ({s_pt:.4f}) is outside its interval "
                    f"[{s_lo:.4f}, {s_hi:.4f}]")

    # --- reliability: grade/band pairing -----------------------------------------
    rel = doc.get("reliability") or {}
    grade = rel.get("grade")
    band = rel.get("band")
    if grade in GRADE_BAND:
        if band != GRADE_BAND[grade]:
            rep.err(f"reliability grade {grade!r} should pair with band "
                    f"{GRADE_BAND[grade]!r}, found {band!r}")
    elif selected and grade not in (None, "—", "-"):
        rep.err(f"reliability.grade {grade!r} is not one of A/B/C")

    # --- models: shape + provenance surfaced (not hard-gated) --------------------
    models = doc.get("models") or {}
    if not isinstance(models, dict) or not models:
        rep.err("models block is missing or empty (provenance cannot be checked)")
    else:
        for role, m in models.items():
            if m is None:
                continue
            h = (m or {}).get("sha256")
            f = (m or {}).get("file")
            if not (isinstance(h, str) and len(h) == 64 and all(c in "0123456789abcdef" for c in h.lower())):
                rep.err(f"models.{role}: sha256 is not a 64-char hex digest")
            else:
                rep.note(f"model {role}: {f} @ {h[:16]}")

    # --- privacy / hygiene warnings ----------------------------------------------
    inp = doc.get("inputs") or {}
    for k in ("hap", "map"):
        v = inp.get(k)
        if isinstance(v, str) and (v.startswith("/Users/") or v.startswith("/home/") or ":\\Users\\" in v):
            rep.warn(f"inputs.{k} contains a local filesystem path ({v!r}); "
                     f"consider replacing it with a relative path or a source label")
    if selected is False:
        rep.note("record is not flagged as selected; onset/s are age/exploratory, not a selection date")

    return rep


def _print(rep: Report) -> None:
    rel = rep.path.relative_to(ROOT) if ROOT in rep.path.parents else rep.path
    mark = "PASS" if rep.ok else "FAIL"
    print(f"[{mark}] {rel}")
    for e in rep.errors:
        print(f"   ✗ {e}")
    for w in rep.warnings:
        print(f"   ! {w}")
    for i in rep.info:
        print(f"   · {i}")


def main(argv):
    args = [a for a in argv if a != "--all"]
    if "--all" in argv or not args:
        files = sorted(SUB_DIR.rglob("*.json")) if SUB_DIR.exists() else []
        if not files:
            print("no submissions found under submissions/ — nothing to validate")
            return 0
    else:
        files = [Path(a).resolve() for a in args]

    failed = 0
    for f in files:
        if not f.exists():
            print(f"[FAIL] {f}: file not found")
            failed += 1
            continue
        rep = validate(f)
        _print(rep)
        failed += not rep.ok

    n = len(files)
    print(f"\n{n - failed}/{n} file(s) passed"
          + (f", {failed} failed" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
