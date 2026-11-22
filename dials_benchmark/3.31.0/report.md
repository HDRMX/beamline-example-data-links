# DIALS 3.31.0 benchmark report

468 public depositions listed in [HDRMX/beamline-example-data-links](https://github.com/HDRMX/beamline-example-data-links) were each put once through the same fixed DIALS script. **331** ran through the whole pipeline, **95** stopped at a step, and **42** could not be downloaded.

Every entry goes through import, spot finding, indexing, refinement, integration, symmetry, scaling, export and merging, with no per-dataset options. A failure is recorded as a result and is not repaired.

Among completed entries, the median high-resolution limit is **1.39 Å** with no resolution cutoff applied (**1.80 Å** at the limit DIALS suggests), the median overall CC½ is **0.994**, and the median pipeline run takes **4.5 minutes** on 24 cores.

> **About the statistics.** dials.scale is run with its defaults, so no resolution cutoff is applied to any dataset. The headline resolution, CC½, completeness and multiplicity are therefore for all scaled data. The "suggested" columns give the same statistics at the resolution limit dials.merge suggests, where a fit of CC½ falls to 0.3. In `all_results.csv`, `overall_*` holds the uncut statistics and `suggested_*` the statistics at the suggested limit.

An interactive version of this report, with a sortable and filterable table, is in [report.html](report.html). The full set of metrics per entry is in [all_results.csv](all_results.csv).

## Contents

- [Results by repository](#results-by-repository)
- [Where the pipeline stopped](#where-the-pipeline-stopped)
- [How to read the failures](#how-to-read-the-failures)
- [The pipeline script](#the-pipeline-script)
- [System and software](#system-and-software)
- [All datasets](#all-datasets)

## Results by repository

| Repository | Entries | Complete | Failed | Download failed |
| --- | ---: | ---: | ---: | ---: |
| proteindiffraction.org | 223 | 178 | 39 | 6 |
| SBGrid | 114 | 88 | 24 | 2 |
| Other (manual) | 50 | 12 | 15 | 23 |
| PDBj XRDA | 37 | 23 | 7 | 7 |
| Zenodo | 34 | 23 | 8 | 3 |
| MX-RDR | 10 | 7 | 2 | 1 |
| **Total** | **468** | **331** | **95** | **42** |

## Where the pipeline stopped

Failed entries counted by the first step that did not finish. Input selection means the fixed file rule found nothing to hand to `dials.import`.

| Step | Entries |
| --- | ---: |
| Input selection | 12 |
| dials.import | 33 |
| dials.find_spots | 8 |
| dials.index | 23 |
| dials.refine | 2 |
| dials.integrate | 4 |
| dials.symmetry | 13 |

## How to read the failures

- **Some failures come from the benchmark harness and say nothing about DIALS.** Examples are a gap in the image numbering of a sweep (reported by `dials.import` as missing images), depositions that hold fewer than ten images per sweep, and a few downloads that stopped on a missing-directory error or an incomplete rsync transfer.
- **Serial and XFEL depositions** (CXIDB, SACLA, PAL-XFEL, PLS-II) either exceed the 500 GB download cap or hold file types the rotation input rule does not select. They are recorded as they fell, mostly as input selection failures or failed downloads.
- **ESRF data portal entries** need a session login or are archived to tape, so they were not fetched.
- **Low CC½ or low completeness in a completed row is reported as measured.** "Complete" only means the script ran through `dials.merge`. No mask, resolution limit or repair was applied to any entry.

## The pipeline script

This is [tldr.sh](tldr.sh), the one script every entry is run through. Its arguments are the image files, templates or master files chosen by the fixed input rule, and they go to `dials.import` unchanged.

```bash
#!/bin/bash
# Standard DIALS benchmark pipeline.  DO NOT EDIT, DO NOT ADD OPTIONS.
#
# Usage (run from inside the entry's proc/ directory):
#     tldr.sh <dials.import arguments>
#
# Every argument is handed to dials.import unchanged (image files, templates,
# or NeXus/HDF5 master files; all sweeps of the entry go in together and are
# indexed separately).  No other step takes per-dataset options.
# nproc=24 only limits CPU use so that 8 entries can run side by side.
# The script stops at the first step that fails.
#
# Files written to the current directory, besides the normal DIALS output:
#     tldr.log    stdout+stderr of every step
#     steps.tsv   one row per step attempted: step, exit_code, seconds

set -u

if [ $# -lt 1 ]; then
  echo "usage: tldr.sh <dials.import arguments>" >&2
  exit 2
fi

exec 3>&1                 # keep the caller's stdout for the one-line verdict
exec > tldr.log 2>&1

echo "### started $(date -u +%Y-%m-%dT%H:%M:%SZ) on $(hostname) in $(pwd)"
dials.version
printf 'step\texit_code\tseconds\n' > steps.tsv

run () {
  local name=$1; shift
  local t0=$SECONDS
  echo
  echo "### $*"
  "$@"
  local rc=$?
  printf '%s\t%d\t%d\n' "$name" "$rc" "$((SECONDS - t0))" >> steps.tsv
  if [ "$rc" -ne 0 ]; then
    echo "### FAILED at $name (exit code $rc)"
    echo "FAILED at $name (exit code $rc)" >&3
    exit "$rc"
  fi
}

run import     dials.import "$@"
run find_spots dials.find_spots imported.expt nproc=24
run index      dials.index imported.expt strong.refl joint_indexing=False
run refine     dials.refine indexed.expt indexed.refl
run integrate  dials.integrate refined.expt refined.refl nproc=24
run symmetry   dials.symmetry integrated.expt integrated.refl nproc=24
run scale      dials.scale symmetrized.expt symmetrized.refl
run export     dials.export scaled.expt scaled.refl
run merge      dials.merge scaled.expt scaled.refl

echo
echo "### finished $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "COMPLETE" >&3
```

## System and software

Every entry was processed on the same machine with the same build. DIALS is the 3.31.0 release; `dials.version` reports it as DIALS 3.31.

| Item | Value |
| --- | --- |
| DIALS | 3.31 (release 3.31.0) |
| dxtbx | 3.31.0 |
| Python | 3.14.10 (numpy 2.5.4, scipy 1.18.1, h5py 3.16.0) |
| Linux | Rocky Linux 9.7 (Blue Onyx), kernel 5.14.0-611.49.1.el9_7.x86_64 |
| Hardware | 2 × AMD EPYC 9554 64-core, 224 logical CPUs, 1.5 TB RAM |
| Parallelism | nproc=24 per entry, up to 8 entries side by side |
| Run dates | 21 November 2026 |

## All datasets

Entries are in the order of the source list. Resolution, CC½, completeness and multiplicity are the overall values written by `dials.merge` for all scaled data, with no resolution cutoff. The "suggested" columns are the statistics `dials.merge` reports for the same data cut at the limit DIALS suggests, where a fit of CC½ falls to 0.3. For failed downloads the last column gives the reason.

| Entry | Status | Stopped at | Repository | Facility | Beamline | Detector | Space group | Sweeps | Images | Indexed (%) | d min (Å) | d min, suggested (Å) | CC½ | CC½, suggested | Complete (%) | Complete, suggested (%) | Multiplicity | Run time (s) | Download note |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| zenodo_15017658 | Complete |  | Zenodo | DLS | I24 | JF1M | I 2 3 | 1 | 3600 | 98.6 | 1.28 | 1.31 | 1.000 | 1.000 | 92.0 | 96.1 | 27.9 | 275 |  |
| 37AS | Complete |  | proteindiffraction.org | NSLS-II | 19-ID | EIGER2 XE 9M | C 2 2 21 | 1 | 1800 | 70.1 | 1.41 | 1.71 | 0.998 | 0.998 | 79.0 | 99.7 | 10.9 | 292 |  |
| 36IQ | Complete |  | proteindiffraction.org | ALS | 8.3.1 | PILATUS3 S 6M | P 3 2 1 | 1 | 3600 | 73.7 | 1.30 | 1.45 | 0.997 | 0.997 | 87.1 | 98.6 | 27.5 | 531 |  |
| 36GK | Complete |  | proteindiffraction.org | CLSI | 08ID-1 | EIGER X 9M | I 2 2 2 | 2 | 3600 | 92.1 | 1.37 | 2.09 | 0.997 | 0.998 | 79.3 | 100.0 | 21.9 | 1657 |  |
| 29HN | Complete |  | proteindiffraction.org | DIAMOND | I23 | PILATUS 12M | P 41 2 2 | 3 | 10800 | 48.8 | 1.80 |  | 1.000 |  | 100.0 |  | 41.3 | 992 |  |
| 21OO | Complete |  | PDBj XRDA | SPRING-8 | BL44XU | EIGER X 16M | P 31 2 1 | 1 | 1500 | 96.7 | 1.47 | 2.11 | 0.974 | 0.974 | 77.6 | 100.0 | 6.9 | 466 |  |
| 9Z55 | Complete |  | proteindiffraction.org | APS | 24-ID-E | EIGER X 16M | I 1 2 1 | 1 | 1800 | 67.3 | 1.91 | 2.91 | 0.997 | 0.996 | 67.7 | 99.3 | 6.2 | 316 |  |
| 9Z7O | Complete |  | SBGrid | APS | 24-ID-C | EIGER2 X 16M | P 1 | 1 | 1800 | 75.2 | 2.24 | 3.89 | 0.834 | 0.941 | 55.0 | 94.4 | 3.8 | 251 |  |
| 9QLK | Complete |  | Zenodo | ESRF | ID23-2 | EIGER X 9M | P 31 | 1 | 900 | 98.3 | 1.42 | 1.93 | 0.995 | 0.996 | 75.4 | 100.0 | 4.2 | 238 |  |
| 9ZLO | Complete |  | Zenodo | AUSTRALIAN SYNCHROTRON | MX2 | EIGER X 16M | P 21 21 21 | 1 | 3600 | 68.8 | 1.31 | 1.62 | 0.999 | 0.999 | 81.7 | 100.0 | 10.4 | 398 |  |
| 9YZI | Complete |  | proteindiffraction.org | ALS | 8.2.1 | EIGER X 9M | P 1 | 1 | 900 | 29.6 | 2.22 | 4.87 | 0.871 | 0.930 | 52.7 | 93.4 | 1.9 | 202 |  |
| 9Q41 | Failed | index | SBGrid | CHESS | 7B2 | PILATUS 6M |  | 1 | 900 |  |  |  |  |  |  |  |  | 52 |  |
| 9W3Y | Complete |  | proteindiffraction.org | PHOTON FACTORY | BL-1A | EIGER X 4M | P 21 21 21 | 1 | 180 | 98.4 | 1.00 | 1.25 | 0.996 | 0.998 | 86.0 | 100.0 | 5.8 | 224 |  |
| 9SNU | Complete |  | Zenodo | NSLS-II | 17-ID-1 | EIGER X 16M | I 4 2 2 | 2 | 2925 | 43.7 | 1.10 | 2.22 | 0.449 | 0.959 | 86.5 | 99.7 | 10.2 | 430 |  |
| 9PBH | Complete |  | SBGrid | SSRL | BL12-1 | EIGER2 XE 16M | P 1 2 1 | 1 | 1800 | 46.7 | 1.54 | 2.20 | 0.982 | 0.989 | 65.8 | 98.0 | 6.6 | 248 |  |
| 9XYK | Complete |  | SBGrid | NSLS-II | 17-ID-1 | EIGER X 9M | P 1 21 1 | 1 | 1800 | 67.3 | 1.15 | 1.85 | 0.945 | 0.980 | 74.3 | 100.0 | 6.0 | 507 |  |
| 9PBB | Complete |  | proteindiffraction.org | SSRL | BL12-1 | EIGER2 S 16M | C 1 2 1 | 3 | 270 | 46.9 | 1.54 | 1.92 | 0.981 | 0.992 | 72.1 | 98.8 | 6.8 | 208 |  |
| 9P7Q | Complete |  | proteindiffraction.org | SSRL | BL12-1 | EIGER2 X 16M | C 1 2 1 | 1 | 90 | 60.5 | 1.54 | 2.44 | 0.835 | 0.974 | 68.9 | 98.2 | 3.1 | 125 |  |
| 9RCU | Failed | index | PDBj XRDA | DIAMOND | I04 | EIGER2 X 16M |  | 1 | 1800 |  |  |  |  |  |  |  |  | 79 |  |
| 9TDQ | Complete |  | Other (manual) | DIAMOND | I04 | EIGER2 XE 16M | P 31 | 1 | 3600 | 98.6 | 1.17 | 1.45 | 1.000 | 1.000 | 80.4 | 100.0 | 8.5 | 624 |  |
| 9QVV | Download failed |  | Zenodo | DIAMOND | I03 | EIGER2 XE 16M |  |  |  |  |  |  |  |  |  |  |  |  | command failed (12): unzip |
| 9VX7 | Failed | index | proteindiffraction.org | PAL/PLS | 5C (4A) | EIGER X 9M |  | 1 | 360 |  |  |  |  |  |  |  |  | 14 |  |
| 9SN0 | Complete |  | Zenodo | NSLS-II | 17-ID-2 | EIGER X 16M | I 4 2 2 | 2 | 2925 | 43.7 | 1.10 | 2.22 | 0.449 | 0.959 | 86.5 | 99.7 | 10.2 | 437 |  |
| 9RCS | Failed | index | PDBj XRDA | DIAMOND | I24 | EIGER2 X CdTe 9M |  | 1 | 1440 |  |  |  |  |  |  |  |  | 42 |  |
| 9RP9 | Complete |  | proteindiffraction.org | SOLEIL | PROXIMA 1 | EIGER X 16M | C 1 2 1 | 1 | 3600 | 36.1 | 1.52 | 1.90 | 0.995 | 0.997 | 71.8 | 99.8 | 5.9 | 259 |  |
| 26UI | Complete |  | proteindiffraction.org | RRCAT INDUS-2 | PX-BL21 | RAYONIX MX-225 | P 1 21 1 | 1 | 181 | 43.7 | 1.49 | 1.57 | 0.993 | 0.993 | 68.5 | 78.5 | 3.4 | 139 |  |
| 9SKO | Complete |  | proteindiffraction.org | ESRF | MASSIF-1 | PILATUS4 X 4M | P 21 21 21 | 1 | 2120 | 84.0 | 1.09 | 1.35 | 0.995 | 0.995 | 77.6 | 98.5 | 3.3 | 273 |  |
| 9PBG | Complete |  | SBGrid | SSRL | BL12-2 | EIGER2 XE 16M | P 1 21 1 | 1 | 1800 | 42.2 | 1.36 | 1.99 | 0.982 | 0.988 | 71.1 | 98.4 | 6.3 | 328 |  |
| 9HS7 | Download failed |  | proteindiffraction.org | ALBA | XALOC | PILATUS3 S 6M |  |  |  |  |  |  |  |  |  |  |  |  | [Errno 2] No such file or directory: 'entries/9HS7/data/9hs7/other/deposit/proc/AP_B28X1_P65/Images' |
| 9PBX | Complete |  | SBGrid | SSRL | BL9-2 | PILATUS 6M | P 2 21 21 | 1 | 1800 | 98.0 | 1.19 | 1.60 | 1.000 | 1.000 | 75.5 | 99.3 | 12.2 | 408 |  |
| 9SKP | Complete |  | proteindiffraction.org | ESRF | ID30B | EIGER2 S 9M | P 2 21 21 | 1 | 3600 | 62.1 | 1.35 | 1.71 | 0.997 | 0.998 | 78.1 | 100.0 | 10.5 | 322 |  |
| 9MIN | Complete |  | SBGrid | ALS | 8.2.1 | EIGER2 S 9M | P 2 2 21 | 1 | 3175 | 40.5 | 1.39 | 1.95 | 0.997 | 0.998 | 76.6 | 99.9 | 20.0 | 571 |  |
| 9O0H | Complete |  | proteindiffraction.org | SSRL | BL12-2 | EIGER X 16M | P 21 21 21 | 1 | 1800 | 85.8 | 1.04 | 2.04 | -0.011 | 0.977 | 85.8 | 100.0 | 11.4 | 373 |  |
| 9WFH | Complete |  | PDBj XRDA | SPRING-8 | BL45XU | PILATUS 6M | C 2 2 21 | 1 | 7200 | 36.6 | 1.34 | 1.82 | 0.924 | 0.995 | 79.2 | 100.0 | 21.8 | 800 |  |
| 9QDU | Download failed |  | proteindiffraction.org | ESRF | MASSIF-1 | PILATUS 6M |  |  |  |  |  |  |  |  |  |  |  |  | [Errno 2] No such file or directory: 'entries/9QDU/data/run_01_05_datacollection_9qdu/other/run_01_05_datacollection/autoprocess/out2/Images' |
| 9I9X | Download failed |  | Other (manual) | ESRF | MASSIF-3 | EIGER X 4M |  |  |  |  |  |  |  |  |  |  |  |  | ESRF DOI dataset (23 files, ~2.2 GB) needs an ICAT/IDS session for file download; investigation embargoed until 2027-10-08, no anonymous access |
| 9T6R | Failed | index | SBGrid | ESRF | ID30B | EIGER2 X 9M |  | 1 | 900 |  |  |  |  |  |  |  |  | 28 |  |
| 9EAE | Download failed |  | SBGrid | SSRL | BL12-1 | EIGER X 16M |  |  |  |  |  |  |  |  |  |  |  |  | [Errno 2] No such file or directory: 'entries/9EAE/data/autoprocessing_autoproc_5396512_ec0881a' |
| 9H0Q | Complete |  | Zenodo | SOLEIL | PROXIMA 2 | EIGER X 16M | R 3 2 :H | 1 | 2000 | 90.3 | 1.70 | 2.00 | 0.997 | 0.998 | 81.3 | 99.6 | 7.9 | 434 |  |
| 9HGD | Download failed |  | Other (manual) | ESRF | BM07 | PILATUS 6M |  |  |  |  |  |  |  |  |  |  |  |  | ESRF dataset 1794849127 (1802 files) is ARCHIVED; IDS says restoration is disabled, anonymous access cannot restore; size unknown |
| 9CKX | Failed | import | proteindiffraction.org | ALS | 8.2.2 | PILATUS3 2M |  |  |  |  |  |  |  |  |  |  |  | 1 |  |
| 9Z73 | Download failed |  | SBGrid | SSRL | BL9-2 | EIGER X 16M |  |  |  |  |  |  |  |  |  |  |  |  | [Errno 2] No such file or directory: 'entries/9Z73/data/autoprocessing_autoproc_5392716_5cc0cba' |
| 9RLS | Failed | symmetry | Other (manual) | ESRF | MASSIF-1 | PILATUS3 6M | P 1 | 6 | 12600 | 38.8 |  |  |  |  |  |  |  | 1420 |  |
| 9NB0 | Complete |  | proteindiffraction.org | ALS | 8.2.1 | ADSC QUANTUM 315r | I 1 2 1 | 1 | 900 | 81.5 | 2.24 | 2.85 | 0.999 | 0.999 | 66.6 | 98.5 | 3.1 | 130 |  |
| 9UOA | Complete |  | proteindiffraction.org | PHOTON FACTORY | BL-17A | EIGER X 4M | P 41 21 2 | 1 | 720 | 21.9 | 1.49 | 1.69 | 0.995 | 0.998 | 83.2 | 98.4 | 18.8 | 269 |  |
| 9HG3 | Complete |  | proteindiffraction.org | BESSY | 14.1 | PILATUS3 S 6M | P 1 21 1 | 1 | 3600 | 83.5 | 1.38 | 2.16 | 0.993 | 0.997 | 71.3 | 99.3 | 6.0 | 868 |  |
| 8ZUS | Failed | index | PDBj XRDA | SPRING-8 | BL41XU | EIGER X 16M |  | 1 | 360 |  |  |  |  |  |  |  |  | 33 |  |
| 9KHR | Complete |  | Zenodo | RRCAT INDUS-2 | PX-BL21 | MAR CCD 165 mm | P 21 21 21 | 1 | 180 | 77.0 | 1.24 | 1.44 | 0.992 | 0.995 | 80.7 | 99.3 | 5.9 | 133 |  |
| 9LXL | Failed | index | Zenodo | SSRF | BL17UM | EIGER2 S 16M |  | 1 | 2000 |  |  |  |  |  |  |  |  | 59 |  |
| 9WVU | Complete |  | proteindiffraction.org | PHOTON FACTORY | BL-5A | PILATUS3 6M | R 3 2 :H | 1 | 360 | 97.3 | 1.77 | 2.09 | 0.999 | 0.999 | 84.3 | 99.7 | 7.2 | 474 |  |
| 9CJ9 | Complete |  | SBGrid | ESRF | MASSIF-3 | EIGER X 9M | C 1 2 1 | 1 | 3600 | 9.8 | 1.46 | 2.03 | 0.675 | 0.787 | 55.9 | 89.3 | 6.0 | 1451 |  |
| 22LX | Complete |  | PDBj XRDA | PHOTON FACTORY | AR-NE3A | PILATUS 2M-F | I 1 2 1 | 1 | 720 | 52.8 | 1.34 | 2.94 | 0.351 | 0.384 | 73.5 | 99.9 | 3.0 | 426 |  |
| 9OJ3 | Complete |  | proteindiffraction.org | ALS | 2.0.1 | PILATUS 6M | P 21 21 21 | 1 | 720 | 78.7 | 1.30 | 1.33 | 0.994 | 0.994 | 80.9 | 85.1 | 5.1 | 255 |  |
| 9G3K | Complete |  | Zenodo | SOLEIL | PROXIMA 2 | EIGER X 9M | P 1 21 1 | 1 | 3600 | 70.7 | 1.04 | 1.07 | 0.998 | 0.998 | 78.5 | 84.4 | 6.0 | 486 |  |
| 9S04 | Complete |  | Other (manual) | MAX IV | BioMAX | EIGER X 16M | P 21 2 21 | 1 | 1800 | 99.1 | 1.23 | 1.42 | 0.999 | 0.999 | 80.9 | 98.9 | 10.7 | 1321 |  |
| 9S01 | Complete |  | Other (manual) | MAX IV | BioMAX | EIGER2 X 16M | P 21 2 21 | 2 | 1802 | 98.7 | 1.11 | 1.43 | 0.999 | 0.999 | 82.6 | 100.0 | 11.0 | 1502 |  |
| 9DBT | Failed | refine | proteindiffraction.org | ALS | 5.0.1 | PILATUS3 2M | P 1 | 2 | 1800 | 96.9 |  |  |  |  |  |  |  | 210 |  |
| 9CUN | Download failed |  | proteindiffraction.org | ALBA | XALOC | PILATUS3 6M |  |  |  |  |  |  |  |  |  |  |  |  | HTTP Error 404: Not Found |
| 9Z1A | Complete |  | proteindiffraction.org | ALS | 8.2.2 | PILATUS 2M | I 1 2 1 | 1 | 720 | 34.4 | 2.01 | 2.80 | 0.967 | 0.967 | 68.1 | 97.9 | 3.0 | 90 |  |
| 9YZA | Complete |  | proteindiffraction.org | ALS | 8.2.2 | EIGER X 9M | I 1 2 1 | 1 | 720 | 68.6 | 2.02 | 2.88 | 0.994 | 0.994 | 65.8 | 98.4 | 3.2 | 88 |  |
| 8R5R | Complete |  | proteindiffraction.org | ESRF | ID23-1 | PILATUS 6M | C 1 2 1 | 1 | 1080 | 40.9 | 1.69 | 3.19 | 0.706 | 0.812 | 65.6 | 99.9 | 4.6 | 815 |  |
| 9GDJ | Download failed |  | Other (manual) | ESRF | ID23-1 | EIGER2 X CdTe 16M |  |  |  |  |  |  |  |  |  |  |  |  | ESRF DOI dataset (run_03_datacollection, ID23-1); file listing/download via icatplus needs a session login, no public anonymous access found |
| 8R5Q | Complete |  | proteindiffraction.org | SLS | X06DA | PILATUS 2M-F | P 21 21 21 | 1 | 720 | 64.6 | 1.69 | 2.59 | 0.984 | 0.983 | 70.5 | 100.0 | 5.8 | 335 |  |
| 9QZT | Download failed |  | Other (manual) | EUROPEAN XFEL | SPB/SFX | AGIPD |  |  |  |  |  |  |  |  |  |  |  |  | raw deposition (CXIDB 224, 13 runs r0076-r0088, ~2900 h5 files) is ~28 TB, over 500 GB limit |
| 9HW6 | Complete |  | Other (manual) | ESRF | MASSIF-1 | PILATUS3 2M | P 1 21 1 | 1 | 900 | 43.9 | 1.86 | 2.53 | 0.955 | 0.963 | 60.6 | 99.3 | 3.1 | 158 |  |
| 8XTF | Complete |  | SBGrid | SSRF | BL02U1 | EIGER2 S 9M | I 1 2 1 | 1 | 360 | 91.7 | 1.21 | 2.20 | 0.201 | 0.965 | 67.1 | 98.9 | 6.1 | 430 |  |
| 9NMV | Complete |  | SBGrid | ALS | 2.0.1 | PILATUS3 6M | C 1 2 1 | 1 | 1800 | 60.5 | 1.59 | 1.93 | 0.996 | 0.996 | 70.3 | 97.3 | 5.6 | 333 |  |
| 9JZO | Complete |  | proteindiffraction.org | PAL/PLS | 11C | PILATUS3 6M | P 1 | 1 | 360 | 60.5 | 1.15 |  | 0.994 |  | 59.1 |  | 3.7 | 213 |  |
| 8V23 | Complete |  | proteindiffraction.org | ALS | 4.2.2 | RDI CMOS 8M | P 6 | 1 | 1440 | 86.4 | 1.22 | 1.27 | 0.997 | 0.998 | 87.6 | 94.8 | 15.0 | 664 |  |
| 8W6K | Failed | Input selection | proteindiffraction.org | SSRF | BL03HB | PILATUS 2M |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 8RNZ | Failed | index | Zenodo | ESRF | ID23-1 | EIGER2 S 16M |  | 1 | 3600 |  |  |  |  |  |  |  |  | 296 |  |
| 8WNA | Complete |  | PDBj XRDA | PHOTON FACTORY | BL-5A | PILATUS3 S 2M | P 21 21 21 | 1 | 720 | 96.5 | 1.01 |  | 1.000 |  | 82.2 |  | 5.8 | 594 |  |
| 8JQQ | Complete |  | PDBj XRDA | PHOTON FACTORY | BL-5A | PILATUS3 S 6M | P 21 2 21 | 1 | 720 | 50.6 | 1.39 | 1.69 | 0.997 | 0.998 | 81.0 | 100.0 | 5.1 | 197 |  |
| 8WN6 | Failed | import | PDBj XRDA | SPRING-8 | BL45XU | PILATUS3 6M |  |  |  |  |  |  |  |  |  |  |  | 2 |  |
| 9FM0 | Download failed |  | Other (manual) | ESRF | MASSIF-1 | PILATUS 2M |  |  |  |  |  |  |  |  |  |  |  |  | ESRF DOI 10.15151/ESRF-DC-1732137788 (1 dataset, S4P5D6-B14-B2-5): file download via icatplus needs a session/login; no public anonymous download found; size unknown |
| 8T55 | Complete |  | proteindiffraction.org | APS | 24-ID-E | EIGER2 X 16M | P 21 21 2 | 1 | 700 | 67.5 | 1.54 | 1.96 | 0.999 | 0.999 | 65.4 | 98.0 | 7.6 | 279 |  |
| 9EWK | Complete |  | MX-RDR | APS | 19-ID | PILATUS3 X 6M | P 1 | 5 | 3677 | 90.2 | 0.38 | 0.70 | 0.994 | 0.998 | 82.7 | 99.8 | 6.0 | 691 |  |
| 8XTE | Failed | index | SBGrid | SSRF | BL19U1 | PILATUS 6M |  | 1 | 360 |  |  |  |  |  |  |  |  | 16 |  |
| 8TCA | Complete |  | proteindiffraction.org | APS | 31-ID | PILATUS3 S 6M | P 1 | 3 | 1030 | 47.6 | 1.26 | 2.45 | 0.005 | 0.772 | 58.2 | 89.7 | 1.9 | 245 |  |
| 9C14 | Complete |  | SBGrid | APS | 21-ID-D | EIGER X 9M | P 41 21 2 | 3 | 1802 | 91.0 | 1.32 | 1.46 | 0.977 | 0.998 | 91.8 | 100.0 | 20.7 | 219 |  |
| 8OQH | Failed | index | PDBj XRDA | APS | 24-ID-C | EIGER X 16M |  | 1 | 1800 |  |  |  |  |  |  |  |  | 127 |  |
| 9M7D | Download failed |  | PDBj XRDA | PHOTON FACTORY | BL-17A | EIGER X 16M |  |  |  |  |  |  |  |  |  |  |  |  | command failed (23): rsync |
| 9LPX | Complete |  | PDBj XRDA | PHOTON FACTORY | BL-5A | PILATUS 6M | P 21 21 21 | 1 | 180 | 92.4 | 0.89 | 1.10 | 0.997 | 0.997 | 80.5 | 96.2 | 6.3 | 369 |  |
| 9PUO | Complete |  | proteindiffraction.org | APS | 19-ID | PILATUS3 6M | P 1 | 1 | 400 | 35.1 | 1.85 | 2.89 | 0.480 | 0.879 | 55.4 | 93.1 | 2.0 | 77 |  |
| 8PQA | Complete |  | proteindiffraction.org | SLS | X10SA | EIGER2 X 16M | P 21 21 21 | 1 | 3600 | 79.2 | 1.22 | 1.44 | 0.999 | 0.999 | 77.0 | 98.9 | 11.7 | 577 |  |
| 8V9Q | Complete |  | SBGrid | APS | 22-BM | RAYONIX MX300-HS | P 1 | 1 | 800 | 21.6 | 1.64 | 3.97 | 0.225 | 0.313 | 55.7 | 91.2 | 2.1 | 796 |  |
| 9QBT | Download failed |  | proteindiffraction.org | SLS | X06SA | EIGER X 16M |  |  |  |  |  |  |  |  |  |  |  |  | [Errno 2] No such file or directory: 'entries/9QBT/data/collectKEAP-P6-1_1_data_000001_9qbt/other/autoprocess/out1/H5ToXds' |
| 8OTM | Complete |  | PDBj XRDA | ALBA | XALOC | PILATUS 6M | P 1 21 1 | 1 | 3600 | 94.8 | 1.31 | 1.48 | 0.999 | 0.999 | 71.4 | 91.7 | 6.0 | 672 |  |
| 8SO5 | Complete |  | proteindiffraction.org | APS | 23-ID-D | PILATUS3 6M | P 1 21 1 | 1 | 500 | 68.5 | 1.14 | 1.76 | 0.951 | 0.980 | 77.5 | 100.0 | 4.1 | 327 |  |
| 8RCC | Download failed |  | PDBj XRDA | ESRF | MASSIF-3 | EIGER R 4M |  |  |  |  |  |  |  |  |  |  |  |  | command failed (23): rsync |
| 8UFO | Complete |  | proteindiffraction.org | APS | 23-ID-D | PILATUS 6M | P 1 | 1 | 1800 | 18.0 | 1.20 |  | 0.944 |  | 67.2 |  | 3.2 | 460 |  |
| 9Q1L | Download failed |  | Zenodo | APS | 22-ID | EIGER2 X 16M |  |  |  |  |  |  |  |  |  |  |  |  | HTTP Error 404: NOT FOUND |
| 8WZV | Failed | Input selection | Other (manual) | SACLA | BL2 | MPCCD |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 8FG7 | Complete |  | proteindiffraction.org | ALS | 8.3.1 | PILATUS3 6M | P 21 21 21 | 1 | 720 | 49.0 | 1.30 | 1.57 | 0.995 | 0.996 | 75.4 | 99.3 | 11.9 | 168 |  |
| 8T7R | Complete |  | proteindiffraction.org | APS | 22-ID | EIGER X 16M | P 1 | 1 | 800 | 70.8 | 2.06 | 4.52 | 0.221 | 0.417 | 53.4 | 91.5 | 2.1 | 4762 |  |
| 9CHW | Complete |  | SBGrid | APS | 21-ID-F | MAR CCD 300 mm | P 61 | 1 | 300 | 55.8 | 1.60 |  | 0.991 |  | 72.5 |  | 3.1 | 140 |  |
| 8EPS | Complete |  | proteindiffraction.org | ALS | 8.2.2 | PILATUS3 S 2M | P 1 | 1 | 440 | 76.4 | 1.64 | 1.86 | 0.917 | 0.917 | 59.7 | 80.9 | 2.2 | 157 |  |
| 9WFI | Complete |  | proteindiffraction.org | SSRF | BL18U1 | MARMOSAIC 225 mm CCD | P 1 | 1 | 360 | 9.4 | 1.16 |  | 0.090 |  | 54.7 |  | 1.4 | 945 |  |
| 8EGN | Complete |  | proteindiffraction.org | CLSI | 08B1-1 | PILATUS3 6M | P 21 21 21 | 1 | 720 | 88.6 | 1.53 | 1.68 | 0.999 | 0.999 | 80.6 | 95.2 | 5.1 | 175 |  |
| 8EGM | Complete |  | proteindiffraction.org | APS | 21-ID-F | RAYONIX MX-300 | I 1 2 1 | 1 | 220 | 96.5 | 1.54 | 1.91 | 0.992 | 0.992 | 70.4 | 99.1 | 4.0 | 347 |  |
| 8QJ5 | Complete |  | proteindiffraction.org | ELETTRA | 11.2C | PILATUS 6M | P 1 21 1 | 1 | 720 | 66.7 | 1.12 | 1.42 | 0.995 | 0.996 | 76.2 | 100.0 | 5.7 | 386 |  |
| 8BXT | Complete |  | Zenodo | DIAMOND | I04 | EIGER X 16M | P 61 | 1 | 720 | 98.1 | 1.18 | 1.46 | 0.993 | 0.998 | 88.0 | 100.0 | 14.9 | 457 |  |
| 8UDN | Complete |  | proteindiffraction.org | APS | 23-ID-B | EIGER X 16M | P 4 | 1 | 1440 | 94.4 | 1.19 |  | 0.999 |  | 76.2 |  | 12.3 | 259 |  |
| 8RCB | Download failed |  | PDBj XRDA | ESRF | ID30B | PILATUS3 6M |  |  |  |  |  |  |  |  |  |  |  |  | command failed (23): rsync |
| 8VKB | Failed | index | proteindiffraction.org | ALS | 8.2.2 | ADSC QUANTUM 315 |  | 1 | 220 |  |  |  |  |  |  |  |  | 19 |  |
| 9J6N | Complete |  | PDBj XRDA | PHOTON FACTORY | AR-NW12A | PILATUS 2M | P 1 21 1 | 1 | 720 | 95.4 | 1.22 | 1.42 | 0.994 | 0.994 | 68.8 | 93.6 | 3.3 | 184 |  |
| 8IC7 | Complete |  | PDBj XRDA | PHOTON FACTORY | AR-NW12A | PILATUS3 2M | P 1 21 1 | 1 | 720 | 90.9 | 1.05 | 1.19 | 0.989 | 0.989 | 79.3 | 98.8 | 2.9 | 539 |  |
| 8U09 | Failed | find_spots | proteindiffraction.org | AUSTRALIAN SYNCHROTRON | MX1 | EIGER2 X 9M |  | 1 | 3600 |  |  |  |  |  |  |  |  | 4 |  |
| 9CN2 | Complete |  | proteindiffraction.org | APS | 21-ID-D | PILATUS3 6M | P 41 3 2 | 1 | 360 | 98.1 | 2.05 | 2.42 | 0.998 | 0.999 | 92.0 | 100.0 | 48.7 | 529 |  |
| 8FT8 | Complete |  | proteindiffraction.org | SSRL | BL12-2 | PILATUS 6M | P 61 | 1 | 1800 | 94.7 | 1.27 | 1.41 | 0.999 | 0.999 | 77.0 | 92.3 | 17.4 | 472 |  |
| 8A9D | Download failed |  | Zenodo | DIAMOND | VMXi | EIGER2 X 4M |  |  |  |  |  |  |  |  |  |  |  |  | Zenodo 6772044 holds only scaled.mtz (0.57 MB); no raw images in deposition |
| 8B1N | Complete |  | proteindiffraction.org | BESSY | 14.2 | PILATUS3 2M | C 2 2 21 | 1 | 2400 | 37.9 | 1.29 | 1.81 | 0.994 | 0.996 | 81.3 | 100.0 | 6.9 | 196 |  |
| 8PQC | Complete |  | proteindiffraction.org | ESRF | ID23-2 | PILATUS3 X 2M | P 1 | 1 | 3600 | 7.2 | 1.40 | 1.67 | 0.689 | 0.676 | 46.2 | 68.9 | 2.1 | 2105 |  |
| 9VZR | Download failed |  | PDBj XRDA | NSRRC | TPS 05A | RAYONIX MX300-HS |  |  |  |  |  |  |  |  |  |  |  |  | command failed (23): rsync |
| 7XRC | Download failed |  | PDBj XRDA | BESSY | 14.1 | PILATUS3 6M |  |  |  |  |  |  |  |  |  |  |  |  | command failed (23): rsync |
| 8K9N | Failed | index | PDBj XRDA | SPRING-8 | BL41XU | EIGER2 X 4M |  | 1 | 1801 |  |  |  |  |  |  |  |  | 46 |  |
| 7U0O | Complete |  | proteindiffraction.org | APS | 21-ID-F | RAYONIX MX300HE | C 1 2 1 | 1 | 280 | 58.3 | 1.40 | 1.69 | 0.994 | 0.994 | 69.7 | 97.0 | 5.1 | 206 |  |
| 9RLQ | Failed | symmetry | Other (manual) | ESRF | MASSIF-1 | PILATUS3 S 6M | P 1 | 6 | 12600 | 38.8 |  |  |  |  |  |  |  | 1552 |  |
| 7Z8Y | Complete |  | proteindiffraction.org | DIAMOND | I24 | PILATUS3 6M | P 63 | 1 | 3600 | 41.7 | 1.17 | 2.18 | 0.464 | 0.987 | 87.2 | 100.0 | 14.4 | 757 |  |
| 9ENH | Complete |  | SBGrid | ESRF | ID23-1 | PILATUS 6M-F | C 2 2 21 | 1 | 2400 | 29.7 | 1.89 | 2.24 | 0.962 | 0.996 | 75.4 | 97.8 | 10.3 | 1223 |  |
| 7UDI | Failed | import | Zenodo | CLSI | 08B1-1 | PILATUS3 S 6M |  |  |  |  |  |  |  |  |  |  |  | 2 |  |
| 8UFN | Failed | import | proteindiffraction.org | ALS | 5.0.1 | PILATUS 2M |  |  |  |  |  |  |  |  |  |  |  | 3 |  |
| 8DA3 | Complete |  | SBGrid | ALS | 5.0.2 | PILATUS3 6M | P 21 21 21 | 1 | 1800 | 81.3 | 0.98 | 1.03 | 0.999 | 0.999 | 87.8 | 97.5 | 10.8 | 458 |  |
| 7TM9 | Complete |  | proteindiffraction.org | NSLS-II | 19-ID | PILATUS 6M | P 1 2 1 | 1 | 720 | 14.6 | 1.13 | 2.46 | 0.634 | 0.604 | 70.0 | 98.9 | 3.1 | 699 |  |
| 8R0D | Complete |  | proteindiffraction.org | BESSY | 14.2 | PILATUS 2M | I 2 2 2 | 1 | 1500 | 47.1 | 1.29 | 1.66 | 0.989 | 0.989 | 76.8 | 99.8 | 4.6 | 213 |  |
| 7WDA | Complete |  | proteindiffraction.org | ESRF | ID30B | PILATUS 6M | C 2 2 21 | 1 | 720 | 51.9 | 1.48 | 1.85 | 0.995 | 0.997 | 79.5 | 100.0 | 10.1 | 475 |  |
| 8UPA | Complete |  | SBGrid | APS | 23-ID-D | EIGER X 16M | I 2 3 | 1 | 450 | 64.0 | 1.76 | 2.97 | 0.392 | 0.971 | 78.5 | 100.0 | 7.8 | 139 |  |
| 8OIA | Download failed |  | Other (manual) | ESRF | ID23-2 | PILATUS3 2M |  |  |  |  |  |  |  |  |  |  |  |  | ESRF data portal: 1 dataset, 7200 cbf; download needs anonymous ICAT+ session login, blocked by permission, not fetched |
| 8U1E | Complete |  | proteindiffraction.org | NSLS-II | 19-ID | EIGER X 9M | P 41 21 2 | 1 | 1800 | 97.7 | 1.13 | 1.40 | 0.999 | 1.000 | 81.1 | 100.0 | 21.6 | 752 |  |
| 7R59 | Failed | import | Other (manual) | DIAMOND | I03 | EIGER X 16M |  |  |  |  |  |  |  |  |  |  |  | 2 |  |
| 8GI4 | Complete |  | SBGrid | APS | 24-ID-E | PILATUS 6M-F | P 1 21 1 | 4 | 4320 | 44.9 | 1.29 | 1.89 | 0.997 | 0.997 | 77.2 | 100.0 | 15.7 | 1650 |  |
| 9MYP | Complete |  | SBGrid | APS | 24-ID-C | PILATUS 6M | P 21 21 21 | 1 | 450 | 75.2 | 1.35 | 1.63 | 0.993 | 0.996 | 83.8 | 99.6 | 2.9 | 166 |  |
| 9MUG | Complete |  | SBGrid | APS | 24-ID-C | PILATUS 6M-F | P 21 2 21 | 1 | 900 | 24.1 | 1.36 | 1.37 | 0.994 | 0.993 | 84.9 | 88.0 | 5.4 | 258 |  |
| 7V0J | Failed | import | proteindiffraction.org | APS | 21-ID-G | RAYONIX MX-300 |  |  |  |  |  |  |  |  |  |  |  | 1 |  |
| 8G28 | Complete |  | proteindiffraction.org | APS | 21-ID-G | MARMOSAIC 300 mm CCD | P 61 2 2 | 1 | 350 | 98.7 | 1.05 | 1.20 | 0.999 | 0.999 | 91.5 | 100.0 | 18.5 | 507 |  |
| 7Z7U | Complete |  | Zenodo | BESSY | 14.1 | PILATUS 6M | P 41 21 2 | 1 | 3600 | 68.3 | 1.41 | 2.39 | 0.982 | 0.982 | 88.1 | 100.0 | 17.3 | 127 |  |
| 7S87 | Complete |  | proteindiffraction.org | APS | 21-ID-E | EIGER X 16M | C 2 2 2 | 1 | 360 | 82.3 | 1.72 | 2.24 | 0.985 | 0.986 | 63.5 | 97.9 | 6.6 | 168 |  |
| 8F4F | Download failed |  | Other (manual) | SLAC LCLS | MFX | RAYONIX MX340-HS |  |  |  |  |  |  |  |  |  |  |  |  | CXIDB 215 raw data is LCLS XTC (20 GiB files), ~4.1 TB for mfxlx4319 alone, ~4.8 TB for mfxlu3417; far above 500 GB limit |
| 8GCA | Complete |  | proteindiffraction.org | ALS | 8.3.1 | PILATUS 6M | P 21 21 2 | 1 | 901 | 64.2 | 1.18 | 1.44 | 0.995 | 0.996 | 80.4 | 99.9 | 5.9 | 280 |  |
| 7PWU | Complete |  | Other (manual) | MAX IV | BioMAX | PILATUS 6M | P 1 | 2 | 3604 | 16.5 | 1.11 | 1.79 | 0.924 | 0.976 | 64.7 | 97.5 | 3.5 | 962 |  |
| 7SY9 | Complete |  | proteindiffraction.org | ALS | 5.0.1 | PILATUS3 6M | P 6 2 2 | 1 | 720 | 85.6 | 1.72 | 2.13 | 0.996 | 0.996 | 85.8 | 100.0 | 11.3 | 307 |  |
| 8E60 | Complete |  | SBGrid | APS | 23-ID-B | EIGER2 X 16M | P 2 21 21 | 1 | 450 | 74.8 | 1.62 | 2.28 | 0.983 | 0.987 | 68.4 | 95.8 | 3.1 | 108 |  |
| 5SP6 | Complete |  | proteindiffraction.org | SSRL | BL12-2 | PILATUS3 6M | P 4 | 1 | 900 | 83.7 | 0.80 | 1.05 | 0.995 | 0.995 | 82.2 | 99.7 | 5.8 | 354 |  |
| 9EEZ | Failed | index | proteindiffraction.org | CHESS | 7B2 | EIGER2 X 16M |  | 1 | 1800 |  |  |  |  |  |  |  |  | 61 |  |
| 7Z1Y | Failed | import | Other (manual) | ESRF | MASSIF-1 | EIGER X 16M |  |  |  |  |  |  |  |  |  |  |  | 1 |  |
| 7RJJ | Complete |  | proteindiffraction.org | APS | 21-ID-F | MARMOSAIC 300 mm CCD | P 61 2 2 | 1 | 300 | 84.4 | 1.45 | 1.76 | 0.973 | 0.973 | 90.9 | 99.5 | 13.5 | 166 |  |
| 7S5E | Complete |  | proteindiffraction.org | APS | 21-ID-F | RAYONIX MX300-HS | P 1 21 1 | 1 | 180 | 66.6 | 1.62 | 1.86 | 0.980 | 0.979 | 62.5 | 85.5 | 3.6 | 196 |  |
| 8SLU | Failed | index | proteindiffraction.org | CHESS | 7B2 | EIGER2 S 16M |  | 1 | 900 |  |  |  |  |  |  |  |  | 40 |  |
| 9ENT | Download failed |  | Other (manual) | ESRF | ID30B | EIGER X 9M |  |  |  |  |  |  |  |  |  |  |  |  | ESRF DOI data (233 datasets, ~144 GB, 58613 files) is ARCHIVED; IDS refuses download (DataNotOnlineException, restoration disabled; needs ticket/credentials) |
| 9C74 | Complete |  | proteindiffraction.org | APS | 24-ID-E | ADSC QUANTUM 315 | I 1 2 1 | 1 | 900 | 88.0 | 1.13 | 1.21 | 0.996 | 0.996 | 76.0 | 88.8 | 3.1 | 184 |  |
| 7AV4 | Download failed |  | Other (manual) | SLS | X10SA | EIGER X 16M |  |  |  |  |  |  |  |  |  |  |  |  | CXIDB 177 (DOI 10.11577/1775333) holds only LCLS CXI CSPAD hit-finding patterns (LT59, shared by 7R34); no SLS X10SA EIGER raw images for 7AV4 |
| 7SGW | Failed | index | proteindiffraction.org | APS | 19-BM | PILATUS3 X 6M |  | 1 | 180 |  |  |  |  |  |  |  |  | 22 |  |
| 7LGP | Failed | index | proteindiffraction.org | APS | 19-BM | ADSC QUANTUM 315r |  | 1 | 260 |  |  |  |  |  |  |  |  | 26 |  |
| 7MJB | Complete |  | proteindiffraction.org | APS | 19-ID | PILATUS 6M | P 21 21 2 | 1 | 360 | 97.5 | 1.19 | 1.58 | 0.999 | 0.999 | 83.2 | 100.0 | 10.6 | 279 |  |
| 8AGQ | Failed | import | proteindiffraction.org | SLS | X06DA | PILATUS 2M |  |  |  |  |  |  |  |  |  |  |  | 1 |  |
| 7QT8 | Failed | symmetry | Zenodo | DIAMOND | I24 | PILATUS 6M-F | P 1 | 42 | 8400 | 85.6 |  |  |  |  |  |  |  | 1217 |  |
| 9FMP | Complete |  | proteindiffraction.org | BESSY | 14.1 | PILATUS3 2M | P 21 21 21 | 1 | 3600 | 45.8 | 2.03 | 2.57 | 0.951 | 0.978 | 78.8 | 100.0 | 9.8 | 173 |  |
| 8DYE | Complete |  | SBGrid | APS | 21-ID-F | MARMOSAIC 225 mm CCD | P 21 2 21 | 1 | 525 | 88.7 | 1.02 | 1.44 | 0.994 | 0.998 | 80.4 | 99.7 | 7.5 | 513 |  |
| 5RG0 | Complete |  | Zenodo | DIAMOND | I04-1 | PILATUS 6M | I 1 2 1 | 1 | 400 | 53.0 | 1.19 | 1.70 | 0.988 | 0.992 | 75.1 | 99.9 | 2.8 | 123 |  |
| 6W4B | Complete |  | proteindiffraction.org | APS | 19-BM | PILATUS3 S 6M | P 1 | 1 | 120 | 12.0 | 1.98 |  | 0.116 |  | 44.6 |  | 1.6 | 830 |  |
| 7PWP | Complete |  | Other (manual) | DIAMOND | I03 | PILATUS 6M | P 1 | 2 | 3604 | 16.5 | 1.11 | 1.79 | 0.924 | 0.976 | 64.7 | 97.5 | 3.5 | 965 |  |
| 6Z5F | Complete |  | Other (manual) | DIAMOND | I03 | EIGER2 X 16M | P 21 21 21 | 1 | 1800 | 78.1 | 1.49 | 2.15 | 0.997 | 0.997 | 76.7 | 100.0 | 5.5 | 496 |  |
| 7YZX | Complete |  | proteindiffraction.org | DIAMOND | I24 | PILATUS 6M | P 63 2 2 | 1 | 1300 | 91.6 | 1.31 | 1.99 | 0.994 | 0.996 | 81.9 | 100.0 | 10.3 | 545 |  |
| 7PWW | Complete |  | Other (manual) | DIAMOND | I03 | PILATUS3 6M | P 1 | 2 | 3604 | 16.5 | 1.11 | 1.79 | 0.924 | 0.976 | 64.7 | 97.5 | 3.5 | 981 |  |
| 9EP5 | Complete |  | Zenodo | DIAMOND | I04-1 | EIGER X 9M | C 2 2 2 | 1 | 3600 | 70.4 | 1.03 | 1.27 | 0.994 | 0.996 | 80.5 | 99.9 | 10.0 | 435 |  |
| 7KDS | Complete |  | proteindiffraction.org | CLSI | 08ID-1 | PILATUS3 6M | P 41 3 2 | 1 | 900 | 99.2 | 2.14 | 2.68 | 0.999 | 0.999 | 92.3 | 100.0 | 23.7 | 360 |  |
| 7YXA | Download failed |  | Other (manual) | PAL-XFEL | NCI | RAYONIX MX225-HS |  |  |  |  |  |  |  |  |  |  |  |  | CXIDB 196 raw images are 53 .cxi files totalling ~971 GB (>500 GB limit) |
| 7OU1 | Complete |  | MX-RDR | BESSY | 14.3 | MARMOSAIC 225 mm CCD | P 1 21 1 | 1 | 200 | 57.0 | 1.28 | 1.47 | 0.961 | 0.962 | 71.3 | 94.3 | 3.6 | 289 |  |
| 7CLJ | Complete |  | Zenodo | SPRING-8 | BL32XU | EIGER X 9M | P 1 | 4 | 7900 | 14.3 | 1.43 | 3.37 | 0.042 | 0.569 | 70.3 | 98.3 | 3.4 | 1910 |  |
| 7DTB | Failed | Input selection | Other (manual) | PAL/PLS | 11C | PILATUS 6M |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 7KMJ | Complete |  | SBGrid | SSRL | BL9-2 | PILATUS3 S 6M | P 21 21 2 | 1 | 1800 | 38.2 | 1.03 | 1.09 | 0.998 | 0.997 | 85.4 | 95.8 | 10.9 | 361 |  |
| 6YRZ | Download failed |  | Other (manual) | SOLEIL | PROXIMA 1 | EIGER X 4M |  |  |  |  |  |  |  |  |  |  |  |  | shares CXIDB 177 with 7AV4: deposition holds only LCLS CSPAD hit-finding patterns; no synchrotron EIGER raw images for this entry |
| 7DBU | Complete |  | PDBj XRDA | AichiSR | BL2S1 | ADSC QUANTUM 270 | P 1 | 1 | 720 | 79.3 | 1.38 | 1.43 | 0.976 | 0.975 | 64.8 | 70.5 | 7.8 | 166 |  |
| 8F4J | Download failed |  | Other (manual) | SACLA | BL2 | RAYONIX MX300-HS |  |  |  |  |  |  |  |  |  |  |  |  | shares CXIDB 215 with 8F4F: raw data is LCLS XTC, ~4.1 TB and ~4.8 TB, far above 500 GB limit; XFEL serial data |
| 7TPB | Complete |  | SBGrid | APS | 24-ID-E | EIGER2 S 16M | C 1 2 1 | 2 | 960 | 92.6 | 1.92 | 3.08 | 0.980 | 0.984 | 67.6 | 100.0 | 5.7 | 197 |  |
| 7RKB | Complete |  | proteindiffraction.org | APS | 21-ID-E | MARMOSAIC 300 mm CCD | P 41 21 2 | 1 | 480 | 70.9 | 1.80 | 2.17 | 0.997 | 0.998 | 78.5 | 99.2 | 20.6 | 160 |  |
| 7R7J | Complete |  | SBGrid | APS | 21-ID-D | MARMOSAIC 300 mm CCD | P 1 | 1 | 360 | 72.3 | 1.54 | 2.02 | 0.996 | 0.997 | 59.8 | 98.1 | 3.7 | 178 |  |
| 6VZQ | Complete |  | SBGrid | ALS | 5.0.2 | PILATUS3 S 6M | P 21 21 21 | 1 | 360 | 80.8 | 1.78 | 2.15 | 0.982 | 0.990 | 80.0 | 100.0 | 9.6 | 235 |  |
| 6UCA | Complete |  | proteindiffraction.org | ALS | 5.0.2 | PILATUS 6M | P 2 21 21 | 1 | 400 | 91.4 | 2.09 | 2.75 | 0.950 | 0.951 | 75.7 | 99.9 | 4.7 | 220 |  |
| 7Z41 | Failed | import | Other (manual) | DIAMOND | I04 | PILATUS 6M |  |  |  |  |  |  |  |  |  |  |  | 2 |  |
| 7O5K | Download failed |  | Other (manual) | SwissFEL ARAMIS | ESA | PSI JUNGFRAU 16M |  |  |  |  |  |  |  |  |  |  |  |  | CXIDB 180 raw data ~27.6 TB total (smallest dataset thaumatin10 ~6.4 TB), exceeds 500 GB limit |
| 6P8S | Complete |  | SBGrid | SSRL | BL9-2 | PILATUS3 6M | C 2 2 21 | 1 | 1350 | 65.9 | 1.68 | 1.80 | 0.996 | 0.996 | 70.7 | 83.5 | 8.7 | 173 |  |
| 6PTQ | Failed | Input selection | Other (manual) | SACLA | BL3 | MPCCD |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 9HG1 | Complete |  | proteindiffraction.org | BESSY | 14.3 | PILATUS 6M | P 1 | 2 | 7200 | 71.6 | 2.02 | 2.06 | 0.905 | 0.911 | 75.9 | 80.7 | 6.1 | 1016 |  |
| 6TPI | Complete |  | Zenodo | DIAMOND | I04-1 | PILATUS 6M-F | P 21 21 21 | 1 | 720 | 92.2 | 1.39 | 1.89 | 0.999 | 1.000 | 78.2 | 100.0 | 9.0 | 280 |  |
| 7CVM | Failed | Input selection | Other (manual) | PAL/PLS | 11C | PSI PILATUS 6M |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 6KCD | Failed | Input selection | Other (manual) | PAL/PLS | 11C | PILATUS3 X 6M |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 6P8U | Complete |  | SBGrid | APS | 24-ID-C | PILATUS3 6M | I 1 2 1 | 1 | 900 | 50.1 | 1.25 | 1.73 | 0.986 | 0.986 | 68.7 | 97.9 | 3.0 | 139 |  |
| 9RP2 | Complete |  | proteindiffraction.org | BESSY | 14.2 | PILATUS3 S 2M | C 2 2 21 | 1 | 1800 | 75.4 | 1.14 | 1.65 | 0.971 | 0.987 | 79.7 | 99.8 | 5.8 | 118 |  |
| 6O6D | Failed | import | proteindiffraction.org | APS | 19-BM | ADSC QUANTUM 210r |  |  |  |  |  |  |  |  |  |  |  | 1 |  |
| 6JXQ | Failed | Input selection | Other (manual) | PAL/PLS | 11C | PILATUS3 S 6M |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 9QVU | Complete |  | Other (manual) | DIAMOND | I04-1 | PILATUS3 6M | P 1 21 1 | 1 | 1390 | 85.0 | 1.09 | 1.53 | 0.998 | 0.998 | 69.7 | 97.8 | 2.2 | 202 |  |
| 8HKR | Complete |  | proteindiffraction.org | ESRF | ID29 | PILATUS3 6M | P 1 | 2 | 7200 | 82.7 | 1.90 | 2.34 | 0.983 | 0.983 | 67.3 | 96.4 | 4.7 | 1068 |  |
| 7R34 | Download failed |  | Other (manual) | SLAC LCLS | CXI | CS-PAD CXI-1 |  |  |  |  |  |  |  |  |  |  |  |  | CXIDB 177: LCLS CSPAD hit-finding patterns only; XFEL serial data, not downloaded |
| 8VTD | Failed | import | proteindiffraction.org | APS | 17-ID | PILATUS 6M |  |  |  |  |  |  |  |  |  |  |  | 2 |  |
| 7R1E | Download failed |  | Other (manual) | SLAC LCLS | CXI | CS-PAD CXI-2 |  |  |  |  |  |  |  |  |  |  |  |  | CXIDB 190 raw LCLS XTC files, ~17.3 TB total (smallest part 4.2 TB), exceeds 500 GB limit |
| 7WDT | Failed | import | PDBj XRDA | SPRING-8 | BL26B2 | RAYONIX MX225-HS |  |  |  |  |  |  |  |  |  |  |  | 2 |  |
| 7DVO | Download failed |  | Other (manual) | SACLA | BL3 | RAYONIX MX300-HS |  |  |  |  |  |  |  |  |  |  |  |  | CXIDB 179 data host portal.nersc.gov/archive/.../cxidb/www returns HTTP 500 for all paths (retried over several minutes); Globus-only alternative needs login; size unknown |
| 6IRK | Failed | Input selection | Other (manual) | PAL-XFEL | CSI | RAYONIX MX225-HS |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 7KCN | Complete |  | proteindiffraction.org | LNLS | W01B-MX2 | PILATUS 2M | P 1 | 2 | 5040 | 10.1 | 1.45 |  | 0.872 |  | 70.2 |  | 2.8 | 4264 |  |
| 6JCG | Failed | Input selection | Other (manual) | PAL-XFEL | NCI | RAYONIX MX-225 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 6V53 | Failed | refine | proteindiffraction.org | APS | 22-ID | RAYONIX MX300-HS | P 1 | 1 | 1800 | 92.6 |  |  |  |  |  |  |  | 129 |  |
| 6R16 | Complete |  | proteindiffraction.org | DIAMOND | I04 | PILATUS 6M-F | P 21 21 21 | 1 | 2000 | 74.9 | 2.09 | 2.60 | 0.997 | 0.998 | 68.7 | 97.4 | 5.7 | 215 |  |
| 6YS2 | Download failed |  | Other (manual) | ESRF | ID29 | EIGER X 4M |  |  |  |  |  |  |  |  |  |  |  |  | shares CXIDB 177 with 7AV4: deposition holds only LCLS CSPAD hit-finding patterns; no synchrotron EIGER raw images for this entry |
| 6NCR | Failed | integrate | proteindiffraction.org | ALS | 5.0.1 | PILATUS 6M |  | 2 | 774 |  |  |  |  |  |  |  |  | 30 |  |
| 6S1G | Download failed |  | Other (manual) | SwissFEL ARAMIS | ESA | PSI JUNGFRAU 1M |  |  |  |  |  |  |  |  |  |  |  |  | CXIDB 105 raw files on portal.nersc.gov/archive return HTTP 500 for all 123 files (checked repeatedly); only other route is Globus (login required) |
| 7WEZ | Complete |  | proteindiffraction.org | ESRF | ID29 | PILATUS 6M-F | C 1 2 1 | 1 | 1127 | 48.2 | 1.42 | 1.84 | 0.996 | 0.997 | 72.8 | 99.0 | 2.7 | 106 |  |
| 6VZW | Complete |  | SBGrid | ALS | 5.0.2 | PILATUS 2M | P 2 2 21 | 1 | 360 | 88.8 | 1.48 | 1.90 | 0.992 | 0.995 | 80.8 | 100.0 | 10.0 | 433 |  |
| 8F4G | Download failed |  | Other (manual) | SLAC LCLS | MFX | RAYONIX MX170-HS |  |  |  |  |  |  |  |  |  |  |  |  | shares CXIDB 215 with 8F4F: raw data is LCLS XTC, ~4.1 TB and ~4.8 TB, far above 500 GB limit; XFEL serial data |
| 8X1A | Failed | find_spots | proteindiffraction.org | RRCAT INDUS-2 | PX-BL21 | MAR scanner 345 mm plate |  | 3 | 381 |  |  |  |  |  |  |  |  | 4 |  |
| 6JOD | Download failed |  | PDBj XRDA | SPRING-8 | BL32XU | RAYONIX MX225-HS |  |  |  |  |  |  |  |  |  |  |  |  | stopped at 324 GB of 1301 GB; over the 500 GB limit; small-wedge multi-crystal data (partial data kept in data/) |
| 6DKM | Complete |  | proteindiffraction.org | ALS | 8.2.2 | ADSC QUANTUM 315r | P 1 21 1 | 1 | 200 | 87.1 | 1.30 | 2.20 | 0.983 | 0.997 | 72.4 | 100.0 | 3.5 | 109 |  |
| 7TCD | Complete |  | proteindiffraction.org | SLS | X06SA | EIGER2 S 16M | I 1 2 1 | 1 | 3600 | 54.9 | 1.58 | 1.63 | 0.998 | 0.998 | 61.0 | 66.7 | 7.1 | 409 |  |
| 7MDN | Complete |  | proteindiffraction.org | APS | 19-ID | PILATUS3 S 6M | P 1 | 1 | 1000 | 22.9 | 1.53 | 2.05 | 0.973 | 0.977 | 55.7 | 89.7 | 2.1 | 185 |  |
| 6MOK | Complete |  | SBGrid | ALS | 8.2.1 | ADSC QUANTUM 315 | C 1 2 1 | 1 | 180 | 88.3 | 2.29 | 4.14 | 0.792 | 0.900 | 63.3 | 99.9 | 2.7 | 185 |  |
| 6R2O | Download failed |  | Other (manual) | SLAC LCLS | MFX | CS-PAD XPP |  |  |  |  |  |  |  |  |  |  |  |  | CXIDB id-120: Cheetah CXI files total ~3.98 TB (60 files), exceeds 500 GB limit |
| 6NKQ | Complete |  | proteindiffraction.org | ALS | 8.3.1 | PILATUS 300K | P 6 2 2 | 7 | 7203 | 71.8 | 1.43 |  | 1.000 |  | 88.9 |  | 179.7 | 2928 |  |
| 6CKT | Complete |  | proteindiffraction.org | ALS | 5.0.1 | ADSC QUANTUM 315r | R 3 :H | 1 | 720 | 90.0 | 1.14 | 1.55 | 0.998 | 0.999 | 76.2 | 99.9 | 4.0 | 207 |  |
| 6CK7 | Complete |  | proteindiffraction.org | ALS | 5.0.1 | PILATUS3 S 6M | P 1 21 1 | 1 | 720 | 59.7 | 1.32 | 1.42 | 0.998 | 0.998 | 68.6 | 83.2 | 2.8 | 295 |  |
| 6VIP | Complete |  | proteindiffraction.org | CLSI | 08ID-1 | PILATUS3 S 6M | P 21 21 21 | 1 | 220 | 96.2 | 1.07 | 1.24 | 0.998 | 0.998 | 83.8 | 99.8 | 6.6 | 272 |  |
| 6CW0 | Complete |  | proteindiffraction.org | CLSI | 08ID-1 | PILATUS 6M | P 21 21 21 | 1 | 240 | 91.2 | 1.06 | 1.16 | 0.997 | 0.997 | 86.5 | 98.9 | 6.9 | 260 |  |
| 8R2G | Complete |  | proteindiffraction.org | DIAMOND | I04 | PILATUS3 6M | C 1 2 1 | 1 | 2000 | 33.1 | 1.77 |  | 0.830 |  | 65.4 |  | 3.1 | 1088 |  |
| 7BVT | Complete |  | PDBj XRDA | PHOTON FACTORY | AR-NW12A | PILATUS3 S 2M | P 61 2 2 | 1 | 900 | 80.6 | 1.27 | 1.46 | 0.998 | 0.999 | 89.0 | 99.4 | 15.2 | 494 |  |
| 6KV0 | Complete |  | PDBj XRDA | SPRING-8 | BL26B1 | RAYONIX MX225HE | P 1 | 1 | 720 | 82.5 | 1.05 | 1.10 | 0.995 | 0.995 | 57.9 | 65.1 | 2.8 | 167 |  |
| 6KUM | Complete |  | PDBj XRDA | SPRING-8 | BL26B1 | MARMOSAIC 225 mm CCD | P 1 | 8 | 720 | 84.8 | 1.05 |  | 0.994 |  | 66.3 |  | 3.1 | 227 |  |
| 7CCZ | Complete |  | PDBj XRDA | SPRING-8 | BL44XU | RAYONIX MX225HE | P 21 21 21 | 1 | 360 | 95.4 | 1.31 | 1.59 | 0.996 | 0.996 | 74.8 | 98.9 | 6.2 | 302 |  |
| 6N1L | Complete |  | proteindiffraction.org | APS | 22-ID | MARMOSAIC 300 mm CCD | P 61 | 1 | 360 | 84.5 | 1.24 | 1.54 | 0.999 | 0.999 | 86.7 | 100.0 | 16.8 | 294 |  |
| 6MDX | Complete |  | proteindiffraction.org | APS | 19-ID | ADSC QUANTUM 315r | P 21 2 21 | 1 | 800 | 93.8 | 1.20 | 1.42 | 0.998 | 0.998 | 79.2 | 99.5 | 12.2 | 228 |  |
| 6OWZ | Complete |  | proteindiffraction.org | DIAMOND | I23 | PILATUS 2M | P 4 2 2 | 3 | 10800 | 50.1 | 1.57 | 1.84 | 0.999 | 0.999 | 99.8 | 99.9 | 42.0 | 966 |  |
| 5ZIL | Complete |  | PDBj XRDA | SPRING-8 | BL41XU | PILATUS 6M | P 1 21 1 | 1 | 500 | 98.0 | 0.86 | 1.33 | 0.983 | 0.983 | 71.7 | 96.6 | 1.8 | 229 |  |
| 6OWX | Failed | symmetry | proteindiffraction.org | DIAMOND | I23 | PILATUS3 2M | P 1 | 3 | 10800 | 24.3 |  |  |  |  |  |  |  | 975 |  |
| 5ZIQ | Complete |  | proteindiffraction.org | SPRING-8 | BL44XU | RAYONIX MX300HE | P 1 | 1 | 180 | 98.6 | 0.87 | 1.24 | 0.991 | 0.991 | 71.8 | 95.8 | 2.0 | 223 |  |
| 6IU9 | Complete |  | Zenodo | SPRING-8 | BL41XU | PILATUS3 6M | P 1 | 2 | 3600 | 66.9 | 2.25 | 3.14 | 0.985 | 0.984 | 59.9 | 86.6 | 1.7 | 600 |  |
| 6Z9G | Failed | find_spots | Zenodo | ESRF | ID30B | EIGER X 4M |  | 1 | 2300 |  |  |  |  |  |  |  |  | 44 |  |
| 6EXI | Complete |  | MX-RDR | BESSY | 14.1 | PILATUS 6M-F | P 1 21 1 | 1 | 2999 | 82.9 | 1.49 | 1.64 | 0.995 | 0.995 | 70.2 | 87.5 | 4.9 | 393 |  |
| 6P8P | Complete |  | SBGrid | APS | 24-ID-C | PILATUS3 S 6M | P 4 | 1 | 900 | 78.2 | 1.17 | 1.71 | 0.990 | 0.996 | 80.1 | 100.0 | 5.3 | 231 |  |
| 6MOE | Complete |  | SBGrid | APS | 23-ID-B | PILATUS 6M | P 21 21 2 | 1 | 1800 | 86.7 | 1.51 | 1.90 | 0.999 | 0.999 | 80.5 | 100.0 | 10.6 | 500 |  |
| 6OTG | Failed | index | proteindiffraction.org | APS | 22-BM | MARMOSAIC 225 mm CCD |  | 1 | 180 |  |  |  |  |  |  |  |  | 26 |  |
| 6O2H | Failed | import | SBGrid | CHESS | F1 | PILATUS3 6M |  |  |  |  |  |  |  |  |  |  |  | 4 |  |
| 6NVB | Complete |  | proteindiffraction.org | AUSTRALIAN SYNCHROTRON | MX1 | ADSC QUANTUM 210r | P 1 | 1 | 720 | 75.4 | 1.26 | 1.42 | 0.998 | 0.998 | 62.9 | 83.8 | 3.9 | 252 |  |
| 5VP5 | Complete |  | proteindiffraction.org | ALS | 5.0.2 | ADSC QUANTUM 315r | I 1 2 1 | 1 | 720 | 88.1 | 1.43 |  | 0.998 |  | 72.3 |  | 2.9 | 156 |  |
| 6BLI | Complete |  | SBGrid | APS | 23-ID-D | PILATUS3 S 6M | C 1 2 1 | 1 | 720 | 69.3 | 1.61 | 1.98 | 0.988 | 0.988 | 70.4 | 98.9 | 2.9 | 203 |  |
| 6AK1 | Complete |  | proteindiffraction.org | SSRF | BL17U1 | ADSC QUANTUM 315r | P 1 | 1 | 90 | 34.0 | 1.34 |  | -0.001 |  | 37.5 |  | 1.3 | 642 |  |
| 7PD5 | Complete |  | SBGrid | ESRF | ID29 | PILATUS 6M | I 41 | 1 | 2400 | 87.6 | 1.38 | 1.83 | 0.999 | 0.999 | 79.5 | 100.0 | 3.6 | 172 |  |
| 5V8T | Complete |  | proteindiffraction.org | CLSI | 08ID-1 | MARMOSAIC 300 mm CCD | P 1 2 1 | 1 | 200 | 93.8 | 1.60 | 1.80 | 0.992 | 0.993 | 67.6 | 87.4 | 3.6 | 95 |  |
| 6U7F | Complete |  | proteindiffraction.org | CLSI | 08ID-1 | RAYONIX MX-300 | P 1 21 1 | 1 | 449 | 94.3 | 1.68 | 2.16 | 0.995 | 0.996 | 68.5 | 99.6 | 3.3 | 259 |  |
| 6P7O | Failed | import | SBGrid | SSRL | BL14-1 | MARMOSAIC 325 mm CCD |  |  |  |  |  |  |  |  |  |  |  | 3 |  |
| 9OM8 | Complete |  | Zenodo | APS | 17-ID | PILATUS3 6M | I 1 2 1 | 1 | 500 | 76.2 | 1.26 | 1.98 | 0.965 | 0.978 | 69.7 | 93.4 | 2.1 | 142 |  |
| 5VYP | Complete |  | SBGrid | AUSTRALIAN SYNCHROTRON | MX2 | ADSC QUANTUM 315 | P 1 21 1 | 1 | 360 | 23.5 | 1.70 | 2.46 | 0.956 | 0.989 | 69.5 | 100.0 | 6.2 | 165 |  |
| 8K7Y | Complete |  | PDBj XRDA | PHOTON FACTORY | BL-17A | PILATUS 6M | P 1 21 1 | 1 | 180 | 91.3 | 1.26 | 1.46 | 0.964 | 0.964 | 70.1 | 93.8 | 3.2 | 212 |  |
| 6U4K | Failed | index | SBGrid | APS | 22-ID | RAYONIX MX300HE |  | 1 | 360 |  |  |  |  |  |  |  |  | 32 |  |
| 8YJO | Complete |  | proteindiffraction.org | NSRRC | BL13B1 | ADSC QUANTUM 315r | P 1 21 1 | 1 | 360 | 98.5 | 1.52 | 1.69 | 0.993 | 0.994 | 71.1 | 89.7 | 3.3 | 171 |  |
| 5MLN | Complete |  | proteindiffraction.org | ESRF | ID23-2 | MARMOSAIC 225 mm CCD | P 21 2 21 | 1 | 1100 | 98.1 | 0.99 | 1.34 | 0.999 | 0.999 | 80.6 | 100.0 | 6.6 | 334 |  |
| 5ONZ | Complete |  | SBGrid | ESRF | ID23-2 | PILATUS 2M-F | P 21 2 21 | 1 | 3200 | 94.2 | 1.13 | 1.68 | 0.990 | 0.990 | 79.1 | 100.0 | 4.6 | 297 |  |
| 6CS9 | Complete |  | SBGrid | AUSTRALIAN SYNCHROTRON | MX2 | ADSC QUANTUM 210r | P 1 21 1 | 1 | 210 | 40.8 | 1.52 | 1.77 | 0.998 | 0.998 | 70.9 | 95.1 | 3.6 | 64 |  |
| 5H3L | Complete |  | SBGrid | ESRF | BM14 | MARMOSAIC 225 mm CCD | P 4 21 2 | 1 | 181 | 60.5 | 1.47 | 2.48 | 0.614 | 0.798 | 78.0 | 100.0 | 10.6 | 229 |  |
| 6YJP | Complete |  | SBGrid | DIAMOND | I02 | PILATUS 6M-F | C 1 2 1 | 6 | 16200 | 82.5 | 2.30 | 2.87 | 0.996 | 0.999 | 83.6 | 99.9 | 19.7 | 657 |  |
| 7BBP | Complete |  | Zenodo | DIAMOND | I04-1 | PILATUS 2M | P 1 21 1 | 1 | 1200 | 94.5 | 1.27 | 1.80 | 0.997 | 0.997 | 73.3 | 98.8 | 2.5 | 140 |  |
| 6E80 | Complete |  | SBGrid | ALS | 5.0.2 | PILATUS3 X 6M | I 1 2 1 | 1 | 2880 | 31.3 | 1.59 | 2.26 | 0.617 | 0.779 | 69.5 | 99.6 | 11.0 | 269 |  |
| 5OD9 | Complete |  | proteindiffraction.org | SLS | X06SA | PILATUS 2M | P 2 21 21 | 1 | 3600 | 76.5 | 1.02 | 1.12 | 0.999 | 0.999 | 86.8 | 99.2 | 10.6 | 345 |  |
| 6WAU | Complete |  | proteindiffraction.org | CLSI | 08B1-1 | RAYONIX MX300HE | P 6 | 1 | 400 | 77.0 | 1.43 | 1.64 | 1.000 | 1.000 | 86.3 | 99.9 | 8.9 | 215 |  |
| 5NHU | Complete |  | SBGrid | ESRF | ID30B | PILATUS 6M-F | I 1 2 1 | 1 | 2100 | 69.2 | 1.12 | 1.44 | 0.975 | 0.974 | 70.2 | 93.2 | 1.9 | 263 |  |
| 5TZP | Complete |  | SBGrid | AUSTRALIAN SYNCHROTRON | MX2 | ADSC QUANTUM 315r | P 41 | 3 | 731 | 31.5 | 1.11 | 1.27 | 0.999 | 0.999 | 81.7 | 99.0 | 12.2 | 345 |  |
| 7AO4 | Complete |  | proteindiffraction.org | BESSY | 14.3 | MAR CCD 165 mm | C 2 2 21 | 1 | 1500 | 90.7 | 1.57 | 1.77 | 0.994 | 0.995 | 79.0 | 96.9 | 4.2 | 107 |  |
| 5K9F | Complete |  | proteindiffraction.org | APS | 21-ID-F | RAYONIX MX-225 | I 4 2 2 | 1 | 150 | 91.3 | 1.24 | 1.35 | 0.997 | 0.997 | 81.5 | 94.3 | 9.8 | 160 |  |
| 5J92 | Complete |  | proteindiffraction.org | APS | 21-ID-F | RIGAKU SATURN 944+ | P 1 21 1 | 1 | 200 | 92.2 | 1.46 | 1.54 | 0.965 | 0.965 | 65.6 | 74.5 | 3.8 | 178 |  |
| 5VZR | Complete |  | SBGrid | APS | 19-ID | PILATUS 2M | P 21 21 21 | 1 | 1200 | 98.2 | 1.24 | 1.45 | 0.996 | 0.996 | 81.2 | 99.4 | 5.4 | 358 |  |
| 5K7M | Complete |  | SBGrid | APS | 19-ID | PILATUS 12M | P 41 21 2 | 1 | 999 | 99.1 | 1.28 | 1.46 | 1.000 | 1.000 | 88.4 | 100.0 | 16.2 | 778 |  |
| 6O6N | Complete |  | SBGrid | SOLEIL | PROXIMA 1 | PILATUS 6M | P 41 21 2 | 1 | 999 | 78.7 | 1.21 | 1.53 | 1.000 | 1.000 | 87.1 | 100.0 | 10.5 | 220 |  |
| 5M0Z | Complete |  | proteindiffraction.org | ESRF | BM14 | RAYONIX MX-225 | P 1 | 1 | 200 | 43.3 | 1.19 |  | 0.136 |  | 48.0 |  | 1.4 | 464 |  |
| 5IAX | Complete |  | SBGrid | ALS | 4.2.2 | NOIR-1 | P 1 | 1 | 1800 | 8.6 | 1.43 |  | -0.007 |  | 49.9 |  | 1.5 | 2621 |  |
| 7D6R | Complete |  | PDBj XRDA | PHOTON FACTORY | BL-17A | PILATUS3 S 6M | P 1 | 1 | 360 | 84.8 | 1.25 |  | 0.433 |  | 62.4 |  | 1.7 | 594 |  |
| 5F47 | Complete |  | proteindiffraction.org | APS | 21-ID-G | MAR scanner 300 mm plate | I 1 2 1 | 2 | 440 | 90.1 | 1.14 | 1.35 | 0.998 | 0.998 | 66.8 | 94.0 | 7.4 | 353 |  |
| 8UKV | Complete |  | SBGrid | APS | 23-ID-B | RAYONIX MX-300 | P 1 | 1 | 720 | 15.6 | 2.16 | 2.59 | 0.998 | 0.998 | 57.2 | 87.3 | 3.9 | 227 |  |
| 5TTA | Complete |  | proteindiffraction.org | APS | 21-ID-D | RAYONIX MX-300 | I 1 2 1 | 2 | 960 | 30.7 | 1.46 | 2.11 | 0.974 | 0.990 | 70.5 | 99.9 | 6.0 | 250 |  |
| 5EQV | Complete |  | proteindiffraction.org | APS | 21-ID-G | MARMOSAIC 325 mm CCD | P 41 21 2 | 1 | 360 | 98.5 | 1.11 | 1.20 | 0.996 | 0.996 | 81.3 | 94.5 | 11.7 | 524 |  |
| 7UNO | Failed | symmetry | proteindiffraction.org | APS | 19-ID | ADSC QUANTUM 315 | P 1 | 2 | 360 | 56.2 |  |  |  |  |  |  |  | 565 |  |
| 5LXW | Failed | import | Zenodo | DIAMOND | I04 | PILATUS3 S 6M |  |  |  |  |  |  |  |  |  |  |  | 2 |  |
| 5NKT | Complete |  | proteindiffraction.org | NSLS | X6A | PILATUS 2M-F | R 3 2 :H | 1 | 1800 | 95.5 | 1.27 | 1.42 | 0.999 | 0.999 | 79.8 | 95.7 | 7.9 | 287 |  |
| 5TOJ | Complete |  | SBGrid | APS | 23-ID-B | MARMOSAIC 300 mm CCD | P 31 2 1 | 1 | 240 | 64.7 | 2.37 | 3.05 | 0.992 | 0.993 | 73.4 | 99.4 | 5.9 | 185 |  |
| 5IUJ | Complete |  | SBGrid | SOLEIL | PROXIMA 2 | ADSC QUANTUM 315r | P 1 | 1 | 110 | 16.3 | 2.28 | 3.40 | 0.751 | 0.811 | 38.3 | 66.7 | 1.6 | 195 |  |
| 5CYZ | Complete |  | SBGrid | APS | 24-ID-C | PSI PILATUS 6M | P 1 21 1 | 2 | 1800 | 87.7 | 1.20 | 1.76 | 0.989 | 0.997 | 73.6 | 99.3 | 5.8 | 334 |  |
| 7TBO | Download failed |  | proteindiffraction.org | SLS | X06SA | PILATUS 6M |  |  |  |  |  |  |  |  |  |  |  |  | [Errno 2] No such file or directory: 'entries/7TBO/data/7tbo/other/proc/Images' |
| 6NW4 | Complete |  | proteindiffraction.org | SLS | X06DA | PILATUS3 6M | P 31 2 1 | 1 | 3600 | 23.9 | 1.27 | 2.28 | 0.950 | 0.993 | 79.6 | 100.0 | 15.3 | 290 |  |
| 5Y5H | Failed | integrate | Other (manual) | SACLA | BL3 | RAYONIX MX225-HS | P 1 | 134 | 2995 | 44.7 |  |  |  |  |  |  |  | 2618 |  |
| 5UAI | Complete |  | proteindiffraction.org | APS | 21-ID-G | RAYONIX MX-225 | P 21 2 21 | 1 | 180 | 89.8 | 1.73 | 2.10 | 0.990 | 0.992 | 74.5 | 98.8 | 5.5 | 195 |  |
| 5LP9 | Complete |  | proteindiffraction.org | SLS | X10SA | PILATUS 6M-F | P 1 21 1 | 1 | 3600 | 90.1 | 0.83 | 0.85 | 0.999 | 0.999 | 78.6 | 83.5 | 6.1 | 393 |  |
| 7EXU | Complete |  | PDBj XRDA | PHOTON FACTORY | AR-NE3A | ADSC QUANTUM 270 | P 31 2 1 | 1 | 180 | 99.3 | 1.67 | 1.91 | 0.997 | 0.997 | 82.4 | 98.3 | 7.9 | 169 |  |
| 5BXG | Complete |  | proteindiffraction.org | SSRL | BL11-1 | PILATUS 6M | P 1 21 1 | 2 | 480 | 69.5 | 1.39 | 1.77 | 0.947 | 0.945 | 63.7 | 84.8 | 2.2 | 156 |  |
| 5CZO | Complete |  | SBGrid | ALS | 12.3.1 | ADSC QUANTUM 315 | C 1 2 1 | 1 | 360 | 50.8 | 1.75 | 4.18 | 0.233 | 0.349 | 49.1 | 100.0 | 5.9 | 220 |  |
| 5WS4 | Complete |  | PDBj XRDA | SPRING-8 | BL44XU | MAR scanner 300 mm plate | P 41 21 2 | 2 | 400 | 99.2 | 2.34 | 3.19 | 0.997 | 0.996 | 79.2 | 100.0 | 13.4 | 401 |  |
| 5E9I | Complete |  | SBGrid | ELETTRA | 5.2R | PILATUS 2M | C 2 2 21 | 1 | 180 | 84.6 | 1.20 | 1.39 | 0.992 | 0.992 | 78.8 | 96.2 | 5.3 | 123 |  |
| 5C50 | Complete |  | SBGrid | ALS | 8.3.1 | ADSC QUANTUM 315r | P 1 | 2 | 490 | 98.5 | 1.31 | 1.45 | 0.997 | 0.997 | 65.0 | 82.8 | 2.8 | 245 |  |
| 5D4I | Download failed |  | Other (manual) | SACLA | BL3 | CUSTOM-MADE |  |  |  |  |  |  |  |  |  |  |  |  | raw data 1.3 TB+ (380 of 386 h5 files fetched), exceeds 500 GB limit |
| 5IWL | Complete |  | SBGrid | SSRL | BL7-1 | ADSC QUANTUM 315 | C 1 2 1 | 1 | 180 | 47.9 | 2.03 | 3.18 | 0.839 | 0.879 | 60.7 | 98.9 | 3.7 | 100 |  |
| 5FD7 | Failed | index | SBGrid | CHESS | F1 | PILATUS 6M |  | 1 | 180 |  |  |  |  |  |  |  |  | 12 |  |
| 5FD9 | Failed | index | SBGrid | CHESS | F1 | ADSC QUANTUM 270 |  | 1 | 210 |  |  |  |  |  |  |  |  | 13 |  |
| 5E11 | Failed | integrate | SBGrid | APS | 14-ID-B | RAYONIX MX340-HS |  | 20 | 1815 |  |  |  |  |  |  |  |  | 230 |  |
| 5EA8 | Complete |  | SBGrid | ALS | 5.0.3 | ADSC QUANTUM 315r | P 4 3 2 | 1 | 360 | 25.0 | 1.36 | 2.71 | 0.587 | 0.661 | 93.9 | 100.0 | 27.3 | 1280 |  |
| 5JVL | Complete |  | proteindiffraction.org | ESRF | BM30A | ADSC QUANTUM 315r | P 1 | 1 | 720 | 9.0 | 1.89 | 2.99 | 0.482 | 0.641 | 54.6 | 94.4 | 2.6 | 1838 |  |
| 6F3O | Complete |  | proteindiffraction.org | BESSY | 14.3 | RAYONIX MX-225 | C 1 2 1 | 1 | 400 | 20.2 | 1.32 | 2.17 | 0.793 | 0.797 | 66.6 | 91.8 | 3.2 | 512 |  |
| 8BFY | Complete |  | SBGrid | SOLEIL | PROXIMA 1 | PILATUS3 6M | P 1 21 1 | 2 | 2291 | 60.8 | 1.23 | 1.63 | 0.646 | 0.997 | 75.0 | 100.0 | 7.1 | 300 |  |
| 6NQW | Complete |  | SBGrid | SOLEIL | PROXIMA 2 | ADSC QUANTUM 315 | P 6 2 2 | 1 | 200 | 48.6 | 1.46 | 1.83 | 0.990 | 0.991 | 86.3 | 100.0 | 8.4 | 187 |  |
| 5D6A | Complete |  | proteindiffraction.org | APS | 21-ID-G | MARMOSAIC 225 mm CCD | P 31 2 1 | 1 | 240 | 83.8 | 1.70 | 2.13 | 0.995 | 0.997 | 75.7 | 99.5 | 8.2 | 142 |  |
| 4X54 | Complete |  | proteindiffraction.org | APS | 17-ID | RAYONIX MX-225 | I 2 2 2 | 1 | 90 | 88.7 | 1.14 | 1.30 | 0.986 | 0.986 | 75.1 | 95.5 | 3.4 | 131 |  |
| 5TDX | Complete |  | proteindiffraction.org | APS | 23-ID-B | MAR scanner 300 mm plate | P 41 21 2 | 1 | 560 | 30.1 | 1.34 | 1.72 | 0.994 | 0.994 | 83.6 | 96.9 | 6.4 | 864 |  |
| 4WI1 | Complete |  | proteindiffraction.org | CLSI | 08ID-1 | RAYONIX MX-225 | I 1 2 1 | 1 | 334 | 96.3 | 1.23 | 1.39 | 0.998 | 0.998 | 66.8 | 86.7 | 6.8 | 649 |  |
| 5UBE | Complete |  | SBGrid | NSLS | X25 | ADSC QUANTUM 315 | P 1 21 1 | 1 | 90 | 62.1 | 1.49 | 1.77 | 0.987 | 0.987 | 56.1 | 83.1 | 1.6 | 78 |  |
| 4TVT | Complete |  | proteindiffraction.org | NSLS | X25 | PSI PILATUS 6M | P 2 21 21 | 1 | 360 | 58.7 | 1.39 | 1.82 | 0.954 | 0.953 | 74.2 | 100.0 | 5.8 | 253 |  |
| 5JLT | Complete |  | proteindiffraction.org | APS | 22-ID | MAR CCD 130 mm | P 61 2 2 | 1 | 900 | 92.2 | 2.05 | 2.92 | 0.999 | 0.999 | 84.3 | 100.0 | 28.0 | 255 |  |
| 5E7S | Complete |  | SBGrid | NSRRC | BL15A1 | RAYONIX MX-325 | C 1 2 1 | 1 | 241 | 73.6 | 1.86 | 2.17 | 0.992 | 0.993 | 67.6 | 91.9 | 4.2 | 401 |  |
| 4R8F | Complete |  | SBGrid | NSRRC | BL15A | RAYONIX MX300HE | R 3 :H | 1 | 120 | 97.3 | 1.74 | 2.05 | 0.993 | 0.993 | 71.0 | 94.0 | 3.0 | 282 |  |
| 4Z3U | Complete |  | SBGrid | APS | 24-ID-C | ADSC QUANTUM 315 | P 42 21 2 | 1 | 600 | 85.0 | 2.02 | 2.28 | 0.997 | 0.997 | 80.9 | 97.2 | 5.9 | 185 |  |
| 4QQD | Complete |  | proteindiffraction.org | APS | 19-ID | adsc q315 | C 2 2 2 | 1 | 180 | 53.9 | 1.53 | 2.53 | 0.738 | 0.763 | 70.5 | 100.0 | 6.1 | 259 |  |
| 6B3I | Complete |  | SBGrid | APS | 21-ID-G | MARRESEARCH | I 1 2 1 | 1 | 220 | 71.5 | 1.69 | 2.28 | 0.977 | 0.977 | 61.8 | 99.0 | 4.1 | 188 |  |
| 5W23 | Failed | index | SBGrid | CHESS | A1 | ADSC QUANTUM 210 |  | 1 | 180 |  |  |  |  |  |  |  |  | 22 |  |
| 5KJ7 | Failed | integrate | SBGrid | SLAC LCLS | XPP | RAYONIX MX-325 |  | 14 | 188 |  |  |  |  |  |  |  |  | 58 |  |
| 5DGY | Download failed |  | Other (manual) | SLS | X10SA | PSI PILATUS 6M |  |  |  |  |  |  |  |  |  |  |  |  | CXIDB 32 (LCLS CSPAD SFX): raw files ~10.9 TB tape-stored, exceeds 500 GB; hit-filtered CXI batches alone ~86 GB |
| 7RJZ | Complete |  | proteindiffraction.org | NSLS | X6A | ADSC QUANTUM 210 | P 1 | 1 | 180 | 37.8 | 1.48 |  | 0.338 |  | 59.7 |  | 1.8 | 140 |  |
| 4QGR | Complete |  | proteindiffraction.org | SSRL | BL7-1 | ADSC QUANTUM 315r | P 1 21 1 | 1 | 180 | 58.5 | 1.40 | 1.48 | 0.993 | 0.993 | 74.2 | 84.9 | 3.3 | 178 |  |
| 5JZQ | Download failed |  | MX-RDR | BESSY | 14.2 | RAYONIX MX-225 |  |  |  |  |  |  |  |  |  |  |  |  | command failed (33): curl |
| 4YPM | Complete |  | SBGrid | NSRRC | BL15A1 | RAYONIX MX325HE | P 6 2 2 | 1 | 360 | 98.5 | 1.34 | 1.48 | 0.998 | 0.998 | 86.8 | 99.3 | 16.3 | 437 |  |
| 4XGU | Complete |  | SBGrid | SSRL | BL12-2 | PSI PILATUS 6M | C 2 2 21 | 1 | 180 | 71.0 | 2.10 | 2.95 | 0.993 | 0.995 | 68.3 | 100.0 | 6.0 | 184 |  |
| 6BGA | Complete |  | SBGrid | SSRL | BL11-1 | PILATUS3 6M | I 1 2 1 | 1 | 950 | 52.2 | 1.68 | 2.17 | 0.984 | 0.984 | 63.4 | 97.2 | 3.5 | 119 |  |
| 7QOQ | Complete |  | SBGrid | ESRF | ID23-2 | PILATUS 6M | P 1 | 1 | 1000 | 43.9 | 1.16 | 2.02 | 0.901 | 0.935 | 56.6 | 90.8 | 1.5 | 134 |  |
| 4R4K | Failed | symmetry | proteindiffraction.org | SSRL | BL9-2 | MARMOSAIC 325 mm CCD | P 1 | 5 | 1590 | 50.5 |  |  |  |  |  |  |  | 737 |  |
| 4WA7 | Complete |  | SBGrid | APS | 19-ID | ADSC QUANTUM 210r | P 63 | 1 | 261 | 70.1 | 1.45 | 1.83 | 0.996 | 0.996 | 80.4 | 100.0 | 5.9 | 129 |  |
| 4RWD | Failed | Input selection | Other (manual) | SLAC LCLS | CXI | Cornell-SLAC Pixel Array Detector (CSPAD) |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 5AUI | Download failed |  | PDBj XRDA | PHOTON FACTORY | BL-1A | PILATUS 2M-F |  |  |  |  |  |  |  |  |  |  |  |  | command failed (23): rsync |
| 8IBT | Complete |  | PDBj XRDA | PHOTON FACTORY | BL-5A | ADSC QUANTUM 315 | P 6 2 2 | 1 | 240 | 98.1 | 1.65 | 1.94 | 0.986 | 0.987 | 86.7 | 99.4 | 9.8 | 322 |  |
| 4OHC | Complete |  | proteindiffraction.org | APS | 21-ID-G | RAYONIX MX225HE | P 1 | 1 | 360 | 93.1 | 1.39 | 1.60 | 0.998 | 0.998 | 61.8 | 86.5 | 3.7 | 327 |  |
| 5N15 | Complete |  | SBGrid | ESRF | ID23-2 | MARMOSAIC 300 mm CCD | P 1 | 1 | 120 | 71.2 | 1.60 |  | 0.004 |  | 45.7 |  | 1.6 | 172 |  |
| 7TAL | Download failed |  | proteindiffraction.org | SLS | X06DA | PILATUS 6M |  |  |  |  |  |  |  |  |  |  |  |  | [Errno 2] No such file or directory: 'entries/7TAL/data/7tal/data/ForBackgroundOnly_00003.img' |
| 6H26 | Failed | symmetry | MX-RDR | BESSY | 14.2 | MARMOSAIC 225 mm CCD | P 1 | 10 | 480 | 73.9 |  |  |  |  |  |  |  | 990 |  |
| 6NQY | Complete |  | SBGrid | SOLEIL | PROXIMA 1 | PILATUS3 S 6M | C 1 2 1 | 1 | 900 | 40.4 | 1.73 | 2.12 | 0.988 | 0.987 | 59.9 | 92.3 | 3.1 | 127 |  |
| 5T4N | Complete |  | SBGrid | APS | 24-ID-E | ADSC QUANTUM 315r | P 6 | 1 | 110 | 67.7 | 1.92 | 2.74 | 0.992 | 0.997 | 75.7 | 99.7 | 5.1 | 114 |  |
| 5FFG | Complete |  | SBGrid | APS | 23-ID-B | MAR CCD 165 mm | I 1 2 1 | 1 | 152 | 66.7 | 1.49 | 2.00 | 0.990 | 0.991 | 71.3 | 99.1 | 2.8 | 157 |  |
| 4NTL | Complete |  | proteindiffraction.org | ALS | 8.2.1 | ADSC Q315 | I 4 2 2 | 3 | 540 | 91.2 | 1.26 | 1.67 | 0.997 | 0.997 | 86.9 | 100.0 | 10.2 | 531 |  |
| 5K6X | Complete |  | SBGrid | NSLS | X4C | MAR CCD 165 mm | P 1 21 1 | 1 | 305 | 82.8 | 1.92 | 2.43 | 0.947 | 0.944 | 62.1 | 94.7 | 5.7 | 131 |  |
| 8HL7 | Failed | index | proteindiffraction.org | PAL/PLS | 5C (4A) | ADSC QUANTUM 315r |  | 1 | 360 |  |  |  |  |  |  |  |  | 22 |  |
| 4PR9 | Failed | import | SBGrid | APS | 22-ID | RAYONIX MX300HS |  |  |  |  |  |  |  |  |  |  |  | 2 |  |
| 4MUQ | Complete |  | proteindiffraction.org | APS | 21-ID-D | MAR scanner 300 mm plate | P 1 2 1 | 1 | 400 | 89.5 | 1.53 |  | 0.995 |  | 78.8 |  | 3.6 | 143 |  |
| 4M0J | Complete |  | proteindiffraction.org | APS | 21-ID-F | MAR scanner 300 mm plate | C 1 2 1 | 1 | 180 | 82.0 | 1.37 | 1.79 | 0.997 | 0.997 | 70.3 | 100.0 | 3.2 | 167 |  |
| 8V2T | Complete |  | Zenodo | NSLS | X25 | PILATUS 6M | P 42 21 2 | 1 | 360 | 94.9 | 1.15 | 1.19 | 0.997 | 0.997 | 89.3 | 95.9 | 9.7 | 248 |  |
| 8V4J | Complete |  | Zenodo | NSLS | X29A | ADSC QUANTUM 315 | P 42 21 2 | 1 | 600 | 56.7 | 1.10 |  | 0.998 |  | 89.9 |  | 11.0 | 379 |  |
| 5EO9 | Complete |  | SBGrid | SSRL | BL11-1 | PSI PILATUS 6M | F 2 2 2 | 2 | 1810 | 26.1 | 1.66 | 2.24 | 0.977 | 0.986 | 75.2 | 100.0 | 8.2 | 367 |  |
| 4MQT | Failed | Input selection | SBGrid | APS | 23-ID-D | MARMOSAIC 300 mm CCD |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 5MXW | Complete |  | MX-RDR | MAX II | I911-2 | MARMOSAIC 225 mm CCD | P 61 | 1 | 80 | 92.0 | 1.16 | 1.42 | 0.998 | 0.998 | 80.7 | 100.0 | 4.1 | 118 |  |
| 4PNJ | Failed | Input selection | SBGrid | SLAC LCLS | XPP | CS-PAD CXI-1 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 4K6M | Complete |  | SBGrid | SSRF | BL17U | ADSC QUANTUM 4 | P 1 | 1 | 270 | 64.3 | 1.50 |  | 0.250 |  | 36.0 |  | 1.4 | 338 |  |
| 4ILD | Complete |  | SBGrid | NSLS | X25 | S/N 60-0107 | C 1 2 1 | 1 | 1200 | 51.3 | 2.22 | 2.76 | 0.997 | 0.997 | 69.6 | 98.6 | 5.3 | 110 |  |
| 4HSP | Complete |  | proteindiffraction.org | ALS | 8.2.2 | ADSC Q315 | P 62 2 2 | 3 | 360 | 96.4 | 1.71 | 2.28 | 0.996 | 0.998 | 79.2 | 100.0 | 10.2 | 204 |  |
| 4J3G | Complete |  | proteindiffraction.org | ALS | 5.0.1 | RIGAKU SATURN 944+ | P 1 | 1 | 360 | 49.9 | 1.30 | 1.66 | 0.997 | 0.997 | 62.5 | 97.1 | 3.9 | 227 |  |
| 4KAM | Complete |  | proteindiffraction.org | ALS | 5.0.1 | ADSC QUANTUM 315 | P 1 21 1 | 1 | 220 | 99.3 | 1.27 | 1.68 | 0.994 | 0.997 | 73.0 | 100.0 | 4.1 | 300 |  |
| 5MXB | Complete |  | MX-RDR | BESSY | 14.1 | MARMOSAIC 225 mm CCD | P 61 | 1 | 130 | 83.2 | 1.12 | 1.38 | 0.996 | 0.996 | 81.5 | 100.0 | 3.3 | 114 |  |
| 4QKI | Complete |  | SBGrid | DIAMOND | I02 | PILATUS 2M | P 2 21 21 | 1 | 900 | 33.2 | 1.44 | 1.49 | 0.998 | 0.998 | 72.2 | 78.9 | 5.9 | 101 |  |
| 4GNV | Complete |  | proteindiffraction.org | ALS | 5.0.3 | ADSC QUANTUM 315 | P 1 21 1 | 1 | 360 | 79.2 | 1.23 | 1.25 | 0.999 | 0.999 | 71.3 | 74.1 | 6.8 | 331 |  |
| 5L0C | Failed | import | SBGrid | APS | 22-BM | MARMOSAIC 300 mm CCD |  |  |  |  |  |  |  |  |  |  |  | 2 |  |
| 4U97 | Failed | index | SBGrid | NSLS | X29A | ADSC QUANTUM 315r |  | 1 | 360 |  |  |  |  |  |  |  |  | 25 |  |
| 4MTK | Complete |  | SBGrid | SLS | X06SA | PSI PILATUS 6M | P 61 | 1 | 720 | 93.5 | 2.44 | 2.93 | 0.763 | 0.924 | 81.5 | 99.9 | 7.2 | 504 |  |
| 4EXQ | Complete |  | proteindiffraction.org | ALS | 5.0.1 | ADSC QUANTUM 210 | P 41 21 2 | 1 | 300 | 90.4 | 1.20 | 1.37 | 0.997 | 0.996 | 81.1 | 98.6 | 4.7 | 200 |  |
| 9US6 | Complete |  | proteindiffraction.org | PHOTON FACTORY | AR-NW12A | ADSC QUANTUM 210 | P 1 21 1 | 1 | 40 | 82.0 | 1.71 | 2.50 | 0.887 | 0.947 | 44.7 | 55.0 | 1.4 | 50 |  |
| 4F4H | Failed | import | proteindiffraction.org | ALS | 5.0.2 | ADSC QUANTUM 315 |  |  |  |  |  |  |  |  |  |  |  | 2 |  |
| 4ECD | Complete |  | proteindiffraction.org | APS | 21-ID-D | MARMOSAIC 225 mm CCD | P 1 | 1 | 300 | 54.1 | 1.73 |  | 0.632 |  | 53.6 |  | 1.7 | 630 |  |
| 4QKG | Complete |  | SBGrid | DIAMOND | I02 | ADSC QUANTUM 315 | P 31 2 1 | 1 | 360 | 70.4 | 1.39 | 1.82 | 0.968 | 0.968 | 82.3 | 100.0 | 8.1 | 108 |  |
| 4X8Y | Complete |  | PDBj XRDA | SPRING-8 | BL41XU | RAYONIX MX225HE | I 41 2 2 | 5 | 1260 | 95.3 | 2.18 |  | 0.995 |  | 88.3 |  | 10.7 | 1108 |  |
| 4FS7 | Complete |  | proteindiffraction.org | SSRL | BL9-2 | MAR MAR325 | P 21 21 21 | 3 | 1080 | 79.6 | 1.03 | 1.13 | 0.993 | 0.994 | 83.3 | 98.1 | 3.1 | 667 |  |
| 5UTK | Complete |  | SBGrid | APS | 23-ID-B | MARRESEARCH | I 1 2 1 | 1 | 160 | 41.2 | 1.95 | 2.13 | 0.993 | 0.993 | 67.3 | 82.7 | 2.9 | 136 |  |
| 4TWN | Complete |  | SBGrid | SLS | X06DA | PSI PILATUS 6M | P 1 21 1 | 1 | 800 | 80.8 | 1.12 | 1.49 | 0.998 | 0.999 | 76.8 | 100.0 | 3.2 | 118 |  |
| 6ZJ6 | Failed | symmetry | Zenodo | DIAMOND | I03 | PILATUS 6M-F | P 1 | 8 | 22800 | 68.2 |  |  |  |  |  |  |  | 3541 |  |
| 4FII | Complete |  | SBGrid | NSLS | X6A | ADSC QUANTUM 270 | P 41 21 2 | 1 | 180 | 56.2 | 1.53 | 1.75 | 0.995 | 0.996 | 87.0 | 98.2 | 9.0 | 154 |  |
| 4OW3 | Download failed |  | Other (manual) | SLAC LCLS | CXI | CS-PAD detector |  |  |  |  |  |  |  |  |  |  |  |  | Raw XTC data on CXIDB id-23 totals ~4.37 TB (80 files), over the 500 GB limit |
| 5I8F | Failed | import | MX-RDR | APS | 22-ID | MARMOSAIC 225 mm CCD |  |  |  |  |  |  |  |  |  |  |  | 2 |  |
| 3UPS | Complete |  | proteindiffraction.org | APS | 18-ID | ADSC QUANTUM 315r | P 31 2 1 | 1 | 180 | 95.0 | 1.32 | 1.51 | 0.997 | 0.997 | 82.8 | 98.5 | 8.1 | 162 |  |
| 4IX5 | Complete |  | proteindiffraction.org | SSRF | BL17U | ADSC QUANTUM 315r | P 21 21 21 | 1 | 600 | 25.8 | 1.39 | 1.61 | 0.988 | 0.989 | 74.0 | 92.7 | 11.0 | 336 |  |
| 3UF8 | Complete |  | proteindiffraction.org | ALS | 5.0.1 | ADSC Q315R | P 1 21 1 | 1 | 200 | 97.6 | 1.16 | 1.22 | 0.999 | 0.999 | 75.4 | 85.0 | 3.6 | 134 |  |
| 3TX2 | Complete |  | proteindiffraction.org | CLSI | 08ID-1 | MARMOSAIC 225 mm CCD | P 21 2 21 | 1 | 280 | 88.1 | 1.15 | 1.30 | 0.994 | 0.994 | 81.8 | 98.2 | 4.5 | 244 |  |
| 7OVP | Failed | symmetry | Zenodo | SLS | X10SA | PILATUS 6M | P 1 | 5 | 6480 | 36.5 |  |  |  |  |  |  |  | 1008 |  |
| 4H41 | Failed | import | proteindiffraction.org | SSRL | BL11-1 | MARMOSAIC 325 mm CCD |  |  |  |  |  |  |  |  |  |  |  | 2 |  |
| 5BWD | Complete |  | SBGrid | NSLS | X26C | ADSC QUANTUM 315r | P 4 2 2 | 1 | 80 | 41.1 | 1.67 | 2.81 | 0.584 | 0.562 | 76.3 | 96.6 | 3.8 | 270 |  |
| 3U27 | Complete |  | proteindiffraction.org | APS | 19-ID | SBC-3 | P 1 | 1 | 238 | 29.3 | 1.29 | 3.07 | 0.188 | 0.405 | 54.5 | 87.3 | 2.3 | 474 |  |
| 7ROX | Failed | find_spots | proteindiffraction.org | LNLS | D03B-MX1 | MAR CCD 165 mm |  | 1 | 186 |  |  |  |  |  |  |  |  | 8 |  |
| 4FIG | Complete |  | SBGrid | APS | 24-ID-C | ADSC QUANTUM 315r | P 1 21 1 | 1 | 180 | 51.7 | 1.72 |  | 0.345 |  | 68.3 |  | 3.2 | 132 |  |
| 3R9P | Complete |  | proteindiffraction.org | ALS | 5.0.1 | ADSC QUANTUM 4 | P 1 2 1 | 1 | 160 | 25.9 | 1.32 |  | 0.112 |  | 68.0 |  | 2.8 | 324 |  |
| 4Y0E | Complete |  | proteindiffraction.org | ALS | 5.0.1 | MARMOSAIC 300 mm CCD | P 1 | 1 | 200 | 16.7 | 1.37 |  | 0.040 |  | 59.1 |  | 2.0 | 686 |  |
| 4UCM | Complete |  | proteindiffraction.org | ESRF | ID14-4 | ADSC CCD | P 1 | 1 | 120 | 53.4 | 1.29 | 3.40 | 0.262 | 0.337 | 46.9 | 75.6 | 1.4 | 192 |  |
| 3ZXU | Complete |  | SBGrid | APS | 24-ID-C | ADSC CCD | P 6 2 2 | 3 | 228 | 70.6 | 2.33 | 3.32 | 0.934 | 0.993 | 81.5 | 99.5 | 16.8 | 346 |  |
| 3TS0 | Complete |  | SBGrid | NSLS | X25 | ADSC QUANTUM 315r | P 41 21 2 | 1 | 102 | 97.8 | 1.95 | 2.37 | 0.996 | 0.997 | 78.8 | 100.0 | 6.2 | 113 |  |
| 3OUT | Complete |  | proteindiffraction.org | APS | 21-ID-G | MAR CCD | P 41 21 2 | 4 | 960 | 91.8 | 1.16 | 1.30 | 0.995 | 0.995 | 82.6 | 96.7 | 11.2 | 1597 |  |
| 3OOW | Complete |  | proteindiffraction.org | APS | 21-ID-D | MAR CCD | P 21 21 21 | 2 | 530 | 83.3 | 1.25 | 1.50 | 0.997 | 0.997 | 67.4 | 93.7 | 9.9 | 574 |  |
| 6BWT | Complete |  | proteindiffraction.org | APS | 21-ID-E | MARMOSAIC 225 mm CCD | P 21 21 21 | 1 | 250 | 89.8 | 1.75 | 2.12 | 0.994 | 0.994 | 75.0 | 98.7 | 4.0 | 151 |  |
| 3U09 | Complete |  | proteindiffraction.org | APS | 19-BM | ADSC QUANTUM 210 | P 1 | 1 | 419 | 12.5 | 1.48 |  | 0.025 |  | 36.9 |  | 1.3 | 2672 |  |
| 3O38 | Complete |  | proteindiffraction.org | ALS | 5.0.1 | ADSC QUANTUM 210r | P 1 | 1 | 199 | 18.5 | 1.60 |  | 0.102 |  | 50.4 |  | 1.8 | 250 |  |
| 5L0A | Complete |  | MX-RDR | BESSY | 14.3 | RAYONIX SX-165mm | F 2 2 2 | 4 | 240 | 81.0 | 1.67 | 2.20 | 0.938 | 0.933 | 57.1 | 80.2 | 3.5 | 248 |  |
| 7WAB | Complete |  | PDBj XRDA | PHOTON FACTORY | BL-1A | ADSC QUANTUM 270 | P 1 | 1 | 340 | 35.8 | 1.49 |  | 0.001 |  | 28.5 |  | 1.3 | 547 |  |
| 8HRZ | Complete |  | proteindiffraction.org | PHOTON FACTORY | BL-17A | ADSC QUANTUM 270 | P 1 21 1 | 1 | 360 | 90.5 | 2.06 | 2.51 | 0.999 | 0.999 | 66.6 | 95.4 | 6.7 | 638 |  |
| 5OOH | Complete |  | SBGrid | ESRF | ID23-1 | ADSC QUANTUM 315r | P 1 21 1 | 1 | 400 | 98.3 | 1.01 | 1.19 | 0.988 | 0.988 | 73.8 | 96.5 | 4.0 | 245 |  |
| 8UKW | Failed | find_spots | SBGrid | APS | 23-ID-B | MAR CCD 300 mm |  | 1 | 180 |  |  |  |  |  |  |  |  | 14 |  |
| 3MQD | Complete |  | proteindiffraction.org | ALS | 5.0.1 | ADSC QUANTUM Q315R | I 1 2 1 | 1 | 279 | 24.9 | 1.02 | 1.80 | 0.645 | 0.618 | 72.8 | 99.8 | 4.7 | 522 |  |
| 3MMT | Failed | import | proteindiffraction.org | ALS | 5.0.1 | ADSC QUANTUM Q315 |  |  |  |  |  |  |  |  |  |  |  | 2 |  |
| 4EED | Complete |  | SBGrid | CLSI | 08ID-1 | MARMOSAIC CCD300 | P 21 21 21 | 1 | 180 | 76.8 | 2.29 | 3.55 | 0.980 | 0.992 | 69.3 | 100.0 | 5.8 | 129 |  |
| 5K54 | Complete |  | MX-RDR | BESSY | 14.1 | RAYONIX MX-225 | I 41 2 2 | 12 | 600 | 85.0 | 1.38 | 1.58 | 0.997 | 0.997 | 78.9 | 97.1 | 7.6 | 387 |  |
| 3LV0 | Complete |  | proteindiffraction.org | ALS | 5.0.2 | ADSC QUANTUM 210r | P 1 | 1 | 220 | 36.8 | 1.38 |  | 0.100 |  | 55.8 |  | 2.2 | 252 |  |
| 8KG2 | Complete |  | proteindiffraction.org | PHOTON FACTORY | BL-17A | ADSC QUANTUM 210r | P 1 | 1 | 360 | 38.6 | 2.01 |  | 0.138 |  | 55.9 |  | 3.7 | 562 |  |
| 5J1I | Complete |  | Zenodo | ESRF | ID14-2 | ADSC QUANTUM 4 | C 1 2 1 | 1 | 360 | 94.6 | 2.09 | 2.78 | 0.999 | 1.000 | 63.1 | 99.4 | 6.8 | 113 |  |
| 3U8R | Complete |  | SBGrid | ESRF | ID14-1 | ADSC QUANTUM 210 | P 21 21 21 | 1 | 150 | 75.3 | 2.04 |  | 0.999 |  | 75.6 |  | 4.6 | 117 |  |
| 6ZRW | Complete |  | Zenodo | SLS | X06DA | MARMOSAIC 225 mm CCD | P 1 21 1 | 1 | 720 | 98.3 | 1.15 |  | 0.999 |  | 77.4 |  | 13.3 | 622 |  |
| 3K9W | Complete |  | proteindiffraction.org | CLSI | 08ID-1 | MAR scanner 300 mm plate | I 4 3 2 | 1 | 90 | 89.8 | 1.23 | 1.41 | 0.998 | 0.999 | 85.8 | 98.7 | 8.2 | 167 |  |
| 3KH1 | Complete |  | proteindiffraction.org | SSRL | BL9-1 | ADSC QUANTUM 315 | I 1 2 1 | 2 | 340 | 76.1 | 0.98 | 1.14 | 0.998 | 0.998 | 80.1 | 99.3 | 3.4 | 293 |  |
| 3INN | Complete |  | proteindiffraction.org | SSRL | BL12-2 | MARMOSAIC 325 mm CCD | P 31 2 1 | 1 | 300 | 73.7 | 1.52 | 1.76 | 0.996 | 0.996 | 81.1 | 97.3 | 6.9 | 455 |  |
| 6RYN | Complete |  | Other (manual) | DIAMOND | I04 | ADSC QUANTUM 315 | P 41 | 2 | 335 | 82.3 | 0.84 | 0.88 | 0.999 | 0.999 | 82.0 | 91.2 | 7.7 | 500 |  |
| 3GVG | Complete |  | proteindiffraction.org | APS | 23-ID-D | MAR scanner 300 mm plate | C 1 2 1 | 1 | 180 | 63.5 | 1.24 | 1.37 | 0.997 | 0.997 | 72.7 | 90.5 | 3.4 | 248 |  |
| 3HRP | Complete |  | proteindiffraction.org | SSRL | BL11-1 | MAR MAR325 | P 2 21 21 | 3 | 300 | 91.6 | 1.28 | 1.52 | 0.996 | 0.997 | 71.1 | 96.0 | 3.8 | 346 |  |
| 3GMT | Complete |  | proteindiffraction.org | NSLS | X8C | ADSC QUANTUM Q315r | P 1 21 1 | 1 | 360 | 40.8 | 1.57 | 1.82 | 0.998 | 0.998 | 67.9 | 91.6 | 6.6 | 225 |  |
| 3GSE | Failed | import | proteindiffraction.org | APS | 19-BM | SBC-3 |  |  |  |  |  |  |  |  |  |  |  | 2 |  |
| 3G48 | Complete |  | proteindiffraction.org | APS | 19-ID | ADSC QUANTUM Q315r | P 1 | 1 | 311 | 32.3 | 1.21 |  | 0.293 |  | 59.4 |  | 1.6 | 277 |  |
| 3FS2 | Complete |  | proteindiffraction.org | ALS | 4.2.2 | WESTBROOK NOIR | P 1 | 1 | 360 | 12.5 | 1.47 |  | 0.760 |  | 38.8 |  | 1.7 | 1872 |  |
| 3G68 | Failed | import | proteindiffraction.org | APS | 23-ID-B | MARMOSAIC 325 mm CCD |  |  |  |  |  |  |  |  |  |  |  | 3 |  |
| 3FEZ | Complete |  | proteindiffraction.org | APS | 23-ID-B | MAR MAR300 | P 6 2 2 | 3 | 285 | 49.4 | 1.62 | 1.93 | 0.992 | 0.992 | 65.3 | 91.0 | 15.8 | 333 |  |
| 5UNA | Complete |  | proteindiffraction.org | ESRF | ID14-4 | ADSC QUANTUM 315 | R 3 :H | 3 | 540 | 71.8 | 1.84 | 2.29 | 0.997 | 0.998 | 74.8 | 99.7 | 4.5 | 601 |  |
| 3EK2 | Complete |  | proteindiffraction.org | APS | 23-ID-B | MAR 300 | P 1 | 1 | 180 | 44.9 | 1.33 |  | 0.021 |  | 61.3 |  | 1.9 | 472 |  |
| 3E4V | Complete |  | proteindiffraction.org | SSRL | BL1-5 | ADSC QUANTUM 315 | P 21 21 21 | 1 | 300 | 91.5 | 1.20 | 1.27 | 0.998 | 0.998 | 80.6 | 91.8 | 4.9 | 181 |  |
| 3CJM | Complete |  | proteindiffraction.org | SSRL | BL1-5 | ADSC QUANTUM 315r | P 41 21 2 | 3 | 600 | 96.4 | 1.27 | 1.37 | 0.998 | 0.998 | 73.7 | 86.6 | 7.0 | 445 |  |
| 6RYG | Complete |  | Other (manual) | DIAMOND | I03 | ADSC QUANTUM 315 | P 41 | 2 | 335 | 89.2 | 0.97 |  | 0.997 |  | 81.8 |  | 8.6 | 444 |  |
| 5OPE | Complete |  | SBGrid | ESRF | ID14-4 | ADSC QUANTUM 315r | C 2 2 21 | 1 | 360 | 65.0 | 1.97 | 2.10 | 0.981 | 0.981 | 70.6 | 82.2 | 5.8 | 99 |  |
| 2QZC | Failed | symmetry | proteindiffraction.org | SSRL | BL1-5 | ADSC QUANTUM 4 | P 1 | 6 | 820 | 95.5 |  |  |  |  |  |  |  | 605 |  |
| 9FHC | Complete |  | Zenodo | SLS | X06SA | MARRESEARCH | I 2 3 | 1 | 400 | 93.6 | 1.67 | 1.94 | 0.998 | 0.998 | 79.1 | 96.4 | 18.2 | 764 |  |
| 2QT1 | Complete |  | proteindiffraction.org | APS | 23-ID-D | MARMOSAIC 325 mm CCD | C 2 2 21 | 1 | 360 | 75.2 | 0.97 | 1.14 | 0.996 | 0.996 | 76.3 | 95.5 | 6.9 | 262 |  |
| 2QFZ | Complete |  | proteindiffraction.org | NSLS | X12B | ADSC QUANTUM 4 | P 1 2 1 | 1 | 352 | 39.1 | 1.59 | 2.13 | 0.836 | 0.878 | 68.1 | 99.8 | 4.9 | 182 |  |
| 2QSY | Complete |  | proteindiffraction.org | APS | 17-ID | ADSC QUANTUM 4 | C 2 2 21 | 1 | 360 | 45.9 | 1.44 | 1.59 | 0.996 | 0.996 | 71.1 | 88.7 | 6.4 | 92 |  |
| 3H50 | Complete |  | proteindiffraction.org | SSRL | BL11-1 | ADSC QUANTUM 315 | I 1 2 1 | 5 | 1092 | 40.7 | 1.21 | 1.25 | 0.994 | 0.994 | 69.7 | 76.5 | 4.3 | 349 |  |
| 2HLZ | Complete |  | proteindiffraction.org | APS | 17-ID | ADSC QUANTUM 210 | P 1 | 1 | 720 | 94.2 | 1.44 | 1.55 | 0.998 | 0.998 | 60.3 | 73.5 | 3.9 | 187 |  |
| 5WDE | Complete |  | proteindiffraction.org | CHESS | F1 | ADSC QUANTUM 4 | I 1 2 1 | 1 | 512 | 27.7 | 1.31 |  | 0.082 |  | 62.3 |  | 2.0 | 383 |  |
| 6RT3 | Complete |  | SBGrid | ESRF | ID29 | ADSC QUANTUM 315 | P 41 21 2 | 1 | 120 | 94.7 | 1.01 |  | 0.995 |  | 90.2 |  | 7.4 | 206 |  |
| 5B48 | Complete |  | PDBj XRDA | PHOTON FACTORY | BL-5A | ADSC QUANTUM 4r | P 1 | 1 | 230 | 23.9 | 1.69 |  | 0.133 |  | 43.5 |  | 1.5 | 406 |  |
| 2G42 | Complete |  | proteindiffraction.org | ALS | 8.2.1 | ADSC QUANTUM 210 | P 1 2 1 | 3 | 540 | 60.7 | 1.86 | 2.24 | 0.995 | 0.997 | 64.8 | 92.8 | 3.2 | 94 |  |
| 2QMQ | Failed | symmetry | proteindiffraction.org | ALS | 8.3.1 | ADSC QUANTUM 210 | P 1 | 3 | 641 | 56.7 |  |  |  |  |  |  |  | 107 |  |
| 2H0V | Complete |  | proteindiffraction.org | ALS | 8.3.1 | ADSC QUANTUM | P 21 21 21 | 1 | 184 | 94.7 | 2.70 |  | 0.997 |  | 66.2 |  | 3.2 | 114 |  |
| 4XYD | Complete |  | Zenodo | ESRF | ID23-1 | ADSC QUANTUM 315 | P 2 21 21 | 1 | 180 | 98.3 | 2.31 | 2.50 | 0.985 | 0.985 | 72.4 | 85.8 | 5.8 | 107 |  |
| 2F8J | Complete |  | proteindiffraction.org | SSRL | BL9-2 | ADSC QUANTUM 315 | P 2 21 21 | 2 | 191 | 86.2 | 1.80 | 2.03 | 0.992 | 0.992 | 71.2 | 89.1 | 3.3 | 175 |  |
| 1VR5 | Complete |  | proteindiffraction.org | ALS | 8.2.1 | ADSC | P 21 2 21 | 4 | 1360 | 93.3 | 2.09 | 2.18 | 0.993 | 0.993 | 67.5 | 75.8 | 3.0 | 667 |  |
| 1VR7 | Complete |  | proteindiffraction.org | ALS | 8.3.1 | ADSC | R 3 :H | 4 | 630 | 97.8 | 1.81 |  | 0.995 |  | 65.5 |  | 2.4 | 276 |  |
| 1VQR | Complete |  | proteindiffraction.org | ALS | 5.0.2 | ADSC | I 1 2 1 | 2 | 180 | 73.8 | 1.71 | 2.13 | 0.980 | 0.980 | 59.3 | 93.5 | 2.8 | 122 |  |
| 2FYX | Complete |  | proteindiffraction.org | ALS | 5.0.3 | ADSC QUANTUM 4 | P 1 | 2 | 137 | 40.7 | 1.35 |  | 0.016 |  | 40.2 |  | 1.4 | 172 |  |
| 6RYM | Complete |  | Other (manual) | SRS | PX10.1 | MAR CCD 165 mm | P 1 2 1 | 2 | 130 | 96.1 | 1.46 |  | 0.929 |  | 71.5 |  | 2.9 | 134 |  |
| 1U9C | Failed | import | SBGrid | APS | 19-ID | CUSTOM-MADE |  |  |  |  |  |  |  |  |  |  |  | 1 |  |
| 6Y28 | Complete |  | proteindiffraction.org | BESSY | 14.1 | MARRESEARCH | P 21 21 21 | 1 | 99 | 71.9 | 1.32 | 1.62 | 0.974 | 0.972 | 71.3 | 96.6 | 3.4 | 107 |  |
| 1VP2 | Complete |  | proteindiffraction.org | ALS | 5.0.1 | ADSC | P 1 | 1 | 241 | 22.5 | 1.57 |  | -0.002 |  | 23.4 |  | 1.2 | 281 |  |
| 2FNO | Failed | import | proteindiffraction.org | APS | 19-BM | SBC |  |  |  |  |  |  |  |  |  |  |  | 1 |  |
| 2FM1 | Failed | import | proteindiffraction.org | APS | 19-BM | APS-1 |  |  |  |  |  |  |  |  |  |  |  | 1 |  |
| 1VPA | Failed | import | proteindiffraction.org | APS | 19-BM | APS |  |  |  |  |  |  |  |  |  |  |  | 1 |  |
| 1VPX | Failed | symmetry | proteindiffraction.org | ALS | 5.0.3 | ADSC | P 1 | 3 | 341 | 29.9 |  |  |  |  |  |  |  | 538 |  |
| 1VKH | Complete |  | proteindiffraction.org | APS | 8-BM | ADSC | P 1 21 1 | 8 | 1098 | 87.7 | 1.43 | 1.51 | 0.999 | 0.999 | 68.3 | 79.0 | 19.1 | 591 |  |
| 1VJO | Failed | import | proteindiffraction.org | APS | 14-BM-C | MARRESEARCH |  |  |  |  |  |  |  |  |  |  |  | 2 |  |
| 1VQU | Complete |  | proteindiffraction.org | ALS | 8.2.2 | ADSC | P 1 | 4 | 190 | 94.7 | 1.39 | 1.70 | 0.996 | 0.996 | 58.5 | 89.1 | 1.8 | 178 |  |
| 1YQ2 | Failed | import | SBGrid | ESRF | ID29 | ADSC QUANTUM 210 |  |  |  |  |  |  |  |  |  |  |  | 3 |  |
| 1VRG | Failed | import | proteindiffraction.org | APS | 19-ID | APS |  |  |  |  |  |  |  |  |  |  |  | 2 |  |
| 2GRJ | Failed | import | proteindiffraction.org | APS | 14-ID-B | MAR CCD 165 mm |  |  |  |  |  |  |  |  |  |  |  | 2 |  |
| 1WQ6 | Complete |  | proteindiffraction.org | NSLS | X9B | ADSC QUANTUM 4 | P 1 | 1 | 250 | 15.1 | 1.54 |  | 0.124 |  | 51.1 |  | 1.5 | 194 |  |
| 1O5K | Failed | symmetry | proteindiffraction.org | APS | 14-BM-C | ADSC QUANTUM 4 | P 1 | 5 | 275 | 66.7 |  |  |  |  |  |  |  | 328 |  |
| 1V9Z | Failed | find_spots | SBGrid | SPRING-8 | BL44XU | MACSCIENCE |  | 1 | 103 |  |  |  |  |  |  |  |  | 4 |  |
| 1V9Y | Failed | find_spots | SBGrid | SPRING-8 | BL41XU | MARRESEARCH |  | 2 | 240 |  |  |  |  |  |  |  |  | 4 |  |
| 1O1X | Complete |  | proteindiffraction.org | SSRL | BL9-1 | ADSC QUANTUM 4 | I 2 2 2 | 3 | 270 | 72.8 | 1.71 |  | 0.996 |  | 79.6 |  | 4.2 | 171 |  |
| 1O22 | Complete |  | proteindiffraction.org | ALS | 5.0.2 | ADSC QUANTUM | P 41 21 2 | 5 | 377 | 72.5 | 1.31 | 1.96 | 0.985 | 0.991 | 64.6 | 83.8 | 2.7 | 238 |  |
| 2AFB | Complete |  | proteindiffraction.org | SSRL | BL9-2 | ADSC QUANTUM 4 | R 3 2 :H | 3 | 492 | 83.7 | 1.71 | 2.03 | 0.993 | 0.994 | 77.3 | 97.9 | 3.9 | 303 |  |
| 1ZLF | Failed | import | SBGrid | ESRF | ID14-1 | MARRESEARCH |  |  |  |  |  |  |  |  |  |  |  | 1 |  |
| 1M0B | Failed | find_spots | SBGrid | ESRF | ID29 | MARRESEARCH |  | 4 | 150 |  |  |  |  |  |  |  |  | 3 |  |
| 1ZSF | Failed | import | SBGrid | ELETTRA | 5.2R | MARRESEARCH |  |  |  |  |  |  |  |  |  |  |  | 2 |  |

Snapshot of 2026-11-22 00:29 UTC.
