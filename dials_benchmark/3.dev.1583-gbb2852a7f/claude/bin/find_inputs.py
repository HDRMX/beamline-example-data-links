#!/usr/bin/env python3
"""Fixed rule that turns an entry's data/ folder into dials.import arguments.

Usage: find_inputs.py DATA_DIR [ENTRY]      (one argument per output line)

Rule (no judgment involved):
  0. If DATA_DIR contains sub-folders whose name contains ENTRY (case-insensitive),
     only those sub-folders are searched (used when entries share a deposition).
  1. HDF5: every *.nxs file is imported.  A *_master.h5 is imported only when
     no .nxs with the same prefix sits next to it.  Other .h5 files are ignored.
  2. Everything else: files with a diffraction-image extension are grouped into
     templates by replacing the frame number with '#'; each template with at
     least MIN_IMAGES files is imported as template=...  XDS/processing output
     images (GAIN.cbf, BKGINIT.cbf, ...) are ignored.
  3. Output is sorted, so the result is reproducible.
"""
import os, re, sys

MIN_IMAGES = 10
IMG_EXT = {".cbf", ".img", ".mccd", ".osc", ".sfrm", ".pck", ".mar1200", ".mar1600", ".mar1800",
           ".mar2000", ".mar2300", ".mar2400", ".mar2560", ".mar3000", ".mar3200", ".mar3450",
           ".marccd", ".tif", ".tiff", ".image", ".ipf", ".rodhypix", ".raxis", ".smv", ".dat"}
COMP = (".gz", ".bz2")
XDS_JUNK = {"ABS", "ABSORP", "BKGINIT", "BKGPIX", "BLANK", "DECAY", "DX-CORRECTIONS", "DY-CORRECTIONS",
            "FRAME", "GAIN", "GX-CORRECTIONS", "GY-CORRECTIONS", "MODPIX", "X-CORRECTIONS", "Y-CORRECTIONS"}


def split_ext(name):
    """-> (stem, ext, compression) ; ext lower-cased, includes the dot."""
    comp = ""
    for c in COMP:
        if name.lower().endswith(c):
            comp, name = name[-len(c):], name[:-len(c)]
    stem, ext = os.path.splitext(name)
    return stem, ext, comp


def template_of(path):
    d, name = os.path.split(path)
    stem, ext, comp = split_ext(name)
    if re.fullmatch(r"\.\d{3,5}", ext):                       # name.0001 style
        return os.path.join(d, stem + "." + "#" * (len(ext) - 1) + comp)
    if ext.lower() not in IMG_EXT or stem.upper() in XDS_JUNK:
        return None
    m = re.fullmatch(r"(.*?)(\d+)", stem)
    if not m:
        return None
    return os.path.join(d, m.group(1) + "#" * len(m.group(2)) + ext + comp)


def main():
    data = os.path.realpath(sys.argv[1])
    entry = sys.argv[2].lower() if len(sys.argv) > 2 else None
    roots = [data]
    if entry:
        sub = sorted(os.path.join(dp, d) for dp, dn, _ in os.walk(data, followlinks=True)
                     for d in dn if entry in d.lower())
        sub = [s for s in sub if not any(s.startswith(o + os.sep) for o in sub)]
        if sub:
            roots = sub
    h5, templates = [], {}
    for root in roots:
        for dp, dn, fn in os.walk(root, followlinks=True):
            dn.sort()
            names = set(fn)
            for f in sorted(fn):
                p = os.path.join(dp, f)
                low = f.lower()
                if low.endswith(".nxs"):
                    h5.append(p)
                elif low.endswith("master.h5"):
                    prefix = re.sub(r"_?master\.h5$", "", f, flags=re.I)
                    if prefix + ".nxs" not in names:
                        h5.append(p)
                elif low.endswith((".h5", ".hdf5")):
                    continue
                else:
                    t = template_of(p)
                    if t:
                        templates[t] = templates.get(t, 0) + 1
    for p in sorted(h5):
        print(p)
    for t in sorted(templates):
        if templates[t] >= MIN_IMAGES:
            print("template=" + t)


main()
