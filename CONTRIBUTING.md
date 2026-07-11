# Contributing dated loci to the KAIROS Atlas

The Atlas grows by pull request. You run KAIROS on your own polarized sample, and submit the JSON it
emits; CI validates it before it enters the map.

## 1. Produce a KAIROS record

```bash
kairos infer --hap sample.hap --map sample.map \
  --marker rs4988235 --ne 12500 --auto-tier --json my_locus.json
```

## 2. Open a pull request

Add your JSON file(s) under `submissions/<population>/` and open a PR. Include, in the PR body:

- the population and its ancestry (e.g. GBR / EUR) and the effective size used,
- the data source (public panel, cohort accession, or "own genotypes"),
- the KAIROS version (`kairos --version`).

## 3. What CI checks

A submission is accepted only if:

- the JSON matches the current KAIROS output schema,
- the referenced model hashes match the frozen production models (so every record is reproducible),
- the reliability grade recomputes to the value in the file,
- the focal marker, frequency, and Ne are internally consistent.

Accepted records are merged into `build/panel.tsv` and the site rebuilds automatically.

## Ground rules

- One variant × one population per record; do not overwrite another contributor's record — add yours.
- No individual-level genotypes: submit only KAIROS's per-locus summary JSON.
- Report the honest grade. A yellow or red record is welcome and useful; a mislabeled green is not.
