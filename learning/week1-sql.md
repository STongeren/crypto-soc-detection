# Week 1: SQL

**How every exercise works:**
1. **Example:** paste it into DB Browser (tab **Execute SQL**) and run it: **Ctrl + Enter** on Windows, **Cmd + Return** on Mac, or click the ▶ button. Read what each part does. Delete the old query first: with several queries in the box, you only see the result of the last one.
2. **Your question:** write the query yourself. Use [the cheat sheet](cheatsheet.md), that's not cheating.
3. Stuck? Click **Hint**. Only when you have your own answer, click **Answer** to check.
4. **Think question:** this is what a SOC analyst asks themselves. Think first, then click.

Some questions ask you to **predict first**. Just guess. A guess that turns out wrong sticks better than an answer you only read.

3 or 4 exercises a day, about 20 to 30 minutes. Day 5 you work on your own.

---

## Day 1: looking

### Exercise 1: the first rows
A database table is like a spreadsheet: **rows** (one per event) and **columns** (like `user_id` or `country`). Our main table is called `events`.

**Example:**
```sql
SELECT * FROM events LIMIT 10;
```
Read it as a sentence:
- `SELECT *` = show all columns (`*` means "all" here)
- `FROM events` = from the table `events`
- `LIMIT 10` = only the first 10 rows
- `;` = the end of the query

Don't want all columns? Write their names instead of `*`, with a comma in between:
```sql
SELECT user_id, country FROM events LIMIT 10;
```

**Your question:** show only the columns `timestamp`, `user_id` and `event_type`, and only 5 rows.

<details><summary>Hint</summary>

Replace `*` with the column names, separated by commas.
</details>
<details><summary>Answer</summary>

```sql
SELECT timestamp, user_id, event_type FROM events LIMIT 5;
```
</details>

### Exercise 2: the second victim
**Example:**
```sql
SELECT * FROM events WHERE user_id = 'U00005';
```
`WHERE` is a filter: you only see the rows of this customer. Text values like `'U00005'` go between single quotes `' '`. Numbers don't.

Look at the `country` column. His home country is Belgium (`BE`), and he also uses the exchange from the Netherlands (`NL`). The rows from Russia (`RU`) are the attack.

**Your question:** customer `U00918` was hacked too. Show only the `country` column for this customer. Which unusual country did the attack come from?

<details><summary>Hint</summary>

Combine exercise 1 and the example: pick the `country` column after `SELECT`, and change the `user_id`.
</details>
<details><summary>Answer</summary>

```sql
SELECT country FROM events WHERE user_id = 'U00918';
```
You mostly see `NL`: that's where she lives. In between, `VN` (Vietnam) shows up a few times. That's where the attack came from.
</details>

### Exercise 3: which networks exist
**Example:**
```sql
SELECT DISTINCT event_type FROM events;
```
`DISTINCT` shows each value only once. That's how you see what a column can contain.

**Predict first:** how many types of network do you think there are?
**Your question:** which types of `network` are in the data?

<details><summary>Answer</summary>

