# History of this round

- 2026-11-21: all entries processed with the original tldr.sh (one uncut dials.scale).
- 2026-11-22: frozen.
- 2026-11-24: unfrozen. tldr.sh changed to scale twice: once uncut to obtain the
  resolution limit DIALS suggests from its CC1/2 fit, then again from the unscaled
  data with d_min set to that limit, followed by export and merge of the cut data.
  For the entries that had completed, only this scaling portion was re-run
  (rescale_entry.sh): the existing uncut scaling output was renamed to the first-pass
  names (scaled_all.*, dials.scale_all.*), and the previous export/merge output,
  steps.tsv, tldr.log and results.csv were kept in proc/before_rescale/.
  Steps import to symmetry were not re-run. Step times of those steps and of the
  first scaling pass are from 2026-11-21.
- 2026-11-24: the suggested_* and suggested_outer_* statistics columns were removed from
  results.csv and all_results.csv (81 columns instead of 109); overall_* already describes
  the data cut at the suggested limit. suggested_d_min_cc_half_fit, the limit applied, is kept.
