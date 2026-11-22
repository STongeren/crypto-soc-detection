# Python cheat sheet (for logs)

Keep this open next to your editor. Copy an example and change only what you need. All examples use the course data.

## Reading data

| I want to... | Python |
|---|---|
| read a JSON-lines log | `events = [json.loads(line) for line in open("data/events.jsonl", encoding="utf-8")]` (needs `import json`) |
| read a CSV into a lookup table | `users = {r["user_id"]: r for r in csv.DictReader(open("data/users.csv", encoding="utf-8"))}` (needs `import csv`) |
| the first event | `events[0]` |
| a value from an event | `events[0]["user_id"]` |
| a value that might be missing | `e.get("ticket_id")` (gives `None` instead of an error) |
| how many | `len(events)` |

## Filtering and counting

| I want to... | Python | Same idea in SQL / KQL |
|---|---|---|
| keep only some events | `[e for e in events if e["event_type"] == "withdrawal"]` | `WHERE` / `where` |
| two conditions | `if e["event_type"] == "login" and e["result"] == "failure":` | `AND` / `and` |
| count per value | `Counter(e["network"] for e in events)` (needs `from collections import Counter`) | `GROUP BY` / `summarize count() by` |
| the biggest groups | `Counter(...).most_common(3)` | `ORDER BY ... DESC LIMIT 3` / `top 3` |
| a threshold | `{ip for ip, n in fails.items() if n >= 50}` | `HAVING` / `where Total >= 50` |
| count with a variable | `count = 0` then `count += 1` inside the loop | `COUNT(*)` |
| unique values | `set(...)` or `{... for e in events}` | `DISTINCT` / `distinct` |
| group events per customer | `per_user = defaultdict(list)` then `per_user[e["user_id"]].append(e)` (needs `from collections import defaultdict`) | (no direct version) |
| the latest item | `max(items, key=lambda e: e["timestamp"])` | `arg_max(timestamp, *)` |
| is at least one true | `any(... for r in resets)` | `EXISTS` |

## Time

| I want to... | Python |
|---|---|
| turn log text into a time | `datetime.fromisoformat(text.replace("Z", "+00:00"))` (needs `from datetime import datetime`) |
| the gap between two times | `later - earlier` gives a duration |
| a gap in minutes | `(later - earlier).total_seconds() / 60` |
| a fixed duration | `timedelta(minutes=60)` (needs `from datetime import timedelta`) |
| "between 0 and 60 minutes" | `timedelta(0) <= gap <= timedelta(minutes=60)` |

## Functions and output

| I want to... | Python |
|---|---|
| make a function | `def detect(events, users):` and indent the body, end with `return ...` |
| a default value | `def detect_ato(events, window=timedelta(minutes=60)):` |
| text with values in it | `f"Customer {u['name']} lost {pct}%"` |
| text over several lines | `f"""line 1 {x}` ... `"""` |
| make a folder | `Path("tickets").mkdir(exist_ok=True)` (needs `from pathlib import Path`) |
| write a file | `Path("tickets/a.md").write_text(text, encoding="utf-8")` |
| text to a number | `float("4653.0")` |
| round | `round(96.4)` gives `96` |

## Watch out

| Python | Why |
|---|---|
| indentation (4 spaces) | it decides which lines belong to an `if`, `for` or `def` |
| `==` to compare, `=` to store | `if x == 1:` vs `x = 1` |
| everything from a CSV is text | use `float(...)` before calculating |
| `null` in JSON becomes `None` | check with `if e["amount_eur"] is None:` |
| counting starts at 0 | `events[0]` is the first one |
| run from the repo folder | the scripts open `data/...` relative to where your terminal is |

## When it doesn't work

| Error | Probably |
|---|---|
| `NameError: name 'Counter' is not defined` | a missing `import` line |
| `KeyError: 'event-type'` | a typo in a key. Check the real keys with `print(events[0].keys())` |
| `TypeError: can only concatenate str` | adding text and a number. Use `float(...)` |
| `IndentationError` | the spaces at the start of a line don't line up |
| `FileNotFoundError: data/events.jsonl` | the terminal isn't in the repo folder, or the data isn't downloaded |
