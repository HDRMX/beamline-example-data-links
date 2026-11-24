#!/usr/bin/env python3
"""Build the report of a round: rounds/ROUND/report.html, report.md and entries.csv.

    make_report.py ["YYYY-MM-DD HH:MM"]      (ROUND = $HDRMX_ROUND or ROOT/CURRENT_ROUND)

Reads rounds/ROUND/status.tsv, all_results.csv (run bin/aggregate.sh first), tldr.sh and
round.json (title, heading, note, software versions).  The HTML comes from
bin/report_template.html.  Refuses to overwrite the report of a frozen round.
"""
import collections, csv, html, json, os, re, statistics, sys, time

ROOT = os.environ.get("HDRMX_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROUND = os.environ.get("HDRMX_ROUND") or open(os.path.join(ROOT, "CURRENT_ROUND")).read().strip()
RD = os.path.join(ROOT, "rounds", ROUND)
if os.path.exists(os.path.join(RD, "FROZEN")):
    sys.exit("round %s is frozen" % ROUND)
stamp = sys.argv[1] if len(sys.argv) > 1 else time.strftime("%Y-%m-%d %H:%M", time.gmtime())
cfg = json.load(open(os.path.join(RD, "round.json")))
tldr = open(os.path.join(RD, "tldr.sh")).read().rstrip()

REPO = {'proteindiffraction': 'proteindiffraction.org', 'sbgrid': 'SBGrid', 'zenodo': 'Zenodo',
        'pdbj': 'PDBj XRDA', 'dataverse': 'MX-RDR', 'manual': 'Other (manual)'}
COLS = ['entry', 'repository', 'facility', 'beamline', 'detector', 'status', 'failed_step', 'note',
        'space_group', 'sweeps', 'images', 'd_min', 'sugg_d_min', 'cc_half', 'sugg_cc_half',
        'completeness', 'sugg_completeness', 'multiplicity', 'pct_indexed', 'seconds', 'updated_utc']
ent = list(csv.DictReader(open(os.path.join(ROOT, 'entries.tsv')), delimiter='\t'))
st = {r['entry']: r for r in csv.DictReader(open(os.path.join(RD, 'status.tsv')), delimiter='\t')}
res = {r['entry']: r for r in csv.DictReader(open(os.path.join(RD, 'all_results.csv')))}
rows = []
for e in ent:
    s = st[e['entry']]
    r = res.get(e['entry'], {}) if s['status'] in ('Complete', 'Failed') else {}
    g = lambda k: r.get(k, '') or ''
    note = (s.get('note') or '').replace(ROOT + '/', '') if s['status'] not in ('Complete', 'Failed') else ''
    rows.append(dict(zip(COLS, [
        e['entry'], REPO[e['repo']], e['facility'], e['beamline'], e['detector'], s['status'],
        g('failed_step') if s['status'] == 'Failed' else '', note, g('space_group'),
        g('n_sweeps_imported'), g('n_images'), g('overall_d_min'), g('suggested_d_min'),
        g('overall_cc_half'), g('suggested_cc_half'), g('overall_completeness'),
        g('suggested_completeness'), g('overall_multiplicity'), g('pct_indexed'), g('total_seconds'),
        s['updated_utc']])))
assert not any(ROOT in ' '.join(r.values()) for r in rows)
HIDE = set(cfg.get('hide_columns', []))
COLS = [c for c in COLS if c not in HIDE]
rows = [{k: r[k] for k in COLS} for r in rows]
with open(os.path.join(RD, 'entries.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)

# ---------------- HTML
# Optional round.json keys for rounds that do not run the plain DIALS script:
#   replace      [[old, new], ...] wording changes applied to the report prose (HTML and Markdown)
#   system_rows  [[item, value], ...] extra rows at the top of the system table
#   step_names   {step: label} for the failure table of the Markdown report
#   note_title   heading of the note (default "About the statistics")
#   hide_columns [field, ...] table columns left out of the report and entries.csv (e.g. the
#                "suggested" columns of a round whose script already cuts at the suggested limit)
REPL = cfg.get('replace', [])
def sub(x):
    for a, b in REPL:
        x = x.replace(a, b)
    return x
SYSROWS = cfg.get('system_rows', [])
NOTE_TITLE = cfg.get('note_title', 'About the statistics')
t = sub(open(os.path.join(ROOT, 'bin', 'report_template.html')).read())
for c in HIDE:
    t, n1 = re.subn(r'\n *<th data-field="%s"[^\n]*' % c, '', t)
    t, n2 = re.subn(r", \['%s', '[^']*'\]" % c, '', t)
    assert (n1, n2) == (1, 1), c
TR = '          <tr><th scope="row" style="text-align: left; font-weight: 600; padding: 6px 24px 6px 0; white-space: nowrap;">'
assert t.count(TR + 'DIALS</th>') == 1
t = t.replace(TR + 'DIALS</th>', ''.join('%s%s</th><td style="padding: 6px 0;">%s</td></tr>\n' % (TR, html.escape(a), html.escape(b)) for a, b in SYSROWS) + TR + 'DIALS</th>')
assert t.count('<b>About the statistics.</b>') == 1
t = t.replace('<b>About the statistics.</b>', '<b>%s.</b>' % html.escape(NOTE_TITLE))
data = json.dumps([{k: (v if v != '' else None) for k, v in r.items()} for r in rows],
                  separators=(',', ':')).replace('</', '<\\/')
E_ = html.escape
for k, v in (('TITLE', E_(cfg['title'])), ('HEADING', E_(cfg['heading'])), ('NOTE', E_(cfg['note'], quote=False)),
             ('SCRIPT', E_(tldr, quote=False)), ('BUILD_NOTE', E_(cfg['build_note'])), ('DIALS', E_(cfg['dials'])),
             ('DXTBX', E_(cfg['dxtbx'])), ('PYTHON', E_(cfg['python'])), ('DATES', E_(cfg['dates'])),
             ('STAMP', stamp), ('DATA', data)):
    assert t.count('{{%s}}' % k) == 1, k
    t = t.replace('{{%s}}' % k, v)
open(os.path.join(RD, 'report.html'), 'w').write(t)

# ---------------- Markdown
C = collections.Counter(r['status'] for r in rows)
ok = [r for r in rows if r['status'] == 'Complete']
def med(k):
    v = [float(r[k]) for r in ok if r[k]]
    return statistics.median(v) if v else float('nan')
active = len(rows) - C['Complete'] - C['Failed'] - C['Download failed']
o = []; w = o.append
w('# %s\n' % cfg['heading'])
w('%d public depositions listed in [HDRMX/beamline-example-data-links](https://github.com/HDRMX/beamline-example-data-links) were each put once through the same fixed DIALS script. **%d** ran through the whole pipeline, **%d** stopped at a step, and **%d** could not be downloaded.%s\n'
  % (len(rows), C['Complete'], C['Failed'], C['Download failed'], (' %d are still waiting or running.' % active) if active else ''))
w('Every entry goes through import, spot finding, indexing, refinement, integration, symmetry, scaling, export and merging, with no per-dataset options. A failure is recorded as a result and is not repaired.\n')
w('Among completed entries, the median high-resolution limit is **%.2f Å** with no resolution cutoff applied (**%.2f Å** at the limit DIALS suggests), the median overall CC½ is **%.3f**, and the median pipeline run takes **%.1f minutes** on 24 cores.\n'
  % (med('d_min'), med('sugg_d_min') if 'sugg_d_min' in COLS else float('nan'), med('cc_half'), med('seconds') / 60))
w('> **%s.** %s\n' % (NOTE_TITLE, cfg['note'].replace('all_results.csv', '`all_results.csv`').replace('overall_*', '`overall_*`').replace('suggested_*', '`suggested_*`')))
w('An interactive version of this report, with a sortable and filterable table, is in [report.html](report.html). The full set of metrics per entry is in [all_results.csv](all_results.csv).\n')
w('## Contents\n')
for h in ('Results by repository', 'Where the pipeline stopped', 'How to read the failures', 'The pipeline script', 'System and software', 'All datasets'):
    w('- [%s](#%s)' % (h, h.lower().replace(' ', '-')))
w('\n## Results by repository\n')
w('| Repository | Entries | Complete | Failed | Download failed |\n| --- | ---: | ---: | ---: | ---: |')
R = collections.defaultdict(collections.Counter)
for r in rows: R[r['repository']][r['status']] += 1
for k, c in sorted(R.items(), key=lambda x: -sum(x[1].values())):
    w('| %s | %d | %d | %d | %d |' % (k, sum(c.values()), c['Complete'], c['Failed'], c['Download failed']))
w('| **Total** | **%d** | **%d** | **%d** | **%d** |' % (len(rows), C['Complete'], C['Failed'], C['Download failed']))
w('\n## Where the pipeline stopped\n')
w('Failed entries counted by the first step that did not finish. Input selection means the fixed file rule found nothing to hand to `dials.import`.\n')
NAMES = {'input_selection': 'Input selection', 'import': 'dials.import', 'find_spots': 'dials.find_spots', 'index': 'dials.index', 'refine': 'dials.refine', 'integrate': 'dials.integrate', 'symmetry': 'dials.symmetry', 'scale': 'dials.scale', 'export': 'dials.export', 'merge': 'dials.merge'}
NAMES.update(cfg.get('step_names', {}))
F = collections.Counter(r['failed_step'] for r in rows if r['status'] == 'Failed')
w('| Step | Entries |\n| --- | ---: |')
for k in NAMES:
    if F[k]: w('| %s | %d |' % (NAMES[k], F[k]))
for k in F:
    if k not in NAMES: w('| %s | %d |' % (k or 'unknown', F[k]))
w('''
## How to read the failures

- **Some failures come from the benchmark harness and say nothing about DIALS.** Examples are a gap in the image numbering of a sweep (reported by `dials.import` as missing images), depositions that hold fewer than ten images per sweep, and a few downloads that stopped on a missing-directory error or an incomplete rsync transfer.
- **Serial and XFEL depositions** (CXIDB, SACLA, PAL-XFEL, PLS-II) either exceed the 500 GB download cap or hold file types the rotation input rule does not select. They are recorded as they fell, mostly as input selection failures or failed downloads.
- **ESRF data portal entries** need a session login or are archived to tape, so they were not fetched.
- **Low CC½ or low completeness in a completed row is reported as measured.** "Complete" only means the script ran through `dials.merge`. No mask, resolution limit or repair was applied to any entry.

## The pipeline script

This is [tldr.sh](tldr.sh), the one script every entry is run through. Its arguments are the image files, templates or master files chosen by the fixed input rule, and they go to `dials.import` unchanged.

```bash''')
w(tldr)
w('''```

## System and software

Every entry was processed on the same machine with the same build. %s

| Item | Value |
| --- | --- |
%s| DIALS | %s |
| dxtbx | %s |
| Python | %s |
| Linux | Rocky Linux 9.7 (Blue Onyx), kernel 5.14.0-611.49.1.el9_7.x86_64 |
| Hardware | 2 × AMD EPYC 9554 64-core, 224 logical CPUs, 1.5 TB RAM |
| Parallelism | nproc=24 per entry, up to 8 entries side by side |
| Run dates | %s |

## All datasets

Entries are in the order of the source list. Resolution, CC½, completeness and multiplicity are the overall values written by `dials.merge` for all scaled data, with no resolution cutoff. The "suggested" columns are the statistics `dials.merge` reports for the same data cut at the limit DIALS suggests, where a fit of CC½ falls to 0.3. For failed downloads the last column gives the reason.
''' % (cfg['build_note'].replace('dials.version', '`dials.version`'), ''.join('| %s | %s |\n' % (a, b) for a, b in SYSROWS), cfg['dials'], cfg['dxtbx'], cfg['python'], cfg['dates']))
o[:] = [sub(x) for x in o]
TC = [('Entry', 'entry'), ('Status', 'status'), ('Stopped at', 'failed_step'), ('Repository', 'repository'), ('Facility', 'facility'), ('Beamline', 'beamline'), ('Detector', 'detector'), ('Space group', 'space_group'), ('Sweeps', 'sweeps'), ('Images', 'images'), ('Indexed (%)', 'pct_indexed'), ('d min (Å)', 'd_min'), ('d min, suggested (Å)', 'sugg_d_min'), ('CC½', 'cc_half'), ('CC½, suggested', 'sugg_cc_half'), ('Complete (%)', 'completeness'), ('Complete, suggested (%)', 'sugg_completeness'), ('Multiplicity', 'multiplicity'), ('Run time (s)', 'seconds'), ('Download note', 'note')]
TC = [x for x in TC if x[1] not in HIDE]
NUM = {'sweeps', 'images', 'pct_indexed', 'd_min', 'sugg_d_min', 'cc_half', 'sugg_cc_half', 'completeness', 'sugg_completeness', 'multiplicity', 'seconds'}
w('| ' + ' | '.join(c for c, _ in TC) + ' |')
w('| ' + ' | '.join('---:' if k in NUM else '---' for _, k in TC) + ' |')
for r in rows:
    v = dict(r); v['failed_step'] = NAMES.get(r['failed_step'], r['failed_step']).replace('dials.', '')
    if r['status'] != 'Download failed': v['note'] = ''
    w('| ' + ' | '.join((v[k] or '').replace('|', '\\|') for _, k in TC) + ' |')
w('\nSnapshot of %s UTC.' % stamp)
open(os.path.join(RD, 'report.md'), 'w').write('\n'.join(o) + '\n')
print(ROUND, stamp, dict(C), 'failed steps', dict(F))
print('medians: d_min %.2f  suggested d_min %.2f  CC1/2 %.3f  minutes %.1f' % (med('d_min'), med('sugg_d_min') if 'sugg_d_min' in COLS else float('nan'), med('cc_half'), med('seconds') / 60))
