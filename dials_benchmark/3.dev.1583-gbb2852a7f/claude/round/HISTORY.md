# History of this round

- 2026-11-19 to 2026-11-21: all entries processed; frozen 2026-11-21.
- 2026-11-24: unfrozen to bring the results table and report to the current column
  convention. No processing was re-run; every value comes from the existing logs.
  - The suggested_* and suggested_outer_* statistics columns were removed from
    results.csv and all_results.csv (81 columns instead of 109). dials.scale d_min=auto
    already cut the data, so overall_* describes the cut data.
  - suggested_d_min_cc_half_fit now holds the limit that was applied, read from the
    "Applying auto resolution cut at" line of dials.scale.log (empty where no cut was
    applied). It previously held a further suggestion printed for the already cut data.
  - The report now has one set of statistics columns; the "no cutoff" comparison columns
    from the earlier run without d_min=auto were removed. That earlier table is still in
    all_results_no_dmin.csv.
  - The tables as they were before this change are in all_results_109_columns.csv.
  - Four rows whose dials_version read "DIALS (2018)" (the citation line of a log, picked up
    by mistake) were corrected to the version printed by dials.version in the same tldr.log.
