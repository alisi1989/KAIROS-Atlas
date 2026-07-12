# submissions/

Drop the JSON that `kairos infer --json` produced here, one file per variant × population,
then open a pull request. See the repository [CONTRIBUTING.md](../CONTRIBUTING.md) for the full
walk-through.

## Layout

```
submissions/<SUPERPOP>/<POP>/<rsid>.json     e.g. submissions/EUR/GBR/rs4988235.json
submissions/example/                          a reference record you can copy from
```

- `<SUPERPOP>` is the 1000 Genomes super-population (AFR, AMR, EAS, EUR, SAS) or your cohort's ancestry.
- `<POP>` is the population code (GBR, YRI, CHB, …) or your cohort label.
- One variant × one population per file. Do not overwrite someone else's file — add your own.

## Before you open the PR

```bash
python build/validate_submission.py submissions/EUR/GBR/rs4988235.json
```

It checks the schema, required fields, and internal consistency, and prints the model
hashes your record references. The same check runs automatically on your pull request.

## What is (and isn't) in a record

The file is KAIROS's per-locus **summary** JSON: onset, s, sweep type, selection test,
reliability grade, and the model provenance hashes. It carries **no individual-level
genotypes** — never submit raw `.hap`/`.map`/VCF data.
