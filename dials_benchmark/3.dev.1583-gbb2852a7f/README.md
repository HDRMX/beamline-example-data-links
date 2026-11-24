# DIALS Benchmark

Nov 21 2026

All datasets listed in <https://github.com/HDRMX/beamline-example-data-links> were downloaded and processed using DIALS. All data was treated the same way with the same processing script, `tldr.sh`. Claude was used to orchestrate the processing and make a report, but the processing was solely DIALS using the same `tldr.sh` script per dataset.

Made with a development build of DIALS to be able to use the new d_min=auto feature of dials.scale, which is not yet in a DIALS release.

`dials.scale d_min=auto` cuts each dataset at the resolution limit DIALS estimates from its CC½ fit. The `overall_*` columns of `all_results.csv` hold the statistics of the cut data, and `suggested_d_min_cc_half_fit` the limit that was applied. The table and report were brought to this layout on Nov 24 2026 from the existing logs, without re-running any processing; see [claude/round/HISTORY.md](claude/round/HISTORY.md).

## Contents

| File | Description |
| ---- | ----------- |
| [report.md](report.md) | Full report, readable on GitHub |
| [report.html](report.html) | Full report, interactive version (download to view) |
| [all_results.csv](all_results.csv) | Benchmark results |
| [tldr.sh](tldr.sh) | Processing script |
| [claude/](claude/) | Full set of Claude scripts and `.md` files controlling the orchestration |
