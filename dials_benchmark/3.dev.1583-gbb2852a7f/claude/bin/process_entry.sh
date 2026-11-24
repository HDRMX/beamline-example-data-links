#!/bin/bash
# Run the standard pipeline on one downloaded entry.  DO NOT EDIT.
#   usage: process_entry.sh ENTRY
# Claims the entry (Downloaded -> In-progress), selects the input with the
# fixed rule in find_inputs.py, runs tldr.sh once in entries/ENTRY/proc,
# writes entries/ENTRY/results.csv and sets the final status.
set -u
ROOT=${HDRMX_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}
ID=${1:?usage: process_entry.sh ENTRY}
E=$ROOT/entries/$ID

"$ROOT/bin/status" claim "$ID" "Downloaded" "In-progress" || exit 1

if [ -e "$E/proc" ]; then
  "$ROOT/bin/status" set "$ID" "Failed" "proc/ already existed; not rerun"
  echo "FAILED: $E/proc already exists; an entry is processed only once"; exit 1
fi
mkdir -p "$E/proc" && cd "$E/proc" || exit 1

python3 "$ROOT/bin/find_inputs.py" "$E/data" "$ID" > import_args.txt
mapfile -t ARGS < import_args.txt

if [ ${#ARGS[@]} -eq 0 ]; then
  VERDICT="FAILED at input selection (no importable images found)"
else
  VERDICT=$("$ROOT/tldr.sh" "${ARGS[@]}")
fi

dials.python "$ROOT/bin/collect_results.py" "$ID" > collect.log 2>&1 \
  || echo "warning: collect_results.py failed, see $E/proc/collect.log"

if [ "$VERDICT" = "COMPLETE" ]; then
  "$ROOT/bin/status" set "$ID" "Complete" ""
else
  "$ROOT/bin/status" set "$ID" "Failed" "$VERDICT"
fi
echo "$ID: $VERDICT"
