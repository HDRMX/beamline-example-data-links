#!/usr/bin/env python3
"""Download the raw data of one entry into entries/<data_entry>/data and unpack it.

  download_entry.py ENTRY            claim, download, unpack, verify, set status
  download_entry.py --finish ENTRY   unpack + verify + set status only (after a manual download)

Exit codes: 0 Downloaded, 1 download failed, 3 repository needs a manual download
(status stays "Downloading"; see DOWNLOAD_RULES.md).
Output goes to entries/<data_entry>/download.log as well as stdout.
"""
import hashlib, json, os, re, subprocess, sys, urllib.request

ROOT = os.environ.get("HDRMX_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS = os.path.join(ROOT, "bin", "status")
UA = {"User-Agent": "dials-benchmark-downloader"}
LOG = None


def say(*a):
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True)
    if LOG:
        LOG.write(msg + "\n"); LOG.flush()


def run(cmd):
    say("$", " ".join(cmd))
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if p.stdout.strip():
        say(p.stdout.strip()[-2000:])
    if p.returncode:
        raise RuntimeError("command failed (%d): %s" % (p.returncode, cmd[0]))


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        return r.read()


def curl(url, dest):
    run(["curl", "-sS", "-f", "-L", "-C", "-", "--retry", "8", "--retry-delay", "30",
         "--retry-all-errors", "-A", UA["User-Agent"], "-o", dest, url])


def rsync(src, dest):
    run(["rsync", "-a", "--partial", "--timeout=600", src.rstrip("/") + "/", dest + "/"])


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def get_zenodo(link, dest):
    rec = re.search(r"(\d+)/?$", link).group(1)
    meta = json.loads(fetch("https://zenodo.org/api/records/" + rec))
    for f in meta["files"]:
        out = os.path.join(dest, f["key"])
        os.makedirs(os.path.dirname(out), exist_ok=True)
        want = f.get("checksum", "").replace("md5:", "")
        if os.path.exists(out) and os.path.getsize(out) == f["size"] and (not want or md5(out) == want):
            continue
        curl(f["links"]["self"], out)
        if want and md5(out) != want:
            raise RuntimeError("md5 mismatch for " + f["key"])


def get_proteindiffraction(link, dest):
    page = fetch(link).decode("utf-8", "replace")
    urls = sorted(set(re.findall(r'href="(https?://data\.proteindiffraction\.org/[^"]+)"', page)))
    if not urls:
        raise RuntimeError("no data links found on " + link)
    for u in urls:
        curl(u, os.path.join(dest, u.rstrip("/").split("/")[-1]))


def get_dataverse(link, dest):
    doi = re.search(r"(10\.\d+/.+)$", link).group(1)
    base = "https://mxrdr.icm.edu.pl"
    meta = json.loads(fetch("%s/api/datasets/:persistentId/?persistentId=doi:%s" % (base, doi)))
    for f in meta["data"]["latestVersion"]["files"]:
        df = f["dataFile"]
        out = os.path.join(dest, f.get("directoryLabel", ""), df["filename"])
        os.makedirs(os.path.dirname(out), exist_ok=True)
        if os.path.exists(out) and os.path.getsize(out) == df.get("filesize", -1):
            continue
        curl("%s/api/access/datafile/%s?format=original" % (base, df["id"]), out)


def download(repo, link, dest):
    if repo == "sbgrid":
        rsync("rsync://data.sbgrid.org/10.15785/SBGRID/" + re.search(r"(\d+)/?$", link).group(1), dest)
    elif repo == "pdbj":
        m = re.search(r"xrd-0*(\d+)$", link)
        rsync("data.pdbj.org::rsync/xrda/" + (m.group(1) if m else link.rstrip("/").split("/")[-1]), dest)
    elif repo == "zenodo":
        get_zenodo(link, dest)
    elif repo == "proteindiffraction":
        get_proteindiffraction(link, dest)
    elif repo == "dataverse":
        get_dataverse(link, dest)
    else:
        return False
    return True


ARCHIVE = re.compile(r"\.(tar|tar\.gz|tgz|tar\.bz2|tbz2?|tar\.xz|txz|tar\.zst|zip)$", re.I)


def unpack(dest):
    """Extract every archive next to itself, then delete it; repeat for nested archives."""
    for _ in range(5):
        found = [os.path.join(dp, f) for dp, _, fn in os.walk(dest) for f in fn if ARCHIVE.search(f)]
        if not found:
            return
        for a in sorted(found):
            d = os.path.dirname(a)
            if a.lower().endswith(".zip"):
                run(["unzip", "-q", "-n", a, "-d", d])
            else:
                run(["tar", "-xf", a, "-C", d])
            os.remove(a)


def verify(dest):
    n = size = 0
    for dp, _, fn in os.walk(dest):
        for f in fn:
            n += 1
            size += os.path.getsize(os.path.join(dp, f))
    if n == 0 or size == 0:
        raise RuntimeError("data folder is empty")
    return "%d files, %.2f GB" % (n, size / 1e9)


def main():
    global LOG
    args = [a for a in sys.argv[1:] if a != "--finish"]
    finish = "--finish" in sys.argv
    if len(args) != 1:
        sys.exit(__doc__)
    rows = [l.split("\t") for l in open(os.path.join(ROOT, "entries.tsv")).read().splitlines()[1:]]
    me = [r for r in rows if r[0] == args[0]]
    if not me:
        sys.exit("unknown entry " + args[0])
    owner, repo, link = me[0][1], me[0][2], me[0][6]
    group = [r[0] for r in rows if r[1] == owner]
    edir = os.path.join(ROOT, "entries", owner)
    dest = os.path.join(edir, "data")
    os.makedirs(dest, exist_ok=True)
    LOG = open(os.path.join(edir, "download.log"), "a")

    if not finish:
        cur = subprocess.run([STATUS, "get", owner], capture_output=True, text=True).stdout.strip()
        if cur not in ("Not started", "Download failed"):
            say("refusing: %s is %r" % (owner, cur)); sys.exit(1)
        for e in group:
            subprocess.run([STATUS, "set", e, "Downloading", repo])
    try:
        say("entry %s  repo %s  link %s" % (owner, repo, link))
        if not finish and not download(repo, link, dest):
            say("MANUAL: no automatic method for this repository; download into", dest,
                "and then run: bin/download_entry.py --finish", owner)
            sys.exit(3)
        unpack(dest)
        note = verify(dest)
    except Exception as e:  # noqa
        say("DOWNLOAD FAILED:", e)
        for g in group:
            subprocess.run([STATUS, "set", g, "Download failed", str(e)])
        sys.exit(1)
    for g in group:
        gdir = os.path.join(ROOT, "entries", g)
        os.makedirs(gdir, exist_ok=True)
        if g != owner and not os.path.lexists(os.path.join(gdir, "data")):
            os.symlink(os.path.join("..", owner, "data"), os.path.join(gdir, "data"))
        subprocess.run([STATUS, "set", g, "Downloaded", note])
    say("DOWNLOADED:", note)


main()
