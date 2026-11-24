"""Write entries/<ENTRY>/results.csv (header + one row) from the DIALS output in proc/.

    dials.python collect_results.py ENTRY [PROC_DIR]

Every value is read from the logs and model files of the single standard run;
anything that is missing (e.g. because a step failed) is left empty.
Merging statistics come from dials.merge.log (dials.scale.log if merge did not run).
Column groups:
    overall_*          all scaled data
    overall_outer_*    highest-resolution bin of all scaled data
    suggested_*        data cut at the CC1/2=0.3 limit suggested by DIALS
    suggested_outer_*  highest-resolution shell of that cut
"""
import csv
import os
import re
import sys

ROOT = os.environ.get("HDRMX_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEPS = ["import", "find_spots", "index", "refine", "integrate", "symmetry", "scale", "export", "merge"]
SUMMARY_ROWS = [
    ("High resolution limit", "d_min"),
    ("Low resolution limit", "d_max"),
    ("Completeness", "completeness"),
    ("Multiplicity", "multiplicity"),
    ("I/sigma", "i_over_sigma"),
    ("Rmerge(I)", "rmerge"),
    ("Rmeas(I)", "rmeas"),
    ("Rpim(I)", "rpim"),
    ("CC half", "cc_half"),
    ("Anomalous completeness", "anom_completeness"),
    ("Anomalous multiplicity", "anom_multiplicity"),
    ("Anomalous correlation", "anom_correlation"),
    ("Total observations", "n_obs"),
    ("Total unique", "n_unique"),
]
METRICS = [m for _, m in SUMMARY_ROWS]
GROUPS = ["overall", "overall_outer", "suggested", "suggested_outer"]
# dials.scale d_min=auto already cuts at the suggested limit, so the unused groups are
# listed in HDRMX_DROP_GROUPS (env.sh) and their columns are left out of results.csv
DROP_GROUPS = os.environ.get("HDRMX_DROP_GROUPS", "").split()

COLUMNS = (
    ["entry", "facility", "beamline", "detector", "link", "deposition_version",
     "pipeline_status", "failed_step", "dials_version", "total_seconds"]
    + ["seconds_" + s for s in STEPS]
    + ["n_import_args", "image_format", "n_sweeps_imported", "n_images", "oscillation_deg",
       "total_rotation_deg", "wavelength",
       "n_strong_spots", "n_sweeps_indexed", "n_crystals_indexed", "n_indexed_spots", "pct_indexed",
       "refine_n_experiments", "refine_rmsd_x_px", "refine_rmsd_y_px", "refine_rmsd_z_images",
       "n_integrated", "n_experiments_integrated",
       "symmetry_laue_group", "symmetry_laue_probability",
       "n_experiments_scaled", "error_model_a", "error_model_b",
       "model_source", "space_group", "cell_a", "cell_b", "cell_c", "cell_alpha", "cell_beta", "cell_gamma",
       "stats_source", "suggested_d_min_cc_half_fit", "wilson_b"]
    + ["%s_%s" % (g, m) for g in GROUPS if g not in DROP_GROUPS for m in METRICS]
)


def read(path):
    try:
        with open(path, errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def last(pattern, text, group=1):
    m = re.findall(pattern, text, flags=re.M)
    if not m:
        return ""
    x = m[-1]
    return x if isinstance(x, str) else x[group - 1]


def num(tok):
    tok = tok.rstrip("*")
    try:
        float(tok)
        return tok
    except ValueError:
        return None


def merging_stats(text, row):
    """Parse the last by-bin table and the last summary table of a scale/merge log."""
    lines = text.splitlines()
    # ---- by-resolution-bin table: last bin row before the overall row
    starts = [i for i, l in enumerate(lines) if "Merging statistics by resolution bin" in l]
    if starts:
        rows = []
        for l in lines[starts[-1] + 1:]:
            t = l.split()
            if not t:
                if rows:
                    break
                continue
            if t[0] == "d_max":
                continue
            vals = [num(x) for x in t]
            if len(vals) >= 14 and all(v is not None for v in vals[:14]):
                rows.append(vals)
            elif rows:
                break
        if len(rows) >= 2:
            b = rows[-2]  # rows[-1] is the overall line
            keys = ["d_max", "d_min", "n_obs", "n_unique", "multiplicity", "completeness", None,
                    "i_over_sigma", "rmerge", "rmeas", "rpim", None, "cc_half", "anom_correlation"]
            for k, v in zip(keys, b):
                if k:
                    row["overall_outer_" + k] = v
    # ---- summary table
    starts = [i for i, l in enumerate(lines) if "Summary of merging statistics" in l]
    if not starts:
        return
    i = starts[-1] + 1
    while i < len(lines) and not lines[i].split():
        i += 1
    if i >= len(lines):
        return
    headers = lines[i].split()
    n = len(headers)
    table = {}
    for l in lines[i + 1:]:
        t = l.split()
        if not t:
            break
        vals = [num(x) for x in t[-n:]]
        if len(t) > n and all(v is not None for v in vals):
            table[" ".join(t[:-n])] = dict(zip(headers, vals))
    for label, metric in SUMMARY_ROWS:
        r = table.get(label, {})
        row["overall_" + metric] = r.get("Overall", "")
        if "Suggested" in headers:
            row["suggested_" + metric] = r.get("Suggested", "")
            row["suggested_outer_" + metric] = r.get("High", "")
        elif not row.get("overall_outer_" + metric):
            row["overall_outer_" + metric] = r.get("High", "")


def load_expts(path):
    from dxtbx.model.experiment_list import ExperimentListFactory
    return ExperimentListFactory.from_json_file(path, check_format=False)


def main():
    entry = sys.argv[1]
    proc = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "entries", entry, "proc")
    out = os.path.join(os.path.dirname(os.path.abspath(proc)), "results.csv") if len(sys.argv) <= 2 \
        else os.path.join(proc, "results.csv")
    P = lambda name: os.path.join(proc, name)  # noqa: E731
    row = {c: "" for c in COLUMNS}
    row["entry"] = entry

    # ---- manifest
    for line in read(os.path.join(ROOT, "entries.tsv")).splitlines()[1:]:
        c = line.split("\t")
        if c[0] == entry:
            row.update(facility=c[3], beamline=c[4], detector=c[5], link=c[6], deposition_version=c[8])

    # ---- steps
    done = {}
    for line in read(P("steps.tsv")).splitlines()[1:]:
        c = line.split("\t")
        if len(c) == 3:
            done[c[0]] = (c[1], c[2])
            row["seconds_" + c[0]] = c[2]
    failed = [s for s in STEPS if s in done and done[s][0] != "0"]
    if failed:
        row["pipeline_status"], row["failed_step"] = "failed", failed[0]
    elif all(s in done for s in STEPS):
        row["pipeline_status"] = "complete"
    else:
        row["pipeline_status"] = "failed"
        row["failed_step"] = next((s for s in STEPS if s not in done), "") if done else "input_selection"
    if done:
        row["total_seconds"] = sum(int(v[1]) for v in done.values())
    row["dials_version"] = last(r"^(DIALS \d\S*)", read(P("tldr.log")))
    row["n_import_args"] = len(read(P("import_args.txt")).split("\n")) - 1 if os.path.exists(P("import_args.txt")) else ""

    # ---- import
    log = read(P("dials.import.log"))
    row["image_format"] = last(r"format: <class '[\w.]*\.(\w+)'>", log)
    try:
        ex = load_expts(P("imported.expt"))
        scans = [s for s in ex.scans() if s is not None]
        row["n_sweeps_imported"] = len(ex.imagesets())
        row["n_images"] = sum(s.get_num_images() for s in scans) if scans else len(ex)
        if scans:
            row["oscillation_deg"] = "%.4f" % scans[0].get_oscillation()[1]
            row["total_rotation_deg"] = "%.2f" % sum(abs(s.get_oscillation_range()[1] - s.get_oscillation_range()[0]) for s in scans)
        row["wavelength"] = "%.5f" % ex[0].beam.get_wavelength()
    except Exception as e:
        print("imported.expt:", e)

    # ---- spot finding / indexing
    row["n_strong_spots"] = last(r"Saved (\d+) reflections to strong\.refl", read(P("dials.find_spots.log")))
    try:
        from dials.array_family import flex
        ex = load_expts(P("indexed.expt"))
        refl = flex.reflection_table.from_file(P("indexed.refl"))
        n_idx = (refl["id"] >= 0).count(True)
        row["n_sweeps_indexed"] = len(ex.imagesets())
        row["n_crystals_indexed"] = len(ex.crystals())
        row["n_indexed_spots"] = n_idx
        row["pct_indexed"] = "%.1f" % (100.0 * n_idx / len(refl)) if len(refl) else ""
    except Exception as e:
        print("indexed:", e)

    # ---- refinement RMSDs (weighted mean over experiments)
    log = read(P("dials.refine.log"))
    idx = log.rfind("RMSDs by experiment")
    if idx >= 0:
        rws = re.findall(r"^\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([-\d.eE]+)\s*\|\s*([-\d.eE]+)\s*\|\s*([-\d.eE]+)\s*\|", log[idx:], flags=re.M)
        tot = sum(int(r[1]) for r in rws)
        if tot:
            row["refine_n_experiments"] = len(rws)
            for k, j in (("refine_rmsd_x_px", 2), ("refine_rmsd_y_px", 3), ("refine_rmsd_z_images", 4)):
                row[k] = "%.4f" % (sum(int(r[1]) * float(r[j]) for r in rws) / tot)

    # ---- integration, symmetry, scaling
    row["n_integrated"] = last(r"Saving (\d+) reflections to integrated\.refl", read(P("dials.integrate.log")))
    log = read(P("dials.symmetry.log"))
    row["symmetry_laue_group"] = last(r"^Best solution: (.+)$", log).strip()
    row["symmetry_laue_probability"] = last(r"^Laue group probability: ([\d.]+)", log)
    log = read(P("dials.scale.log"))
    m = re.findall(r"Parameters: a = ([-\d.eE]+), b = ([-\d.eE]+)", log)
    if m:
        row["error_model_a"], row["error_model_b"] = m[-1]
    for name, key in (("integrated.expt", "n_experiments_integrated"), ("scaled.expt", "n_experiments_scaled")):
        try:
            row[key] = len(load_expts(P(name)))
        except Exception as e:
            print(name, e)

    # ---- final crystal model: the furthest stage that exists
    for name in ("scaled.expt", "symmetrized.expt", "integrated.expt", "refined.expt", "indexed.expt"):
        try:
            xtal = load_expts(P(name)).crystals()[0]
        except Exception:
            continue
        row["model_source"] = name
        row["space_group"] = xtal.get_space_group().type().lookup_symbol()
        for k, v in zip(("cell_a", "cell_b", "cell_c", "cell_alpha", "cell_beta", "cell_gamma"), xtal.get_unit_cell().parameters()):
            row[k] = "%.4f" % v
        break

    # ---- merging statistics
    for name in ("dials.merge.log", "dials.scale.log"):
        text = read(P(name))
        if "Summary of merging statistics" in text:
            row["stats_source"] = name
            merging_stats(text, row)
            row["suggested_d_min_cc_half_fit"] = last(r"Resolution limit suggested from CC\S* fit[^:]*: *([\d.]+)", text)
            break
    # the limit that was applied: dials.scale d_min=auto reports the cut it makes
    auto = last(r"^Applying auto resolution cut at ([\d.]+)", read(P("dials.scale.log")))
    if auto or "d_min = Auto" in read(P("dials.scale.log")):
        row["suggested_d_min_cc_half_fit"] = auto
    row["wilson_b"] = last(r"Wilson B factor\s+([-\d.]+)", read(P("dials.merge.log")))

    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerow(row)
    print("wrote", out)


if __name__ == "__main__":
    main()
