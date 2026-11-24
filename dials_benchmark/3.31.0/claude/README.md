# DIALS benchmark over the HDRMX beamline example data

Every deposition listed in https://github.com/HDRMX/beamline-example-data-links
is downloaded once and put through the same fixed DIALS pipeline (`tldr.sh`).
The benchmark is repeated in **rounds**, one per DIALS build; raw data is shared,
everything else is kept per round.

| Path | Purpose |
|---|---|
| `CURRENT_ROUND` | name of the round the helpers work on (override with `HDRMX_ROUND`) |
| `rounds/ROUND/tldr.sh` | the fixed pipeline of that round (ten DIALS commands) |
| `rounds/ROUND/env.sh` | selects the DIALS build of that round |
| `rounds/ROUND/status.tsv` | status of every entry; changed only through `bin/status` |
| `rounds/ROUND/all_results.csv` | all `results.csv` rows, built by `bin/aggregate.sh` |
| `rounds/ROUND/report.html`, `report.md` | the round's report |
| `rounds/ROUND/FROZEN` | present when the round is closed; helpers then refuse to change it |
| `builds/` | DIALS installations |
| `GROUND_RULES.md` | rules for the per-entry processing agents |
| `DOWNLOAD_RULES.md` | rules for the per-entry download agents |
| `entries.tsv` | manifest: entry, data_entry, repo, facility, beamline, detector, link |
| `entries/ENTRY/data/` | raw images, shared by all rounds |
| `entries/ENTRY/rounds/ROUND/` | `proc/`, `results.csv`, `process.job.log` of that round |

Rounds:

| Round | DIALS | Notes |
|---|---|---|
| `3.31.0` | release 3.31.0 in `builds/dials_3.31.0` | `dials.scale` twice: uncut, then cut at the limit it suggests |

| Script | Purpose |
|---|---|
| `bin/make_manifest.py` | builds `entries.tsv` from the repository README |
| `bin/status` | locked read/update of the round's `status.tsv` |
| `bin/download_entry.py ENTRY` | download, unpack, verify one entry |
| `bin/find_inputs.py` | fixed rule choosing the `dials.import` arguments |
| `bin/process_entry.sh ENTRY` | run the round's `tldr.sh` once on an entry and write its CSV |
| `bin/collect_results.py` | DIALS logs and models -> `results.csv` |
| `bin/aggregate.sh` | concatenate all `results.csv` of the round |

Starting a new round: create `rounds/NAME/` with `tldr.sh`, `env.sh` and a
`status.tsv` in which every entry with data is `Downloaded`, write `FROZEN`
into the previous round, and put NAME into `CURRENT_ROUND`.

Agent prompts:
- `Process entry XYZ and read /path/to/project/GROUND_RULES.md with the ground rules first.`
- `Download entry XYZ and read /path/to/project/DOWNLOAD_RULES.md with the rules first.`
