# DIALS Benchmark

Nov 21 2026

All datasets listed in <https://github.com/HDRMX/beamline-example-data-links> were downloaded and processed using DIALS. All data was treated the same way with the same processing script, `tldr.sh`. Claude was used to orchestrate the processing and make a report, but the processing was solely DIALS using the same `tldr.sh` script per dataset.

Made with a development build of DIALS to be able to use the new d_min=auto feature of dials.scale, which is not yet in a DIALS release.

## Contents

| File | Description |
| ---- | ----------- |
| [report.md](report.md) | Full report, readable on GitHub |
| [report.html](report.html) | Full report, interactive version (download to view) |
| [all_results.csv](all_results.csv) | Benchmark results |
| [tldr.sh](tldr.sh) | Processing script |
| [claude/](claude/) | Full set of Claude scripts and `.md` files controlling the orchestration |
