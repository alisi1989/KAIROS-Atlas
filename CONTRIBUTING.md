# Contributing dated loci to the KAIROS Atlas

The Atlas grows by pull request. You run KAIROS on your own polarized sample, and submit the JSON it
emits; CI validates it before it enters the map.

## 1. Produce a KAIROS record

```bash
kairos infer --hap sample.hap --map sample.map \
  --marker rs4988235 --ne 12500 --auto-tier --json my_locus.json
```

## 2. Self-check before you open the PR

From a clone of this repo:

```bash
python build/validate_submission.py my_locus.json
```

It runs the same checks CI runs, so you get instant feedback. `submissions/example/` holds a
reference record you can compare against. The validator is pure-stdlib Python — nothing to install.

## 3. Open a pull request

Add your JSON file(s) under `submissions/<SUPERPOP>/<POP>/` (e.g. `submissions/EUR/GBR/rs4988235.json`)
and open a PR. Include, in the PR body:

- the population and its ancestry (e.g. GBR / EUR) and the effective size used,
- the data source (public panel, cohort accession, or "own genotypes"),
- the KAIROS version (`kairos --version`).

## 4. What is checked

**Automatically, on the PR** (`build/validate_submission.py`):

- the JSON matches the current KAIROS output schema (`kairos.infer.v2`) and has the required fields,
- the focal marker is internally consistent — carrier count agrees with the reported frequency, and
  the frequency and Ne are in range,
- each point estimate (onset, s) sits inside its own interval, and the reliability grade and band agree,
- every referenced model carries a well-formed sha256 digest, which the check prints for review.

**By a maintainer, before merge:** the printed model hashes are confirmed against the released KAIROS
`MANIFEST` (so every record is reproducible from a known model set). Exact hashes are not auto-gated
here — they change whenever the models are re-frozen — so provenance is a review step, not an auto-reject.

Accepted records are merged into `build/panel.tsv` and the site rebuilds automatically.

## Ground rules

- One variant × one population per record; do not overwrite another contributor's record — add yours.
- No individual-level genotypes: submit only KAIROS's per-locus summary JSON.
- Report the honest grade. A yellow or red record is welcome and useful; a mislabeled green is not.
