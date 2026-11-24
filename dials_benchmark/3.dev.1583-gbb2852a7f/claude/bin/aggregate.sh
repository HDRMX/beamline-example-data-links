#!/bin/bash
# Concatenate every entries/*/results.csv into ROOT/all_results.csv
ROOT=${HDRMX_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}
out=$ROOT/all_results.csv
first=1
for f in "$ROOT"/entries/*/results.csv; do
  [ -e "$f" ] || continue
  if [ $first -eq 1 ]; then head -1 "$f" > "$out"; first=0; fi
  tail -n +2 "$f" >> "$out"
done
echo "$(($(wc -l < "$out") - 1)) entries in $out"
