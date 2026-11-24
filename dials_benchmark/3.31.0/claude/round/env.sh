# Environment of this round (sourced by bin/process_entry.sh): DIALS 3.31.0 release build.
. "$HDRMX_ROOT/builds/dials_3.31.0/setpaths.sh"
HDRMX_PYTHON=cctbx.python
export HDRMX_STEPS="import find_spots index refine integrate symmetry scale_all scale export merge"
export HDRMX_DROP_GROUPS="suggested suggested_outer"
