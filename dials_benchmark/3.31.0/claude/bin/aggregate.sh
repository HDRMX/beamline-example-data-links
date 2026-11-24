#!/bin/bash
# Concatenate every entries/*/rounds/ROUND/results.csv into ROOT/rounds/ROUND/all_results.csv
# (ROUND = $HDRMX_ROUND or the content of ROOT/CURRENT_ROUND).  Refuses on a frozen round.
ROOT=${HDRMX_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}
ROUND=${HDRMX_ROUND:-$(cat "$ROOT/CURRENT_ROUND")}
[ -e "$ROOT/rounds/$ROUND/FROZEN" ] && { echo "round $ROUND is frozen"; exit 1; }
out=$ROOT/rounds/$ROUND/all_results.csv
first=1
for f in "$ROOT"/entries/*/rounds/"$ROUND"/results.csv; do
  [ -e "$f" ] || continue
  if [ $first -eq 1 ]; then head -1 "$f" > "$out"; first=0; fi
  tail -n +2 "$f" >> "$out"
done
echo "$(($(wc -l < "$out") - 1)) entries in $out"
