# Week 4: Python for the SOC

7 of 10 crypto SOC job postings ask for scripting, and most name Python. A SOC uses it for the work a SIEM can't do well: combining data, adding context to an alert, writing tickets, calling other tools.

This week you rebuild your detection in Python, add context to the alert (who is the customer, how much did they lose), write a ticket automatically, and build your third detection. The test checks your Python just like your SQL.

Same rules as before: example first, then your question, hints and answers hidden, predict before you look. Every piece of code below was tested on the course data. Python cheat sheet: [cheatsheet-python.md](cheatsheet-python.md).

---

## Before you start (10 minutes, once)

1. **Python:** you installed it in week 1. Check: `python --version` (Mac: `python3 --version`).
2. **An editor:** use [VS Code](https://code.visualstudio.com/download) (free, Windows and Mac). Notepad or TextEdit also works, but VS Code colors your code and shows mistakes.
3. **Your data:** `data/events.jsonl` and `data/users.csv` must be in the `data` folder. Missing? Download [exchange-dataset.zip](https://github.com/STongeren/crypto-soc-detection/releases/latest/download/exchange-dataset.zip) and unzip it into `data`.
4. **Where your scripts go:** a folder `learning/week4/` inside the repo. Each exercise is a small file in there, like `ex1.py`.
   - **VS Code (easiest):** File → Open Folder → pick the repo folder. In the file list on the left, right-click `learning` → New Folder → `week4`. Right-click `week4` → New File → `ex1.py`.
   - **Notepad (Windows):** when saving, set "Save as type" to **All files**, otherwise you get `ex1.py.txt`.
   - **TextEdit (Mac):** first choose **Format → Make Plain Text**, otherwise the file won't run.
5. **How you run a script:** open a terminal in the repo folder (type `cd `, drag the repo folder into the window, press Enter), then:
   - **Windows:** `python learning\week4\ex1.py`
   - **Mac:** `python3 learning/week4/ex1.py`

   Always run from the repo folder. The scripts open `data/...` relative to where you are.

**What `events.jsonl` looks like:** one event per line, written as JSON. JSON is text that looks like this:
```json
{"event_id": "E0000001", "timestamp": "2026-10-01T07:02:31Z", "user_id": "U00590", "event_type": "login", "result": "success", "network": "residential", "amount_eur": null}
```
Each name in quotes (`"user_id"`) is a key, followed by its value. `null` means empty. Python turns this into a **dictionary**: a list of key-value pairs where you look up a value by its key.

---

## Day 1: read, count, filter

### Exercise 1: read the log
**Example** (save as `learning/week4/ex1.py` and run it):
```python
import json

events = []
with open("data/events.jsonl", encoding="utf-8") as f:
    for line in f:
        events.append(json.loads(line))

print(len(events))
```
Line by line:
- `import json` loads Python's built-in JSON tool.
- `events = []` makes an empty list.
- `with open(...) as f:` opens the file. Everything indented under it runs while the file is open.
- `for line in f:` repeats the indented lines once for every line in the file.
- `json.loads(line)` turns one line of JSON text into a dictionary. `events.append(...)` adds it to the list.
- `len(events)` counts the items in the list.

**Indentation matters in Python:** the spaces at the start of a line decide which block it belongs to. Use 4 spaces.

You get 29450.

**New: looking inside.** `events[0]` is the first event (Python counts from 0). `events[0]["user_id"]` is the value of its `user_id` key.

To see every key an event has:
```python
print(events[0].keys())
```
You get `dict_keys(['event_id', 'timestamp', 'user_id', 'event_type', 'result', 'ip', 'country', 'network', 'device_id', 'user_agent', 'auth_method', 'amount_eur', 'asset', 'address', 'actor', 'agent_id', 'ticket_id'])`. Keep this list in mind: you'll use `ip` later this week.

**Your question:** add one line that prints the `event_type` and the `user_id` of the first event.

<details><summary>Hint</summary>

`print(a, b)` prints two things with a space in between.
</details>
<details><summary>Answer</summary>

```python
print(events[0]["event_type"], events[0]["user_id"])
```
`login U00590`.
</details>

### Exercise 2: count per type
**Example** (in `ex1.py`: put the `from collections import Counter` line at the top, under `import json`, and the other two lines at the bottom):
```python
from collections import Counter

counts = Counter(e["event_type"] for e in events)
print(counts.most_common(3))
```
- `Counter` counts how often each value appears. `import` lines always go at the top of a file.
- `e["event_type"] for e in events` means: for every event `e`, take its `event_type`.
- `most_common(3)` gives the 3 most frequent, biggest first.

You get `[('login', 20219), ('support_account_view', 6939), ('withdrawal', 1171)]`. Same numbers as in SQL.

**Your question:** count per `network`, all of them.

<details><summary>Hint</summary>

Change `"event_type"` to `"network"`. `most_common()` without a number gives all of them.
</details>
<details><summary>Answer</summary>

```python
print(Counter(e["network"] for e in events).most_common())
```
`residential` 22235, `corporate` 6939, `hosting` 263, `mobile` 13.
</details>

### Exercise 3: filter
**Example:**
```python
for e in events:
    if e["event_type"] == "password_reset" and e["auth_method"] == "sms":
        print(e["timestamp"], e["user_id"], e["country"])
```
- `if ...:` runs the indented line only when the condition is true. `==` compares, `and` means both.

You get the two SIM-swap resets: `U00005` from `RU` and `U00918` from `VN`.

**New: counting while you loop.** Start a counter at 0 and add 1 every time:
```python
count = 0
for e in events:
    if e["event_type"] == "password_reset":
        count += 1
print(count)
```
`count += 1` means "count becomes count plus 1". This gives 64.

**Predict first:** how many password resets went through `"email"`?
**Your question:** count them.

<details><summary>Answer</summary>

```python
count = 0
for e in events:
    if e["event_type"] == "password_reset" and e["auth_method"] == "email":
        count += 1
print(count)
```
62. The same as in week 1.
</details>

---

## Day 2: time, grouping, your detection

**Warm-up (from memory, in the KQL practice environment):** paste [week2-events.kql](week2-events.kql) first, then count the events per `network` under it.
<details><summary>Answer</summary>

```kql
Events
| summarize Total = count() by network
```
</details>

### Exercise 4: time
Times in the log are text, like `"2026-10-10T02:50:00Z"`. To subtract them, Python must turn them into real times first.

**Example** (`ex4.py`):
```python
from datetime import datetime

def to_time(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00"))

added = to_time("2026-10-10T02:50:00Z")
withdrawn = to_time("2026-10-10T02:54:00Z")
gap = withdrawn - added
print(gap)
print(gap.total_seconds() / 60)
```
- `def to_time(text):` makes your own **function**: a small machine with a name. You give it `text`, and `return` hands back the result.
- `.replace("Z", "+00:00")` writes the `Z` (UTC) in a form every Python version understands.
- Subtracting two times gives a duration: `0:04:00`. `.total_seconds() / 60` turns it into minutes: `4.0`.

These are the new address and the withdrawal of `U00005`.

**Your question:** how many minutes were there between the SMS password reset of `U00918` (`2026-11-01T03:30:00Z`) and the moment they added a new address (`2026-11-01T03:37:00Z`)?

<details><summary>Answer</summary>

```python
print((to_time("2026-11-01T03:37:00Z") - to_time("2026-11-01T03:30:00Z")).total_seconds() / 60)
```
7.0 minutes.
</details>

### Exercise 5: group per customer
To check a pattern per customer, you first put each customer's events together.

**Example** (`ex5.py`, with the reading code from exercise 1 above it):
```python
from collections import defaultdict

per_user = defaultdict(list)
for e in events:
    per_user[e["user_id"]].append(e)

print(len(per_user["U00005"]))
```
- `defaultdict(list)` is a dictionary where every new key automatically starts as an empty list.
- `per_user[e["user_id"]].append(e)` puts each event in the list of its customer.

`U00005` has 19 events.

**Predict first:** how many customers (keys) does `per_user` have? Then check with `print(len(per_user))`.

<details><summary>Answer</summary>

1000: every customer appears at least once.
</details>

**New: sets and `in`.** A **set** is a collection where each value appears only once. You build one like a list, but with `{ }`:
```python
sms_users = {e["user_id"] for e in events if e["auth_method"] == "sms"}
print(len(sms_users))
print("U00005" in sms_users)
```
- `{... for e in events if ...}` collects the matching customers, each only once.
- `x in my_set` is `True` when `x` is in it, otherwise `False`.

You get 2 and `True`. Only two customers have an event where `auth_method` is exactly `"sms"`: the two victims. Normal logins say `"password+sms"`, which is a different value. `==` only matches the exact text.

**Your question:** how many events does `U00918` have?

<details><summary>Answer</summary>

`print(len(per_user["U00918"]))` gives 30.
</details>

### Exercise 6: read your detection in Python
This is the strong ATO-001 rule from week 2, in Python. Read it with the explanation below, then run it (`ex6.py`, with the reading code and `to_time` above it).

```python
from collections import defaultdict
from datetime import timedelta

def detect_ato(events, window=timedelta(minutes=60)):
    per_user = defaultdict(list)
    for e in events:
        per_user[e["user_id"]].append(e)

    flagged = set()
    for user, evs in per_user.items():
        resets = [to_time(e["timestamp"]) for e in evs
                  if e["event_type"] == "password_reset" and e["auth_method"] == "sms"]
        added = [e for e in evs if e["event_type"] == "withdrawal_address_added"]
        withdrawals = [e for e in evs if e["event_type"] == "withdrawal"]

        for ad in added:
            t_add = to_time(ad["timestamp"])
            reset_before = any(timedelta(0) <= t_add - r <= window for r in resets)
            quick_out = any(w["address"] == ad["address"]
                            and timedelta(0) <= to_time(w["timestamp"]) - t_add <= window
                            for w in withdrawals)
            if reset_before and quick_out:
                flagged.add(user)
    return flagged

print(sorted(detect_ato(events)))
```

**New in this code** (read this first):
- `window=timedelta(minutes=60)` is a **default value**: if you don't give a window, it uses 60 minutes. `timedelta` is a duration.
- `set()` is like a list, but every value can only be in it once. Good for "which customers".
- `per_user.items()` gives each customer together with their list of events.
- `[... for e in evs if ...]` builds a new list from the events that match. You saw the same idea in `Counter(...)`.
- `any(...)` is true if **at least one** item matches. `timedelta(0) <= gap <= window` means "the gap is between 0 and the window".
- `sorted(...)` puts the result in order, so it's easy to read.

**Reading questions** (answer them yourself first):
1. What does `reset_before` check?
2. What does `quick_out` check, and why does it compare `address`?

<details><summary>Answers</summary>

1. That there was an SMS password reset at most 60 minutes **before** the new address was added.
2. That money went to that same new address within 60 minutes **after** it was added. Comparing `address` makes sure it's the address that was just added, not an old one.
</details>

**Predict first:** what does it print? Then run it.

<details><summary>Answer</summary>

`['U00005', 'U00918']`. The same 2 victims as your SQL and KQL rules.
</details>

**Your question:** call it with a 5-minute window: `detect_ato(events, timedelta(minutes=5))`. Predict first, then run. Why that result?

<details><summary>Answer</summary>

`[]`, nobody. For both victims the reset came 7 minutes before the new address (`U00005`: 02:43 to 02:50, `U00918`: 03:30 to 03:37, which you measured in exercise 4). With a 5-minute window, `reset_before` is never true. A window that's too tight misses real attacks.
</details>

---

## Day 3: add context and write the ticket

**Warm-up (from memory, in DB Browser):** write the SQL that counts the customers who never made a deposit (week 1, day 6), or, if you skipped day 6, the SQL that shows the countries with more than 2000 events.
<details><summary>Answer</summary>

```sql
SELECT COUNT(*) FROM users u
LEFT JOIN events e ON e.user_id = u.user_id AND e.event_type = 'deposit'
WHERE e.user_id IS NULL;
```
or
```sql
SELECT country, COUNT(*) FROM events GROUP BY country HAVING COUNT(*) > 2000;
```
</details>

### Exercise 7: read the customer table
An alert that only says `U00005` is half the story. An analyst wants to know who it is, how they log in and how much they have. That information is in `users.csv`.

**Example** (`ex7.py`):
```python
import csv

users = {}
with open("data/users.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        users[row["user_id"]] = row

print(users["U00005"]["name"], users["U00005"]["mfa_method"], users["U00005"]["balance_eur"])
```
- `csv.DictReader` reads a CSV file row by row, each row as a dictionary with the column names as keys.
- `users[row["user_id"]] = row` stores each customer under their `user_id`, so you can look them up directly.

You get `Thijs Bakker sms 4653.0`.

**Watch out:** everything from a CSV is **text**, even numbers. `"4653.0" + 1` gives an error. Use `float(...)` to turn it into a number first.

**Your question:** print the name and MFA method of `U00918`.

<details><summary>Answer</summary>

`print(users["U00918"]["name"], users["U00918"]["mfa_method"])` gives `Sara de Wit sms`.
</details>

### Exercise 8: enrich the alert
Adding context to an alert is called **enrichment**. It's a big part of SOC automation.

**Example** (`ex8.py`, with the code from exercises 1, 4, 5, 6 and 7 above it):
```python
for user in sorted(detect_ato(events)):
    u = users[user]
    outs = [e for e in per_user[user] if e["event_type"] == "withdrawal"]
    last = max(outs, key=lambda e: e["timestamp"])
    pct = last["amount_eur"] / float(u["balance_eur"]) * 100
    print(user, u["name"], u["mfa_method"], last["amount_eur"], round(pct))
```
- `max(outs, key=lambda e: e["timestamp"])` picks the withdrawal with the latest time. `lambda e: ...` is a tiny one-line function: "for an event `e`, look at its timestamp".
- `round(pct)` rounds to a whole number.

You get:
```
U00005 Thijs Bakker sms 4466.88 96
U00918 Sara de Wit sms 9105.91 96
```
Both lost 96% of their balance.

**Your question:** also print the country the withdrawal came from.

<details><summary>Answer</summary>

Add `last["country"]` to the `print`: `RU` for `U00005`, `VN` for `U00918`.
</details>
<details><summary>Think question: which of these facts would you put first in a ticket, and why?</summary>

The 96%: it shows the damage and how urgent it is. Then `sms` as MFA method, because it explains how the attacker got in (SIM swap), and the foreign country as supporting evidence.
</details>

### Exercise 9: write the ticket automatically
**Example** (add to `ex8.py`):
```python
from pathlib import Path

Path("tickets").mkdir(exist_ok=True)

for user in sorted(detect_ato(events)):
    u = users[user]
    outs = [e for e in per_user[user] if e["event_type"] == "withdrawal"]
    last = max(outs, key=lambda e: e["timestamp"])
    pct = round(last["amount_eur"] / float(u["balance_eur"]) * 100)

    text = f"""# ATO-001: possible account takeover of {user}

- Customer: {u['name']} (MFA: {u['mfa_method']})
- Withdrawal: {last['amount_eur']} EUR ({pct}% of balance) at {last['timestamp']} from {last['country']}
- Pattern: SMS password reset, new withdrawal address, withdrawal within 60 minutes
"""
    Path(f"tickets/ATO-{user}.md").write_text(text, encoding="utf-8")
    print("written", user)
```
- `Path("tickets").mkdir(exist_ok=True)` makes a folder `tickets` (no error if it already exists).
- `f"""..."""` is an **f-string** over several lines: everything between `{ }` is filled in with the value.
- Inside an f-string with double quotes, use single quotes for keys: `{u['name']}`.
- `.write_text(...)` writes the text to a file.

Run it and open `tickets/ATO-U00005.md` in your editor.

**Your question:** add a line `- Next step: ...` to the ticket with what the analyst should do first.

<details><summary>Answer</summary>

For example:
```
- Next step: freeze withdrawals on the account and contact the customer through a verified channel
```
Add it as one more line inside the f-string, before the closing `"""`. There's no single right text: it has to be the first useful action.
</details>

The `tickets` folder is your output, not part of your repo. It's already in `.gitignore`, so Git ignores it.

---

## Day 4: make it a real detection

**Warm-up (from memory, in the KQL practice environment):** write the KQL threshold that shows the storm types with more than 10000 events.
<details><summary>Answer</summary>

```kql
StormEvents
| summarize Total = count() by EventType
| where Total > 10000
```
</details>

### Exercise 10: plug it into the test
The test looks for a file `detection.py` in the detection folder, with a function called exactly `detect(events, users)` that returns the flagged customers. It reads the data itself and hands it to your function.

1. Open `detections/ATO-001-sim-swap-takeover/detection.py`. It only has comment lines (`#`).
2. Under the comments, paste your imports, your `to_time` function and your detection from exercise 6. Then change three things:
   - Rename `def detect_ato(events, window=timedelta(minutes=60)):` to `def detect(events, users):`. The test always calls it like that.
   - Add `window = timedelta(minutes=60)` as the **first line inside** the function, indented 4 spaces.
   - Keep `return flagged` as the last line, indented 4 spaces. Delete the `print(...)` line.

   You don't need the reading code: the test gives you `events` and `users`.
3. Run the test (Windows: `python tests\run_detections.py`, Mac: `python3 tests/run_detections.py`).

<details><summary>Hint</summary>

Start with:
```python
from collections import defaultdict
from datetime import datetime, timedelta

def to_time(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00"))

def detect(events, users):
    window = timedelta(minutes=60)
```
and then the body of `detect_ato` from exercise 6.
</details>
<details><summary>Answer</summary>

```python
from collections import defaultdict
from datetime import datetime, timedelta


def to_time(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def detect(events, users):
    window = timedelta(minutes=60)
    per_user = defaultdict(list)
    for e in events:
        per_user[e["user_id"]].append(e)
    flagged = set()
    for user, evs in per_user.items():
        resets = [to_time(e["timestamp"]) for e in evs
                  if e["event_type"] == "password_reset" and e["auth_method"] == "sms"]
        added = [e for e in evs if e["event_type"] == "withdrawal_address_added"]
        withdrawals = [e for e in evs if e["event_type"] == "withdrawal"]
        for ad in added:
            t_add = to_time(ad["timestamp"])
            reset_before = any(timedelta(0) <= t_add - r <= window for r in resets)
            quick_out = any(w["address"] == ad["address"]
                            and timedelta(0) <= to_time(w["timestamp"]) - t_add <= window
                            for w in withdrawals)
            if reset_before and quick_out:
                flagged.add(user)
    return flagged
```
The test shows `ATO-001-sim-swap-takeover (python)` as **PASS**: caught 2, false alarms 0, missed 0. Your detection now exists in SQL, KQL and Python. Set Python to **done** in the ATO-001 README.

Got `ERROR`? The message tells you what went wrong:
- `NameError`: a missing `import` or a typo in a name.
- `KeyError`: a key that doesn't exist, often a typo like `"event-type"`.
- `TypeError: 'NoneType' object is not iterable`: your function has no `return flagged` at the end, so it returns nothing.
- `IndentationError`: the spaces at the start of the lines don't line up.
</details>

---

## Day 5: on your own

No examples, no hints. Use the [Python cheat sheet](cheatsheet-python.md) and your scripts from this week.

### Exercise 11: your third detection (CS-001)
<details><summary>One hint, only if you're stuck for 10 minutes</summary>

Step 1: count the failed logins per `e["ip"]` with `Counter`. Step 2: keep the IPs with 50 or more (`for ip, n in fails.items()` gives each IP with its count). Step 3: collect the customers with a successful login from one of those IPs.
</details>

Credential stuffing: one server tries leaked passwords on hundreds of accounts. Almost all fail, a few succeed.

Everything you need is in this week: `Counter` (exercise 2), `e["ip"]` and `e["result"]` (exercise 1), a threshold like `n >= 50` (`>=` means "greater than or equal"), sets and `in` (exercise 5).

**Your question:** in `detections/CS-001-credential-stuffing/detection.py`, write `detect(events, users)` that returns the customers who **successfully** logged in from an IP that had **50 or more failed logins**. Run the test.

<details><summary>Answer</summary>

```python
from collections import Counter


def detect(events, users):
    fails = Counter(e["ip"] for e in events
                    if e["event_type"] == "login" and e["result"] == "failure")
    bad_ips = {ip for ip, n in fails.items() if n >= 50}
    return {e["user_id"] for e in events
            if e["event_type"] == "login" and e["result"] == "success" and e["ip"] in bad_ips}
```
One IP had 257 failed logins. Three customers logged in successfully from it: `U00226`, `U00242` and `U00780`. The test shows CS-001 (python) as **PASS**: caught 3, false alarms 0, missed 0.

Got many false alarms? You probably counted all logins instead of only failures, or forgot `result == "success"` for the second part.
</details>
<details><summary>Think question: why 50? How would you choose a threshold in a real SOC?</summary>

Look at normal behaviour first: `print(fails.most_common(5))` shows that after the attacker's 257, the next IPs have only 5 failures. A threshold sits well above normal and well below the attack. In a real SOC you check this over weeks of data and write the choice down in the detection's README.
</details>

### Exercise 12: week 4 quiz
Predict first, then check each line in **interactive Python**: in a terminal type `python` (Mac: `python3`) and press Enter. You see `>>>`. Paste one line, press Enter, and Python answers right away. Leave with `exit()`.

The `;` in line 1 puts two statements on one line.

1. `from collections import Counter; print(Counter(["a", "b", "a"]).most_common(1))`
2. `print(float("4653.0") + 1)`
3. `print(len({"U1", "U2", "U1"}))`
4. What happens with `print("4653.0" + 1)`?

<details><summary>Answers</summary>

1. `[('a', 2)]`.
2. `4654.0`. `float` turned the text into a number.
3. `2`. A set keeps each value once.
4. A `TypeError`: you can't add text and a number. This is the classic CSV mistake from exercise 7.
</details>

You can now say honestly: "I can read logs with Python, group and filter events, write a detection as a function, add context from another source and write tickets automatically. I built three tested detections."

---

## Day 6 (extra): enrichment from the internet

Optional. Real SOC automation (SOAR) often asks another service for context: who owns this IP, is this file known malware, what is this wallet worth. Here you ask a free crypto price service what the stolen amounts are worth in bitcoin today.

**New: calling a web service.** `urllib.request` downloads a web page. Many services answer in JSON, so you read the answer with `json.loads`:
```python
import json
import urllib.request

url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur"
req = urllib.request.Request(url, headers={"User-Agent": "crypto-soc-detection-course"})
with urllib.request.urlopen(req, timeout=15) as r:
    data = json.loads(r.read())

print(data)
price = data["bitcoin"]["eur"]
print(round(9105.91 / price, 4), "BTC")
```
- The `User-Agent` header tells the service who's asking. Many services refuse requests without one.
- `timeout=15` stops waiting after 15 seconds.

**Mac:** if you get `CERTIFICATE_VERIFY_FAILED`, open **Applications → Python 3.x** and double-click **Install Certificates.command** once. Then run it again.

You get something like `{'bitcoin': {'eur': 55290}}`. The price changes all the time, so your numbers will differ.

**Your question:** add this to your ticket script from exercise 9, so every ticket also shows the stolen amount in BTC at today's price.

<details><summary>Answer</summary>

Get `price` once at the top of the script (not inside the loop: one request instead of one per ticket), then add this line inside the f-string:
```
- Value today: {round(last['amount_eur'] / price, 4)} BTC
```
</details>
<details><summary>Think question: what could go wrong with calling a service inside a detection?</summary>

The service can be slow, down, or limit how often you ask. A detection should still work without it: catch the error and write the ticket without the extra line. And never send customer data to an outside service you don't control.
</details>
