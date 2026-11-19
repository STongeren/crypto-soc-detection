"""Run every detections/*/detection.sql against data/exchange.db and score it.

For each detection it prints true positives, false positives and missed entities,
using tests/ground_truth.json (written by the data generator).

A detection that is still only comments counts as TODO, not as a failure.
Exit code is 1 only when a query crashes, so unfinished work never breaks the build.

Run:  python tests/run_detections.py
"""
import json
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "exchange.db"
TRUTH = json.loads((ROOT / "tests" / "ground_truth.json").read_text(encoding="utf-8"))


def expected(key):
    value = TRUTH[key]
    if isinstance(value, dict):
        return set(value.get("compromised_users", []))
    return set(value)


def has_query(sql):
    lines = [l.strip() for l in sql.splitlines()]
    return any(l and not l.startswith("--") for l in lines)


def main():
    if not DB.exists():
        sys.exit("data/exchange.db not found. Run: python data/generate_exchange_logs.py")
    con = sqlite3.connect(DB)
    rows, crashed = [], False
    for folder in sorted((ROOT / "detections").iterdir()):
        sql_file, meta_file = folder / "detection.sql", folder / "meta.json"
        if not sql_file.exists() or not meta_file.exists():
            continue
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        want = expected(meta["truth_key"])
        sql = sql_file.read_text(encoding="utf-8")
        if not has_query(sql):
            rows.append((folder.name, "TODO", "", "", ""))
            continue
        try:
            cur = con.execute(sql)
            cols = [c[0] for c in cur.description]
            if "entity" not in cols:
                raise ValueError("query must return a column named `entity`")
            got = {r[cols.index("entity")] for r in cur.fetchall()}
        except Exception as exc:  # noqa: BLE001 - report any SQL error
            rows.append((folder.name, f"ERROR: {exc}", "", "", ""))
            crashed = True
            continue
        tp, fp, fn = len(got & want), len(got - want), len(want - got)
        status = "PASS" if fp == 0 and fn == 0 else "WORK"
        rows.append((folder.name, status, str(tp), str(fp), str(fn)))

    header = ("Detection", "Status", "Caught", "False alarms", "Missed")
    widths = [max(len(r[i]) for r in rows + [header]) for i in range(5)]
    line = lambda r: "  ".join(c.ljust(w) for c, w in zip(r, widths))
    print(line(header))
    for r in rows:
        print(line(r))

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("| " + " | ".join(header) + " |\n|" + "---|" * 5 + "\n")
            for r in rows:
                f.write("| " + " | ".join(r) + " |\n")
    sys.exit(1 if crashed else 0)


if __name__ == "__main__":
    main()
