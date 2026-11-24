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
# d_min=auto makes dials.scale cut the data at its own estimated resolution
# limit (CC1/2 fit crossing 0.3); it is the same fixed option for every entry.
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
run scale      dials.scale symmetrized.expt symmetrized.refl d_min=auto
run export     dials.export scaled.expt scaled.refl
run merge      dials.merge scaled.expt scaled.refl

echo
echo "### finished $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "COMPLETE" >&3
