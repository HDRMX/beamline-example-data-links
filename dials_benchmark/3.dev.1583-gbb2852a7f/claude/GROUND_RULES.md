# Ground rules for processing agents

Root of the project: `/path/to/project` (called `ROOT` below).

## Goal

We are benchmarking DIALS. About 470 public raw-data depositions are each put
through **one identical, fixed pipeline** (`ROOT/tldr.sh`) exactly once, and the
outcome is recorded whether it succeeds or fails. The value of the benchmark
comes from every entry being treated the same way. A failure is a valid,
useful result. A rescued dataset is a corrupted data point.

You process **one entry**. You know nothing about other entries and must not
look at them.

## What you do

1. Start the run, once (this returns immediately):

       ROOT/bin/job start ENTRY process ROOT/bin/process_entry.sh ENTRY

   `process_entry.sh` does everything: it claims the entry in the status
   file, selects the input images with a fixed rule, runs `tldr.sh` in
   `ROOT/entries/ENTRY/proc/`, writes `ROOT/entries/ENTRY/results.csv`, and
   sets the final status.
2. Wait for it with a normal foreground Bash call, timeout 600000 ms:

       ROOT/bin/job wait ENTRY process

   It blocks for up to nine minutes and prints `RUNNING` or `EXITED <code>`
   followed by the last log lines. While it prints `RUNNING`, call it again.
   A run can take from minutes to many hours; keep calling it, and do
   nothing else in between. Do not use background tasks, monitors or sleep
   loops, and do not report or return any result while it is `RUNNING`.
3. When it prints `EXITED`, report once, in at most five lines: the script's
   final line (`ENTRY: COMPLETE` or `ENTRY: FAILED at <step> ...`), and,
   copied from `results.csv`, the space group, `overall_d_min`,
   `suggested_d_min`, `overall_cc_half` and `total_seconds`. If it failed,
   also quote the last error line of `proc/tldr.log`, without
   interpretation. The reported status is `Complete` or `Failed` as shown by
   `ROOT/bin/status get ENTRY`; use `Not run` only if the script refused to
   start.

## What you must not do

- Do not edit `tldr.sh`, anything in `ROOT/bin/`, `entries.tsv` or `status.tsv`.
- Do not run any `dials.*` command yourself, and do not rerun the pipeline
  or any step of it, with or without different options.
- Do not try to diagnose, fix or work around a processing failure. No masks,
  no resolution cuts, no changed space group, no excluded images or sweeps,
  no altered input selection.
- Do not move, rename, delete or edit anything in `data/` or `proc/`.
- Do not write or correct `results.csv` by hand.
- Do not touch any other entry's folder.
- If `process_entry.sh` refuses to start (the entry is not in status
  `Downloaded`, or `proc/` already exists), stop and report that. Do not
  change the status to get around it.

Infrastructure problems are different from processing problems: if the script
itself cannot run (command not found, disk full, permission denied), do not
fix it either. Report the exact message and stop.

## Layout

    ROOT/
      GROUND_RULES.md       this file
      DOWNLOAD_RULES.md     rules for download agents
      tldr.sh               the fixed pipeline
      entries.tsv           one line per entry: facility, beamline, detector, link
      status.tsv            status of every entry (changed only through bin/status)
      bin/                  helper scripts
      entries/ENTRY/
        data/               raw images as downloaded (read-only for you)
        download.log
        process.job.log     output of process_entry.sh
        proc/               all DIALS output of the single run
          import_args.txt   what was handed to dials.import
          steps.tsv         step, exit code, seconds
          tldr.log          full stdout/stderr
        results.csv         header + one row of metrics

## Status values

`Not started` -> `Downloading` -> `Downloaded` -> `In-progress` -> `Complete` or `Failed`
(`Download failed` if the data could not be fetched).

`Complete` means the pipeline ran through `dials.merge`. `Failed` means it
stopped at a step, which is named in the status note and in `results.csv`.