```sql
SELECT DISTINCT network FROM events;
```
4: `residential` (home), `corporate` (the exchange's office), `mobile` (phone) and `hosting` (a server in a data center).
</details>
<details><summary>Think question: which of the four would you, as a customer, never use to log in?</summary>

`hosting`. A normal person doesn't log in from a server in a data center. A script that tries thousands of passwords does.
</details>

---

## Day 2: filtering and counting

### Exercise 4: 2FA changed
**Example:**
```sql
SELECT * FROM events WHERE event_type = 'password_reset';
```

**Your question:** how often was two-factor authentication (2FA) changed? Look up in the cheat sheet what that event is called.

<details><summary>Hint</summary>

Look in part 2 of the cheat sheet, under `event_type`.
</details>
<details><summary>Answer</summary>

```sql
SELECT * FROM events WHERE event_type = 'mfa_changed';
```
2 times, for `U00005` and `U00918`: the two victims.
</details>

### Exercise 5: email or SMS
**Example:**
```sql
SELECT * FROM events
WHERE event_type = 'password_reset' AND auth_method = 'sms';
```
`AND` means: both must be true.

**New: counting.** Don't want to see all the rows, just how many there are? Put `COUNT(*)` in place of `*`:
```sql
SELECT COUNT(*) FROM events
WHERE event_type = 'password_reset' AND auth_method = 'sms';
```
You get one number: 2.

**Predict first:** do more resets go through email or through SMS?
**Your question:** count how many resets went through email.

<details><summary>Hint</summary>

Take the query with `COUNT(*)` and only change `'sms'` to `'email'`.
</details>
<details><summary>Answer</summary>

```sql
SELECT COUNT(*) FROM events
WHERE event_type = 'password_reset' AND auth_method = 'email';
```
62. Through SMS there were only 2.
</details>
<details><summary>Think question: what does that difference tell you?</summary>

Normal customers reset through email. Both SMS resets were the attackers. So an SMS reset is a strong signal, especially combined with an unusual country.
</details>

### Exercise 6: countries
**Example:**
```sql
SELECT event_type, COUNT(*) FROM events GROUP BY event_type;
```
`GROUP BY` makes groups. `COUNT(*)` counts how many rows are in each group.

Countries are two-letter codes. The ones you'll meet: `NL` Netherlands, `BE` Belgium, `DE` Germany, `FR` France, `ES` Spain, `RU` Russia, `VN` Vietnam, `SG` Singapore, `TH` Thailand.

**Your question:** which countries do the events come from, and how often? Which countries are unusual for a Dutch exchange?

<details><summary>Hint</summary>

Replace `event_type` with `country`, in both places.
</details>
<details><summary>Answer</summary>

```sql
SELECT country, COUNT(*) FROM events GROUP BY country;
```
`NL` shows up the most (20740). Unusual are `SG`, `RU`, `VN` and `TH`.
</details>
<details><summary>Think question: is every unusual country an attack?</summary>

No. `TH` is a customer on holiday in Thailand. A detection that only looks at "different country" raises false alarms. That's why you combine signals.
</details>

### Exercise 6b: only the big groups
**New: filtering groups with `HAVING`.** `WHERE` filters rows **before** they are grouped. `HAVING` filters the groups **after** counting. This is how a SOC finds "more than N times", the base of every threshold alert.
```sql
SELECT country, COUNT(*) FROM events
GROUP BY country
HAVING COUNT(*) > 2000;
```
You get 4 countries: `NL`, `ES`, `DE` and `BE`. `FR` has fewer than 2000 events, so its group is dropped.

**Predict first:** how many event types happen more than 1000 times?
**Your question:** show the event types that happen more than 1000 times.

<details><summary>Hint</summary>

Same as the example, with `event_type` instead of `country`, and `1000` instead of `2000`.
</details>
<details><summary>Answer</summary>

```sql
SELECT event_type, COUNT(*) FROM events
GROUP BY event_type
HAVING COUNT(*) > 1000;
```
3: `login`, `support_account_view` and `withdrawal`.
</details>
<details><summary>Think question: why can't you write `WHERE COUNT(*) > 1000`?</summary>

Because `WHERE` runs before the counting. At that moment there is no count yet. That's exactly why `HAVING` exists.
</details>

---

## Day 3: sorting and joining

### Exercise 7: the biggest bitcoin withdrawal
**Example:**
```sql
SELECT timestamp, user_id, amount_eur, asset FROM events
WHERE event_type = 'withdrawal'
ORDER BY amount_eur DESC LIMIT 5;
```
`ORDER BY ... DESC` sorts from big to small.

**Your question:** what is the biggest withdrawal in BTC, and from which customer?

<details><summary>Hint</summary>

Add a second condition to the `WHERE`, with `AND`.
</details>
<details><summary>Answer</summary>

```sql
SELECT timestamp, user_id, amount_eur, asset FROM events
WHERE event_type = 'withdrawal' AND asset = 'BTC'
ORDER BY amount_eur DESC LIMIT 5;
```
Customer `U00227`, 7061.17 euro.
</details>

### Exercise 8: logins from servers
**Example:**
```sql
SELECT COUNT(*) FROM events
WHERE event_type = 'login' AND network = 'hosting';
```
This gives 261 logins.

**New: counting different customers.** `COUNT(*)` counts rows. If one customer logs in 10 times, they count 10 times. Want to know how many *different* customers there are? Combine `COUNT` with `DISTINCT` from exercise 3:
```sql
SELECT COUNT(DISTINCT user_id) FROM events
WHERE event_type = 'password_reset';
```
This counts how many different customers reset their password. Each customer counts only once.

**Predict first:** do those 261 hosting logins come from many different customers, or from a few?
**Your question:** for how many different customers was there a login from `hosting`?

<details><summary>Hint</summary>

Take the new example, and use the `WHERE` from the hosting query above it.
</details>
<details><summary>Answer</summary>

```sql
SELECT COUNT(DISTINCT user_id) FROM events
WHERE event_type = 'login' AND network = 'hosting';
```
260 different customers.
</details>
<details><summary>Think question: which attack is this?</summary>

Credential stuffing. One server tries leaked passwords on hundreds of accounts. Almost all fail, but a few get in.

The column `result` says if a login worked: `success` or `failure`. Add `AND result = 'success'` to the `COUNT(*)` query: 4 successful logins, from 3 different customers (`U00226` got in twice). You'll build detection CS-001 for this later.
</details>

### Exercise 9: who is the victim
**Example:**
```sql
SELECT e.timestamp, e.event_type, u.name
FROM events e
JOIN users u ON u.user_id = e.user_id
WHERE e.user_id = 'U00005';
```
What's new:
- `JOIN users` sticks the `users` table onto `events`, so you see the name next to each event.
- `events e` and `users u`: `e` and `u` are short names for the two tables.
- `e.timestamp` means: the `timestamp` column from table `e`. `u.name` is the `name` column from table `u`.
- `ON u.user_id = e.user_id` says which rows belong together: the ones with the same customer.

**Your question:** what is the name of `U00918`, and which `mfa_method` does this customer use?

<details><summary>Hint</summary>

Add `u.mfa_method` after `SELECT`, and change the `user_id`.
</details>
<details><summary>Answer</summary>

```sql
SELECT e.timestamp, e.event_type, u.name, u.mfa_method
FROM events e
JOIN users u ON u.user_id = e.user_id
WHERE e.user_id = 'U00918';
```
Sara de Wit, with `sms`.
</details>
<details><summary>Think question: why does `sms` make her vulnerable?</summary>

Whoever takes over her phone number (SIM swap) also gets her SMS codes. With an authenticator app or a passkey this wouldn't have worked.
</details>

### Prep for day 4 (10 minutes)
On day 4 a test checks your work. It needs Python. Install it now, so day 4 is only about SQL: follow [Setup: for the test](../SETUP.md#for-the-test-end-of-week-1). You're done when `python --version` (Mac: `python3 --version`) shows a version number.

---

## Day 4: your first detection

### Exercise 10: how fast did it go?
**New: several values at once.** Want to see two kinds of events? Put them in a list with `IN`:
```sql
SELECT timestamp, event_type FROM events
WHERE user_id = 'U00918'
  AND event_type IN ('password_reset', 'mfa_changed');
```
`IN ('a', 'b')` means: the value is `a` or `b`.

Times look like `2026-10-10T02:54:00Z`: the date, then `T`, then the time. `Z` means UTC (world time).

**Your question:** for `U00005`, how many minutes were there between adding a new address (`withdrawal_address_added`) and the withdrawal (`withdrawal`)?

<details><summary>Hint</summary>

Take the example above. Change the customer to `U00005` and the two events to `'withdrawal_address_added'` and `'withdrawal'`. Then look at `timestamp`.
</details>
<details><summary>Answer</summary>

```sql
SELECT timestamp, event_type FROM events
WHERE user_id = 'U00005'
  AND event_type IN ('withdrawal_address_added', 'withdrawal');
```
4 minutes: 02:50 new address, 02:54 withdrawal.
</details>

### Exercise 10b: what joining a table to itself does
In exercise 9 you joined two different tables. A detection often joins **the same table to itself**, to put two events of one customer next to each other in one row.

Picture it with 2 rows of `U00005`:

| | timestamp | event_type | address |
|---|---|---|---|
| row **a** | 02:50 | withdrawal_address_added | 0x0ee2... |
| row **w** | 02:54 | withdrawal | 0x0ee2... |

After the join they become **one** row with both times side by side:

| a.timestamp | a.event_type | w.timestamp | w.event_type |
|---|---|---|---|
| 02:50 | withdrawal_address_added | 02:54 | withdrawal |

Now you can subtract the two times. That's the trick behind exercise 11.

**Careful:** a join pairs **every** matching row with **every** other one. Try it.

**Predict first:** `U00005` has 19 events. If you join his events to themselves on `user_id` only, how many rows do you get?
```sql
SELECT COUNT(*)
FROM events a
JOIN events w ON w.user_id = a.user_id
WHERE a.user_id = 'U00005';
```

<details><summary>Answer</summary>

361. That's 19 × 19: every event paired with every event, including itself.
</details>

**Your question:** add two conditions to the `ON` part so only "new address" on the `a` side and "withdrawal" on the `w` side are paired. How many rows are left?

<details><summary>Hint</summary>

After `ON w.user_id = a.user_id` add `AND a.event_type = 'withdrawal_address_added' AND w.event_type = 'withdrawal'`.
</details>
<details><summary>Answer</summary>

```sql
SELECT COUNT(*)
FROM events a
JOIN events w ON w.user_id = a.user_id
 AND a.event_type = 'withdrawal_address_added'
 AND w.event_type = 'withdrawal'
WHERE a.user_id = 'U00005';
```
1 row: exactly the pair from the picture. The conditions in `ON` decide which rows are allowed to pair up.
</details>

### Exercise 11: read a real detection
This is a detection: it looks for withdrawals to an address that was added less than 60 minutes earlier. Read it line by line with the cheat sheet next to you.

```sql
SELECT DISTINCT a.user_id AS entity
FROM events a
JOIN events w
  ON w.user_id = a.user_id
 AND w.address = a.address
 AND w.event_type = 'withdrawal'
WHERE a.event_type = 'withdrawal_address_added'
  AND (julianday(w.timestamp) - julianday(a.timestamp)) * 24 * 60 BETWEEN 0 AND 60;
```

**New in this query** (read this first):
- `AS entity` gives the column a different name. The test looks for a column called `entity`.
- `FROM events a JOIN events w` uses the same table twice, with two short names. Like `e` and `u` in exercise 9, but now `events` twice.
- After `ON` there are now three conditions with `AND`. A row from `a` and a row from `w` only belong together if all three match.
- `julianday(...)` turns a time into a number of days. The difference × 24 × 60 = the number of minutes in between.
- Here `*` means "multiply" and `-` means "minus" (in exercise 1, `*` meant "all columns"). The part in brackets is calculated first, like in maths.
- `BETWEEN 0 AND 60` means: from 0 up to and including 60.

**Reading questions** (answer them yourself first):
1. What is `a`, and what is `w`?
2. Why is `w.address = a.address` in there?
3. What does the last line calculate?

<details><summary>Answers</summary>

1. The same table `events`, twice. `a` is the address being added, `w` is the withdrawal.
2. So you only find withdrawals to the address that was just added.
3. The number of minutes between adding and withdrawing. Only 0 to 60 minutes counts.
</details>

**Predict first:** how many customers does this detection find? Then run it.

<details><summary>Answer</summary>

5 customers. But you know there are only 2 SIM-swap victims...
</details>

### Exercise 12: let the test check it
The test needs Python, which you installed at the end of day 3.

**Put your query in the detection file**
1. Open the repo folder you unzipped in Setup (it may be called `crypto-soc-detection-main`), then `detections` → `ATO-001-sim-swap-takeover`.
2. Open `detection.sql` in a text editor:
   - **Windows:** right-click → **Open with** → **Notepad**.
   - **Mac:** right-click → **Open With** → **TextEdit**. If you see colors or fonts, choose **Format → Make Plain Text**.
3. Paste the query from exercise 11 under the lines that start with `--`. Save (**Ctrl + S** / **Cmd + S**).

**Run the test**
1. Open a terminal:
   - **Windows:** press the Windows key, type `PowerShell`, press Enter.
   - **Mac:** press **Cmd + Space**, type `Terminal`, press Return.
2. Type `cd ` (with a space after it), drag the repo folder from File Explorer or Finder into the window, and press Enter. Now the terminal is in your repo folder.
3. Type this and press Enter:
   - **Windows:** `python tests\run_detections.py`
   - **Mac:** `python3 tests/run_detections.py`

You get a table with these columns:
- **Detection:** the name of the detection
- **Status:** `PASS` = perfect, `WORK` = works but not perfect yet, `TODO` = still empty (you'll do those later)
- **Caught:** attacks your detection found
- **False alarms:** customers you flagged by mistake
- **Missed:** attacks your detection missed

For ATO-001 you see: Caught 2, False alarms 3, Missed 0. You caught both attacks, but also 3 customers who weren't SIM-swap victims.

**Your question:** find out what the 2 real victims have that the 3 others don't. Run this, and compare the columns:
```sql
SELECT user_id, timestamp, event_type, network, country, auth_method
FROM events
WHERE user_id IN ('U00005', 'U00918', 'U00226', 'U00287', 'U00669')
  AND event_type IN ('password_reset', 'mfa_changed', 'withdrawal_address_added');
```

<details><summary>Hint</summary>

Look at which customers have a `password_reset` or `mfa_changed`, and through which `network`.
</details>
<details><summary>Answer</summary>

Only `U00005` and `U00918` had a `password_reset` and an `mfa_changed` through `sms`, from a `mobile` network, right before the withdrawal. The other three are attacks too, but a different kind: credential stuffing and address poisoning. You'll build separate detections for those.

In week 2 you improve ATO-001 until it only finds the 2 real victims. Write your approach in the detection's README already.
</details>

---

## Day 5: on your own

Today there are no examples and no hints. Only the [cheat sheet](cheatsheet.md). This is the step from "I can follow" to "I can write it". Take your time. Stuck for more than 10 minutes? Then look back at the exercise the cheat sheet points to.

**One new thing first: empty values.** An empty cell in SQL is `NULL`. You can't find it with `= ''` or `= NULL`. Use `IS NULL`:
```sql
SELECT COUNT(*) FROM events
WHERE event_type = 'support_account_view' AND ticket_id IS NULL;
```
This counts support-agent views without a ticket: 180.

### Exercise 13: big withdrawals per country
**Your question:** per country, how many withdrawals were above 1000 euro? Biggest first.

<details><summary>Answer</summary>

```sql
SELECT country, COUNT(*) FROM events
WHERE event_type = 'withdrawal' AND amount_eur > 1000
GROUP BY country
ORDER BY COUNT(*) DESC;
```
`NL` 102, `DE` 31, `ES` 16, `FR` 14, `BE` 8, `VN` 1, `RU` 1. The `VN` and `RU` ones are the two SIM-swap thefts.

Got all countries with much higher numbers? You probably forgot `event_type = 'withdrawal'`, so deposits counted too.
</details>

### Exercise 14: your second detection (INS-001)
A bribed support agent opens customer accounts without a ticket (like the Coinbase case).

**Your question:** which support agent opened accounts without a ticket, and how many times? Then turn it into a detection: return the agent as a column named `entity`, put it in `detections/INS-001-support-agent-no-ticket/detection.sql`, and run the test like in exercise 12.

<details><summary>Answer</summary>

```sql
SELECT agent_id AS entity, COUNT(*)
FROM events
WHERE event_type = 'support_account_view' AND ticket_id IS NULL
GROUP BY agent_id;
```
`AG07`, 180 times. The test shows INS-001 as **PASS**: caught 1, false alarms 0, missed 0. Your first perfect detection.

The busy agent `AG03` is not flagged: on their busy day every view had a ticket. That's the look-alike this detection has to ignore.
</details>

### Exercise 15: week 1 quiz
Answer from memory first, then run the query to check. Write your guess down before you run it.

1. `SELECT COUNT(*) FROM users WHERE mfa_method = 'passkey';`
2. `SELECT COUNT(DISTINCT agent_id) FROM events;`. There are 12 support agents. Does `NULL` count as a 13th?
3. `SELECT COUNT(*) FROM events WHERE event_type = 'login' AND result = 'failed';`
4. `SELECT amount_eur FROM events WHERE event_type = 'withdrawal' ORDER BY amount_eur LIMIT 1;`. Is this the biggest or the smallest withdrawal?

<details><summary>Answers</summary>

1. **116.** Got 0? Check the spelling and the quotes: `'passkey'`, all lower case.
2. **12.** `COUNT(DISTINCT ...)` skips `NULL`. Thought 13? Remember: `NULL` is "no value", not a value.
3. **0.** The value is `'failure'`, not `'failed'`. This is why you check values with `DISTINCT` first. With `'failure'` you get 986.
4. **The smallest**, 1.01. `ORDER BY` without `DESC` sorts small to big.
</details>

You can now say honestly: "I can filter, count, group, set thresholds and join log tables in SQL, and I built two tested detections."
