# KAIROS Atlas

**When did natural selection happen?** A queryable, open map of *dated* selection signals across
human populations — for each variant, in each 1000 Genomes population: when selection began (onset,
with a 90% interval), how strong (selection coefficient *s*), the sweep mode, and a reliability grade.

Unlike a variant catalogue (which tells you *whether* a variant exists and at what frequency), the
KAIROS Atlas puts **time** on the axis — the question a frequency lookup can't answer.

Powered by [KAIROS](https://github.com/alisi1989/KAIROS): from a single modern polarized sample it
tests a focal variant for selection and dates the selection onset (no ancestral recombination graph
required).

## Live site

**https://alisi1989.github.io/KAIROS-Atlas/** — every push to `main` rebuilds and redeploys it
automatically via GitHub Actions.

## What each record shows

| field | meaning |
|---|---|
| onset | selection onset in generations and years ago, with a 90% conformal interval |
| s | selection coefficient (with interval) |
| sweep | hard (de novo) vs standing variation (SGV) — sets whether "onset" is selection onset or allele-lineage age |
| selection test | frequency-matched empirical neutral p-value + verdict |
| reliability | A/green (trust the point) · B/yellow (lean on the interval) · C/red (out of domain) |
| tier · Ne | recent vs deep dating tier, and the effective size used |
| literature | curated onset / s comparison where a published estimate exists |

## Build locally

```bash
python build/build_atlas.py      # panel.tsv -> index.html + data/atlas.json
python -m http.server 8000       # then open http://localhost:8000
```

`index.html` is self-contained (data embedded), so it also opens directly in a browser.

## Structure

```
build/build_atlas.py     turns the panel TSV into the site (single source of truth for records)
build/panel.tsv          the KAIROS panel export (one row per variant x population)
index_template.html      the page template (data injected at build time)
index.html               generated, self-contained, served by Pages
data/atlas.json          generated, the same records as downloadable JSON
```

## Submit your own dated loci

The Atlas grows by pull request: you run KAIROS on your own polarized sample and add the JSON it
emits. No genotypes are ever uploaded — only KAIROS's per-locus summary.

**1 — Produce a record.** Run KAIROS on your sample for the variant you care about:

```bash
kairos infer --hap sample.hap --map sample.map \
  --marker rs4988235 --ne 12500 --auto-tier --json rs4988235.json
```

**2 — Self-check it.** From a clone of this repo:

```bash
python build/validate_submission.py rs4988235.json
```

This checks the schema, the required fields, and internal consistency (carrier count vs frequency,
each point estimate inside its interval, grade/band pairing), and prints the model hashes your record
references. See `submissions/example/` for a reference record.

**3 — Open a pull request.** Add the file under `submissions/<SUPERPOP>/<POP>/` (e.g.
`submissions/EUR/GBR/rs4988235.json`) and, in the PR body, state the population and its ancestry, the
effective size used, the data source, and your KAIROS version (`kairos --version`). The same check
from step 2 runs automatically on your PR; a maintainer confirms the model provenance and merges it
into `build/panel.tsv`, after which the site rebuilds itself.

Full rules and ground rules: [CONTRIBUTING.md](CONTRIBUTING.md) · layout: [submissions/](submissions/).

## Note on the reliability grade

While the Atlas is seeded from the curated 1000 Genomes literature panel, the A/B/C badge is derived
from the panel fields following the KAIROS reliability policy. As records are regenerated from live
`kairos infer` JSON, the badge comes directly from the KAIROS reliability index.

## License

Code under the repository [LICENSE](LICENSE). Dated-selection records © the KAIROS project; please
cite KAIROS when using the Atlas.
