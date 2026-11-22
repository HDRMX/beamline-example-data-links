#!/bin/bash
# Run the standard pipeline on one downloaded entry.  DO NOT EDIT.
#   usage: process_entry.sh ENTRY
# Works on the current round (ROUND = $HDRMX_ROUND or the content of ROOT/CURRENT_ROUND):
# claims the entry (Downloaded -> In-progress) in rounds/ROUND/status.tsv, selects the
# input with the fixed rule in find_inputs.py, runs rounds/ROUND/tldr.sh once in
# entries/ENTRY/rounds/ROUND/proc with the DIALS build set up by rounds/ROUND/env.sh,
# writes entries/ENTRY/rounds/ROUND/results.csv and sets the final status.
set -u
ROOT=${HDRMX_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}
export HDRMX_ROOT=$ROOT
export HDRMX_ROUND=${HDRMX_ROUND:-$(cat "$ROOT/CURRENT_ROUND")}
ID=${1:?usage: process_entry.sh ENTRY}
RD=$ROOT/rounds/$HDRMX_ROUND
E=$ROOT/entries/$ID
W=$E/rounds/$HDRMX_ROUND

if [ -e "$RD/FROZEN" ]; then echo "FAILED: round $HDRMX_ROUND is frozen"; exit 1; fi
HDRMX_PYTHON=dials.python
. "$RD/env.sh" || { echo "FAILED: cannot source $RD/env.sh"; exit 1; }

"$ROOT/bin/status" claim "$ID" "Downloaded" "In-progress" || exit 1

if [ -e "$W/proc" ]; then
  "$ROOT/bin/status" set "$ID" "Failed" "proc/ already existed; not rerun"
  echo "FAILED: $W/proc already exists; an entry is processed only once per round"; exit 1
fi
mkdir -p "$W/proc" && cd "$W/proc" || exit 1

python3 "$ROOT/bin/find_inputs.py" "$E/data" "$ID" > import_args.txt
mapfile -t ARGS < import_args.txt

if [ ${#ARGS[@]} -eq 0 ]; then
  VERDICT="FAILED at input selection (no importable images found)"
else
  VERDICT=$("$RD/tldr.sh" "${ARGS[@]}")
fi

"$HDRMX_PYTHON" "$ROOT/bin/collect_results.py" "$ID" > collect.log 2>&1 \
  || echo "warning: collect_results.py failed, see $W/proc/collect.log"

if [ "$VERDICT" = "COMPLETE" ]; then
  "$ROOT/bin/status" set "$ID" "Complete" ""
else
  "$ROOT/bin/status" set "$ID" "Failed" "$VERDICT"
fi
echo "$ID: $VERDICT"
