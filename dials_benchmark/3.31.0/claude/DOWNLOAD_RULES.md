# Rules for download agents

Root of the project: `/path/to/project` (called `ROOT` below).

## Goal

Fetch the raw diffraction images of **one entry** from its public repository
into `ROOT/entries/ENTRY/data/`, unpacked and otherwise unchanged, so that a
separate agent can later process it with a fixed DIALS pipeline. You do no
processing and run no `dials.*` commands.

## What you do

1. Start the download (this returns immediately):

       ROOT/bin/job start ENTRY download ROOT/bin/download_entry.py ENTRY

   `download_entry.py` claims the entry in the status file, downloads,
   unpacks archives, checks that data arrived and sets the status to
   `Downloaded` or `Download failed`. Its output is in
   `ROOT/entries/ENTRY/download.job.log`.
2. Wait for it with a normal foreground Bash call, timeout 600000 ms:

       ROOT/bin/job wait ENTRY download

   It blocks for up to nine minutes and prints `RUNNING` or `EXITED <code>`
   followed by the last log lines. While it prints `RUNNING`, call it again.
   Downloads can take many hours; keep calling it and do nothing else in
   between. Do not use background tasks, monitors, sleep loops or progress
   checks (`du`, `ls`, `tail`), and do not report or return any result while
   it is `RUNNING`.
3. `EXITED 0`: done. Report status `Downloaded` with the final
   `DOWNLOADED: ...` line.
4. `EXITED 1` (download failed): read `download.job.log`. If the cause looks
   transient (timeout, connection reset, 5xx), repeat steps 1 and 2 once. If
   it fails again, or the cause is permanent (404, login required, no data
   files in the deposition), leave the status as `Download failed` and report
   the reason in one or two lines.
5. `EXITED 3` (no automatic method for this repository): download it
   yourself. The link is in `ROOT/entries.tsv`. Work out how the repository
   serves files (landing page, API, rsync, direct links) and fetch **all raw
   image files of the deposition** into `ROOT/entries/ENTRY/data/`, keeping
   the repository's folder structure. Run every long transfer through the
   same helper so it survives and can be waited for:

       ROOT/bin/job start ENTRY fetch <curl or rsync command>
       ROOT/bin/job wait ENTRY fetch

   (use a different name than `fetch` for each additional transfer, or a
   small shell script of your own in `ROOT/entries/ENTRY/` that fetches all
   files). When everything has arrived, run

       ROOT/bin/job start ENTRY finish ROOT/bin/download_entry.py --finish ENTRY
       ROOT/bin/job wait ENTRY finish

   which unpacks, verifies and sets the status. If the data cannot be had
   without credentials, is not there, or is larger than 500 GB in total, run
   `ROOT/bin/status set ENTRY "Download failed" "<short reason, with the size if known>"`
   and report.

## Rules

- Download everything that is raw image data for the deposition. Do not pick
  a subset of sweeps. Processed files (MTZ, logs, PDFs) may be skipped or
  kept; they are ignored later.
- Do not rename, convert, decompress (`.cbf.gz`, `.img.bz2` stay as they are)
  or reorganise image files. Only archives (tar, zip) are unpacked, and
  `download_entry.py` does that.
- Only write inside `ROOT/entries/ENTRY/`. Do not touch other entries.
- Change `status.tsv` only through `ROOT/bin/status`. Never set `Downloaded`
  by hand; `--finish` does it after verifying.
- Do not edit anything in `ROOT/bin/`, `tldr.sh` or `entries.tsv`.
- Do not send any personal or project information to the repositories; no
  logins, no registration forms.
- Report exactly once, when the entry's status is `Downloaded` or
  `Download failed`: at most three lines (status, file count and size, any
  problem).
