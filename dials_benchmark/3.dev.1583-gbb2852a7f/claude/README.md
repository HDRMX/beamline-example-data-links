# DIALS benchmark over the HDRMX beamline example data

Every deposition listed in https://github.com/HDRMX/beamline-example-data-links
is downloaded and put once through the same fixed DIALS pipeline (`tldr.sh`).

| File | Purpose |
|---|---|
| `tldr.sh` | the fixed pipeline (nine DIALS commands) |
| `GROUND_RULES.md` | rules for the per-entry processing agents |
| `DOWNLOAD_RULES.md` | rules for the per-entry download agents |
| `entries.tsv` | manifest: entry, data_entry, repo, facility, beamline, detector, link |
| `status.tsv` | status of every entry; changed only through `bin/status` |
| `entries/ENTRY/` | `data/`, `download.log`, `proc/`, `results.csv` |
| `all_results.csv` | all `results.csv` rows, built by `bin/aggregate.sh` |

| Script | Purpose |
|---|---|
| `bin/make_manifest.py` | builds `entries.tsv` from the repository README |
| `bin/status` | locked read/update of `status.tsv` |
| `bin/download_entry.py ENTRY` | download, unpack, verify one entry |
| `bin/find_inputs.py` | fixed rule choosing the `dials.import` arguments |
| `bin/process_entry.sh ENTRY` | run `tldr.sh` once on an entry and write its CSV |
| `bin/collect_results.py` | DIALS logs and models -> `results.csv` |
| `bin/aggregate.sh` | concatenate all `results.csv` |

Agent prompts:
- `Process entry XYZ and read /path/to/project/GROUND_RULES.md with the ground rules first.`
- `Download entry XYZ and read /path/to/project/DOWNLOAD_RULES.md with the rules first.`
