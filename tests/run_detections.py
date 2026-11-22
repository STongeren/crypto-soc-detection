"""Score every detection against the labelled dataset.

For each detection folder it runs:
  detection.sql  against data/exchange.db  (must return a column named `entity`)
  detection.py   if it exists              (must define detect(events, users) that returns the flagged entities)

and prints what it caught, its false alarms and what it missed, using tests/ground_truth.json
(written by the data generator).

A detection that is still empty counts as TODO, not as a failure.
Exit code is 1 only when a detection crashes, so unfinished work never breaks the build.

Run:  python tests/run_detections.py      (Mac/Linux: python3)
"""
import csv
import importlib.util
import json
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DB = DATA / "exchange.db"
TRUTH = json.loads((ROOT / "tests" / "ground_truth.json").read_text(encoding="utf-8"))


def expected(key):
    value = TRUTH[key]
    if isinstance(value, dict):
        return set(value.get("compromised_users", []))
    return set(value)


def has_code(text, comment):
    return any(l.strip() and not l.strip().startswith(comment) for l in text.splitlines())


def score(name, got, want):
    tp, fp, fn = len(got & want), len(got - want), len(want - got)
    status = "PASS" if fp == 0 and fn == 0 else "WORK"
    return (name, status, str(tp), str(fp), str(fn))


def run_sql(folder, want, con):
    sql = (folder / "detection.sql").read_text(encoding="utf-8")
    if not has_code(sql, "--"):
        return (folder.name, "TODO", "", "", ""), False
    try:
        cur = con.execute(sql)
        cols = [c[0] for c in cur.description]
        if "entity" not in cols:
            raise ValueError("query must return a column named `entity`")
        got = {r[cols.index("entity")] for r in cur.fetchall()}
    except Exception as exc:  # noqa: BLE001 - report any SQL error
        return (folder.name, f"ERROR: {exc}", "", "", ""), True
    return score(folder.name, got, want), False


_cache = {}


def load_data():
    if not _cache:
        with open(DATA / "events.jsonl", encoding="utf-8") as f:
            _cache["events"] = [json.loads(line) for line in f]
        with open(DATA / "users.csv", encoding="utf-8") as f:
            _cache["users"] = {r["user_id"]: r for r in csv.DictReader(f)}
    return _cache["events"], _cache["users"]


def run_py(folder, want):
    name = folder.name + " (python)"
    path = folder / "detection.py"
    if not has_code(path.read_text(encoding="utf-8"), "#"):
        return (name, "TODO", "", "", ""), False
    try:
        spec = importlib.util.spec_from_file_location(f"det_{folder.name.replace('-', '_')}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not hasattr(module, "detect"):
            raise ValueError("detection.py must define detect(events, users)")
        events, users = load_data()
        got = set(module.detect(events, users))
    except Exception as exc:  # noqa: BLE001 - report any error in the learner's code
        return (name, f"ERROR: {type(exc).__name__}: {exc}", "", "", ""), True
    return score(name, got, want), False


def main():
    if not DB.exists():
        sys.exit("data/exchange.db not found. See SETUP.md, or run: python data/generate_exchange_logs.py")
    con = sqlite3.connect(DB)
    rows, crashed = [], False
    for folder in sorted((ROOT / "detections").iterdir()):
        meta_file = folder / "meta.json"
        if not meta_file.exists():
            continue
        want = expected(json.loads(meta_file.read_text(encoding="utf-8"))["truth_key"])
        if (folder / "detection.sql").exists():
            row, bad = run_sql(folder, want, con)
            rows.append(row)
            crashed |= bad
        if (folder / "detection.py").exists():
            if not (DATA / "events.jsonl").exists():
                rows.append((folder.name + " (python)", "ERROR: data/events.jsonl not found", "", "", ""))
                crashed = True
                continue
            row, bad = run_py(folder, want)
            rows.append(row)
            crashed |= bad

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
