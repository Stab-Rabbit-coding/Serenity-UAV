---
title: "Unquoted commas in bom_revS.csv Notes truncate the BOM on rewrite and hide JSON/CSV drift"
date: 2026-09-16
category: logic-errors
module: "current-specification/ BOM (bom_revS.json / bom_revS.csv); tools/compact_bom_entries.py"
problem_type: logic_error
component: tooling
severity: high
symptoms:
  - "csv.DictWriter raises ValueError 'dict contains fields not in fieldnames: None' part-way through writing bom_revS.csv"
  - "bom_revS.csv left truncated at 9 rows after the failed in-place write"
  - "csv.DictReader yields an extra None-keyed overflow field for 18 committed rows whose Notes column contained unquoted commas"
  - "bom_revS.json, declared canonical in current-specification/README.md, silently lacked 14 rows the CSV had (CF-ROD-8MM, PRINT-NACELLE-TRUNNION, BRG-6704ZZ ...)"
  - "bom_revS.json carried the CSV overflow as a literal 'null' key instead of folding it into Notes"
root_cause: missing_validation
resolution_type: code_fix
related_components:
  - current-specification/bom_revS.csv
  - current-specification/bom_revS.json
  - current-specification/README.md
  - tools/compact_bom_entries.py
  - docs/solutions/workflow-issues/generate-open-item-views-never-hand-patch-them.md
tags: [bom, csv, json, data-integrity, dictwriter, atomic-write, canonical-source, quoting]
---

# Unquoted commas in bom_revS.csv Notes truncate the BOM on rewrite and hide JSON/CSV drift

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP. **AI note:** drafted by
Claude (model: Claude Opus 5, Anthropic) under the author's direction,
2026-09-16, per `AGENTS.md` §3. **License:** CC BY-SA 4.0.

## Problem

`current-specification/README.md` names `bom_revS.json` the canonical BOM and
`bom_revS.csv` a derived flat file. In practice every BOM edit goes to the CSV
and is mirrored to the JSON by hand. On 2026-09-16 (cargo Rev T5e) a
tools-assisted edit read the CSV with `csv.DictReader`, changed a dozen rows,
and wrote it back with `csv.DictWriter` — which raised part-way and left the
committed BOM truncated to nine rows. Recovering it exposed that the two files
had already diverged: the "canonical" JSON was missing 14 rows the CSV had.

## Symptoms

* `ValueError: dict contains fields not in fieldnames: None` from
  `csv.DictWriter.writerows` — after the header and a handful of rows were
  already written.
* `git diff --stat` on the CSV: `1 insertion(+), 174 deletions(-)`.
* `csv.DictReader` rows with a `None` key holding a list of strings for 18 of
  the HEAD rows (`CF-ROD-8MM`, `CF-BAR-6X3`, `CF-PLATE-2MM`,
  `PRINT-HEAD-SHELL`, `PRINT-CARGO-SECT`, `SPAR-TILT-4130` …): their Notes had
  been typed with bare commas and never quoted.
* The JSON mirror had the same rows with a literal `"null"` key (a `None` key
  round-tripped through `json.dump`), and lacked 14 Refs present in the CSV.

## What Didn't Work

* Re-running the same DictWriter rewrite after "fixing" one row — the
  exception is raised by the *first* overflow row, and there were 18.
* Treating the JSON as the recovery source — it was the file that had drifted.
  Only `git show HEAD:current-specification/bom_revS.csv` (182 rows) plus the
  13 Rev T5 rows that existed only in the JSON reconstructed the full set.

## Solution

Rebuild both files from the union, folding overflow back into Notes and
letting the writer quote:

```python
fields = [k for k in hrows[0].keys() if k is not None]
def fix(r):
    r = dict(r)
    for key in (None, "null"):                 # DictReader overflow / JSON round-trip
        extra = r.pop(key, None)
        if extra:
            r["Notes"] += "," + (",".join(extra) if isinstance(extra, list) else str(extra))
    return {k: r.get(k, "") for k in fields}
```

`csv.DictWriter(..., fieldnames=fields)` with the default `QUOTE_MINIMAL` then
quotes every field that contains a comma, so the next reader sees one Notes
field again. Both files are now 197 rows with identical Ref sets; the JSON
`description` records the rebuild.

## Why This Works

`DictReader` never loses data — it parks extra fields under `None` — but
`DictWriter` refuses a key that is not in `fieldnames` and raises after it has
already written the rows before it. Writing in place therefore destroys the
file on the first malformed row. Folding the overflow back restores the
original text; quoting on write makes it stable.

## Prevention

1. **Assert parity before touching either file.** Load both, compare row
   counts and Ref sets, and refuse to proceed on a mismatch — that check would
   have caught the 14 missing rows a session earlier.
2. **Never rewrite the BOM in place.** Write to a temp file in the same
   directory, re-read it, check the row count and that no row has a `None`
   key, then `os.replace()`. A failed write then costs nothing.

   ```python
   tmp = path + ".tmp"
   with open(tmp, "w", newline="") as fh:
       w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)
   chk = list(csv.DictReader(open(tmp, newline="")))
   assert len(chk) == len(rows) and not any(r.get(None) for r in chk)
   os.replace(tmp, path)
   ```

3. **Fold and quote overflow before writing** (the `fix()` above), and reject
   a `"null"` key in the JSON the same way.
4. **The "JSON is canonical" claim is unverified** until a script regenerates
   one file from the other (`tools/compact_bom_entries.py` only reformats the
   JSON; nothing syncs them). Either add a sync script (proposed name `tools/bom_sync.py` — does not exist yet, WBS §0.10 BOM-SYNC) with the parity
   assertion, or amend the README to say the CSV is the edited file. Same
   rule as `generate-open-item-views-never-hand-patch-them.md`: a mirror that
   is maintained by hand is not a mirror.
