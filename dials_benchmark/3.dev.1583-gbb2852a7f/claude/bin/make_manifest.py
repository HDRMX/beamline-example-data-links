#!/usr/bin/env python3
"""Build entries.tsv from the HDRMX beamline-example-data-links README table.

Columns: entry, data_entry, repo, facility, beamline, detector, link, description, version
  entry       PDB ID from the description column (upper case); for rows without
              one, a name derived from the link.
  data_entry  the entry whose data/ folder holds the raw images.  Differs from
              `entry` only when several entries share one download link.
  repo        download method used by bin/download_entry.py
"""
import os, re, sys

ROOT = os.environ.get("HDRMX_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "beamline-example-data-links", "README.md")


def repo_of(link):
    l = link.lower()
    if "10.18430/" in l: return "proteindiffraction"
    if "sbgrid" in l: return "sbgrid"
    if "zenodo" in l: return "zenodo"
    if "data.pdbj.org::" in l or "10.51093/xrd-" in l: return "pdbj"
    if "10.18150/" in l: return "dataverse"
    return "manual"


rows, seen, owner = [], set(), {}
for line in open(src):
    if not line.startswith("|"): continue
    c = [x.strip() for x in line.strip().strip("|").split("|")]
    if len(c) < 6 or c[0] == "Facility" or set(c[0]) <= set("- "): continue
    fac, bl, det, link, desc, ver = c[:6]
    if re.fullmatch(r"[0-9][A-Za-z0-9]{3}", desc):
        entry = desc.upper()
    else:
        entry = "zenodo_" + link.rstrip("/").split("/")[-1] if "zenodo" in link else re.sub(r"[^A-Za-z0-9]+", "_", link.split("/")[-1]).strip("_")
    if entry in seen:
        sys.exit("duplicate entry id: " + entry)
    seen.add(entry)
    owner.setdefault(link, entry)
    rows.append([entry, owner[link], repo_of(link), fac, bl, det, link, desc, ver])

with open(os.path.join(ROOT, "entries.tsv"), "w") as f:
    f.write("entry\tdata_entry\trepo\tfacility\tbeamline\tdetector\tlink\tdescription\tversion\n")
    for r in rows:
        f.write("\t".join(r) + "\n")
print(len(rows), "entries written")
