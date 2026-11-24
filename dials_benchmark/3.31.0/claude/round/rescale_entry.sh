#!/bin/bash
# One-off for the 2026-11-24 change of tldr.sh (see HISTORY.md): re-run only the
# scaling portion of an entry that had completed with the original, single-pass script.
#   usage: rescale_entry.sh ENTRY
# The existing uncut scaling output becomes the first pass (scale_all); the second
# pass, export and merge are run exactly as in tldr.sh.
set -u
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
export HDRMX_ROOT=$ROOT HDRMX_ROUND=3.31.0
ID=${1:?usage: rescale_entry.sh ENTRY}
RD=$ROOT/rounds/$HDRMX_ROUND
W=$ROOT/entries/$ID/rounds/$HDRMX_ROUND
HDRMX_PYTHON=dials.python
. "$RD/env.sh" || exit 1
cd "$W/proc" || { echo "$ID: no proc directory"; exit 1; }

if [ -e dials.scale_all.log ] || [ -e before_rescale ]; then echo "$ID: already rescaled, skipped"; exit 0; fi
if [ "$(awk 'NR>1 && $2==0' steps.tsv | wc -l)" -ne 9 ]; then echo "$ID: original run not complete, skipped"; exit 0; fi

mkdir before_rescale
cp -p steps.tsv tldr.log ../results.csv before_rescale/
mv scaled.mtz merged.mtz dials.export.log dials.merge.log dials.merge.html before_rescale/ 2>/dev/null
[ -e collect.log ] && mv collect.log before_rescale/
mv scaled.expt scaled_all.expt
mv scaled.refl scaled_all.refl
mv dials.scale.log dials.scale_all.log
mv dials.scale.html dials.scale_all.html
awk -F'\t' 'BEGIN{OFS="\t"} NR==1 || $1!="export" && $1!="merge" {if($1=="scale")$1="scale_all"; print}' before_rescale/steps.tsv > steps.tsv

exec 3>&1
exec >> tldr.log 2>&1
echo
echo "### scaling portion re-run with the two-pass tldr.sh, started $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "### (first pass = the uncut scaling above; its output files were renamed to scaled_all.*, dials.scale_all.*)"

VERDICT=COMPLETE
run () {
  [ "$VERDICT" = COMPLETE ] || return
  local name=$1; shift
  local t0=$SECONDS
  echo
  echo "### $*"
  "$@"
  local rc=$?
  printf '%s\t%d\t%d\n' "$name" "$rc" "$((SECONDS - t0))" >> steps.tsv
  if [ "$rc" -ne 0 ]; then
    echo "### FAILED at $name (exit code $rc)"
    VERDICT="FAILED at $name (exit code $rc)"
  fi
}

DMIN=$(sed -n 's/^Resolution limit suggested from CC[^ ]* fit.*: *\([0-9.][0-9.]*\) *$/\1/p' dials.scale_all.log | tail -1)
echo
echo "### suggested resolution limit: ${DMIN:-none}"

if [ -n "$DMIN" ]; then
  run scale    dials.scale symmetrized.expt symmetrized.refl d_min="$DMIN"
else
  run scale    dials.scale symmetrized.expt symmetrized.refl
fi
run export     dials.export scaled.expt scaled.refl
run merge      dials.merge scaled.expt scaled.refl

echo
echo "### finished $(date -u +%Y-%m-%dT%H:%M:%SZ)"
exec >&3 2>&1

"$HDRMX_PYTHON" "$ROOT/bin/collect_results.py" "$ID" > collect.log 2>&1 || echo "$ID: warning, collect_results.py failed"
if [ "$VERDICT" = COMPLETE ]; then
  "$ROOT/bin/status" set "$ID" "Complete" ""
else
  "$ROOT/bin/status" set "$ID" "Failed" "$VERDICT"
fi
echo "$ID: $VERDICT (d_min ${DMIN:-none})"
