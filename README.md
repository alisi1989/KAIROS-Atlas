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

Enable GitHub Pages once (**Settings → Pages → Source: GitHub Actions**); every push then rebuilds and
deploys automatically to `https://alisi1989.github.io/KAIROS-Atlas/`.

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

## Contributing dated loci

Run KAIROS on your own data and submit the JSON — see [CONTRIBUTING.md](CONTRIBUTING.md). Submissions
are validated (schema + model provenance) before they enter the Atlas.

## Note on the reliability grade

While the Atlas is seeded from the curated 1000 Genomes literature panel, the A/B/C badge is derived
from the panel fields following the KAIROS reliability policy. As records are regenerated from live
`kairos infer` JSON, the badge comes directly from the KAIROS reliability index.

## License

Code under the repository [LICENSE](LICENSE). Dated-selection records © the KAIROS project; please
cite KAIROS when using the Atlas.
