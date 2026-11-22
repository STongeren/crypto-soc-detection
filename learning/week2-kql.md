# Week 2: KQL

KQL (Kusto Query Language) is the language of Microsoft Sentinel and Microsoft Defender, two of the most used tools in SOC teams. Crypto SOC job postings name it (for example Keyrock and Scrypt). Teams on Elastic use close cousins (Kibana KQL and ES|QL) built on the same ideas.

KQL looks like SQL, but it reads top to bottom: you start with a table and pipe it through steps.

Same rules as week 1: example first, then your question, hints and answers hidden, predict before you look. Keep the [KQL cheat sheet](cheatsheet-kql.md) open next to it. Every query and answer below was tested in the free practice environment.

Days 2 to 4 start with a 2-minute **warm-up**: one query from earlier, from memory. Remembering is what makes it stick.

---

## Before you start (10 minutes, once)

You run KQL in your browser. Nothing to install.

1. You need a free Microsoft account. Have an Outlook or Hotmail address? That works. No account? Make one at [signup.live.com](https://signup.live.com).
2. Open the free practice environment: **[dataexplorer.azure.com/clusters/help/databases/Samples](https://dataexplorer.azure.com/clusters/help/databases/Samples)** and sign in.
3. You see a big text box: that's where you type. On the left you see the **help** cluster with the **Samples** database.
4. Type a query and press **Shift + Enter** (or click **Run** above the text box). The result appears below.

**Important:** the web page runs the query your cursor is in, and it treats an empty line as the end of a query. So never leave an empty line inside one query.

Days 1 and 2 use `StormEvents`, a free table of 59,066 US storms from 2007 that Microsoft provides. Days 3 and 4 use events from your own crypto exchange.

---

## Day 1: SQL to KQL

### Exercise 1: count and look
**Example:**
```kql
StormEvents
| count
```
Read it as: "take the table `StormEvents`, **then** count the rows". The `|` (the pipe) means "then". Every line after it is one step.

You get 59066.

Now look at a few rows and only some columns:
```kql
StormEvents
| take 5
| project State, EventType, DamageProperty
```
- `take 5` = give me any 5 rows (like `LIMIT 5` in SQL). Which 5 is not promised: they can differ each time.
- `project` = only these columns (like the column list after `SELECT` in SQL)

**Your question:** show 10 rows with only the columns `StartTime`, `State` and `EventType`.

<details><summary>Hint</summary>

Take the second example. Change `5` to `10` and change the column names after `project`.
</details>
<details><summary>Answer</summary>

```kql
StormEvents
| take 10
| project StartTime, State, EventType
```
Your 10 rows can be different from someone else's. `take` is for a quick look, never for an answer.
</details>

### Exercise 2: which values exist
**Example:**
```kql
StormEvents
| distinct State
```
`distinct` shows each value once, like `SELECT DISTINCT` in SQL.

You can add more steps with another `|`. This counts how many different states there are:
```kql
StormEvents
| distinct State
| count
```

**Predict first:** how many different storm types (`EventType`) are there?
**Your question:** count the different values of `EventType`.

<details><summary>Hint</summary>

Same as the second example, with `EventType` instead of `State`.
</details>
<details><summary>Answer</summary>

```kql
StormEvents
| distinct EventType
| count
```
46.
</details>

### Exercise 3: filter
**Example:**
```kql
StormEvents
| where State == "TEXAS"
| count
```
`where` filters, like in SQL. Three differences:
- KQL compares with **two** equals signs: `==`.
- `==` is **case-sensitive**: `"TEXAS"` and `"texas"` are different. Want to ignore case? Use `=~`.
- Text can go between `"double"` or `'single'` quotes. Both work.

Two conditions? Use `and`, just like `AND` in SQL:
```kql
StormEvents
| where State == "TEXAS" and EventType == "Hail"
| count
```

**Predict first:** what does `StormEvents | where State == "texas" | count` give?

<details><summary>Answer</summary>

0. The data says `TEXAS` in capitals, and `==` checks case. With `=~ "texas"` you get the Texas rows again. In detection rules, `==` is preferred: it's faster and exact.
</details>

**Your question:** how many floods (`"Flood"`) were there in Texas?

<details><summary>Hint</summary>

Take the second example and change `"Hail"` to `"Flood"`.
</details>
<details><summary>Answer</summary>

```kql
StormEvents
| where State == "TEXAS" and EventType == "Flood"
| count
```
146.
</details>

---

## Day 2: sorting, calculating, counting per group, and time

**Warm-up (from memory, in DB Browser):** write the SQL that counts the password resets that went through SMS.
<details><summary>Answer</summary>

```sql
SELECT COUNT(*) FROM events WHERE event_type = 'password_reset' AND auth_method = 'sms';
```
2.
</details>

### Exercise 4: the worst flood
**Example:**
```kql
StormEvents
| where State == "TEXAS" and EventType == "Flood"
| top 5 by DamageProperty
| project StartTime, State, DamageProperty
```
`top 5 by DamageProperty` = the 5 rows with the highest `DamageProperty` (damage in US dollars). Like `ORDER BY ... DESC LIMIT 5` in SQL.

**Your question:** what was the most expensive flood in Texas: on which day, and how much damage?

<details><summary>Hint</summary>

Run the example and look at the first row. Want only that one? Use `top 1`.
</details>
<details><summary>Answer</summary>

```kql
StormEvents
| where State == "TEXAS" and EventType == "Flood"
| top 1 by DamageProperty
| project StartTime, State, DamageProperty
```
August 18, 2007, 5,000,000 dollars. (Depending on your settings the date shows as `18/08/2007` or `8/18/2007`.)
</details>

### Exercise 5: add a calculated column
**Example:**
```kql
StormEvents
| where State == "TEXAS" and EventType == "Flood"
| top 5 by DamageProperty
| extend Duration = EndTime - StartTime
| project StartTime, EndTime, Duration
```
- `extend Duration = EndTime - StartTime` **adds** a new column called `Duration` and keeps all the others. KQL can subtract times directly. SQL needed `julianday` for that.
- `project` then picks the columns you want to see. (`project` can also make a column, but then it drops every other one. Detection rules use `extend` all the time.)

A duration looks like `1.02:15:00`: that's 1 day, 2 hours and 15 minutes. Without a day in front, `05:00:00` is 5 hours.

**Your question:** how long did the most expensive Texas flood last?

<details><summary>Answer</summary>

The first row: `1.01:30:00`. That's 1 day, 1 hour and 30 minutes.
</details>

### Exercise 6: count per group
**Example:**
```kql
StormEvents
| summarize Total = count() by State
| sort by Total desc
```
- `summarize ... by State` makes a group per state, like `GROUP BY` in SQL.
- `Total = count()` counts the rows per group and calls that column `Total`. Note the difference: `| count` (exercise 1) counts the whole table in one step. `count()` with brackets is used **inside** `summarize`.
- `sort by Total desc` puts the biggest first. (`asc` = smallest first. Without either, KQL sorts biggest first: the opposite of SQL.)

Texas is on top with 4701.

**Predict first:** which storm type happens most often?
**Your question:** count per `EventType` and put the biggest on top.

<details><summary>Hint</summary>

Change `State` to `EventType`. The rest stays the same.
</details>
<details><summary>Answer</summary>

```kql
StormEvents
| summarize Total = count() by EventType
| sort by Total desc
```
`Thunderstorm Wind`, 13015 times.
</details>

### Exercise 7: a threshold
In SQL you used `HAVING`. In KQL you just add a `where` **after** the `summarize`, because each step works on the result of the step before it:
```kql
StormEvents
| summarize Total = count() by EventType
| where Total > 10000
```
This keeps only the storm types with more than 10000 events: `Thunderstorm Wind` and `Hail`.

**Your question:** which states had more than 2000 storm events?

<details><summary>Answer</summary>

```kql
StormEvents
| summarize Total = count() by State
| where Total > 2000
| sort by Total desc
```
5: `TEXAS` 4701, `KANSAS` 3166, `IOWA` 2337, `ILLINOIS` 2022, `MISSOURI` 2016.
</details>

### Exercise 8: time
A real SOC never searches all the data. Every query starts with a time window, almost always with `ago()`:
```kql
StormEvents
| where StartTime > ago(1d)
| count
```
`ago(1d)` means "1 day before now". So this counts storms from the last 24 hours.

**Predict first:** what do you get?

<details><summary>Answer</summary>

0. The storms are from 2007, so none happened in the last day. In Sentinel you'd write `| where TimeGenerated > ago(1d)` as the first line of almost every query. Here the data is old, so we use fixed dates with `between` instead.
</details>

**New: counting per time slot with `bin()`.** `bin(StartTime, 7d)` rounds every time down to its week, so `summarize` can count per week:
```kql
StormEvents
| where StartTime between (datetime(2007-01-01) .. datetime(2007-12-31)) and DamageCrops > 0
| summarize EventCount = count() by bin(StartTime, 7d)
| render timechart
```
`render timechart` draws it as a line chart. You see a peak in summer.

**Your question:** count all storms per **30 days** (`30d`) in 2007 and draw it. Which period had the most?

<details><summary>Hint</summary>

Take the example, remove `and DamageCrops > 0`, and change `7d` to `30d`.
</details>
<details><summary>Answer</summary>

```kql
StormEvents
| where StartTime between (datetime(2007-01-01) .. datetime(2007-12-31))
| summarize EventCount = count() by bin(StartTime, 30d)
| render timechart
```
The highest point is the 30 days starting June 14, 2007: 7,531 storms. Hover over the line to see the numbers, or remove `render timechart` to see the table.
</details>

---

## Day 3: your own exchange data

**Warm-up (from memory, in DB Browser):** write the SQL that shows the event types happening more than 1000 times.
<details><summary>Answer</summary>

```sql
SELECT event_type, COUNT(*) FROM events GROUP BY event_type HAVING COUNT(*) > 1000;
```
</details>

### How the practice table works
Open **[week2-events.kql](week2-events.kql)**. It contains 23 events from your exchange: password resets, 2FA changes, new withdrawal addresses and withdrawals of 7 customers. Some are attacks, some are normal.

It starts with `let Events = datatable(...)`. What's new:
- `datatable(...)` builds a small table right inside your query. First the columns with their type, then the rows.
- The types: `datetime` = a date and time, `string` = text, `real` = a number with decimals. `real(null)` = an empty number (a password reset has no amount).
- `let Events = ...;` gives that table a name, `Events`, so you can use it below. The `;` at the end closes the `let`.

**How to use it in every exercise below:**
1. Copy the whole file and paste it at the top of the text box.
2. Type your query **directly under it**, with no empty line in between.
3. Click anywhere in it and press **Shift + Enter**.

The whole thing looks like this (the rows are shortened here):
```kql
let Events = datatable(timestamp:datetime, user_id:string, ...) [
    ...
];
Events
| count
```
This gives 23.

### Exercise 9: the SMS resets
**Example (under the table):**
```kql
Events
| where event_type == "password_reset"
```

**Your question:** show only the password resets that went through `"sms"`. Which customers are they?

<details><summary>Hint</summary>

Add `and auth_method == "sms"` to the `where` line.
</details>
<details><summary>Answer</summary>

```kql
Events
| where event_type == "password_reset" and auth_method == "sms"
```
2 rows: `U00005` (from `RU`) and `U00918` (from `VN`). The same two victims you found with SQL.
</details>

### Exercise 10: events and customers per network
**New: `dcount()`** counts **different** values inside `summarize`, like `COUNT(DISTINCT ...)` in SQL:
```kql
Events
| summarize Customers = dcount(user_id)
```
This gives 7. (`dcount` is very close but not always exact on huge tables. Need it exact? Use `count_distinct()`.)

**Your question:** per `network`, show how many events **and** how many different customers there are. You can put two counts in one `summarize`, separated by a comma.

<details><summary>Hint</summary>

`summarize Total = count(), Customers = dcount(user_id) by network`
</details>
<details><summary>Answer</summary>

```kql
Events
| summarize Total = count(), Customers = dcount(user_id) by network
| sort by Total desc
```
`residential` 11 events from 4 customers, `mobile` 10 from 3, `hosting` 2 from 1.
</details>
<details><summary>Think question: which customer used a data-center server, and why is that strange?</summary>

`U00226` in `SG`: a new address and a withdrawal 2 minutes later. Customers don't use servers in data centers. This account was taken over in the credential-stuffing attack.
</details>

### Exercise 11: spot the poisoned address
**New: matching the start of a text.** `startswith` finds values that begin with something:
```kql
Events
| where address startswith "0x2e2e"
| project timestamp, user_id, event_type, address
```

**Your question:** run it and compare the addresses. How many different addresses start with `0x2e2e`, and what's strange about them?

<details><summary>Hint</summary>

Look at the first 6 and the last 4 characters of each address. Then look at the middle.
</details>
<details><summary>Answer</summary>

4 rows, all from `U00669`, with 2 different addresses. The first two withdrawals go to `0x2e2ef17c...916a`. The last two rows use `0x2e2ee9a6...916a`. Same start (`0x2e2e`), same end (`916a`), different middle. The customer copied a look-alike address an attacker had planted in their history and sent 8,693.85 euro to it. That's **address poisoning**. You'll build detection AP-001 for this later.
</details>

---

## Day 4: your detection in KQL

**Warm-up (from memory, in DB Browser):** write the SQL that shows which support agent opened accounts without a ticket.
<details><summary>Answer</summary>

```sql
SELECT agent_id, COUNT(*) FROM events
WHERE event_type = 'support_account_view' AND ticket_id IS NULL
GROUP BY agent_id;
```
</details>

### Exercise 12: read the detection
This is the same detection as week 1, exercise 11, now in KQL. Paste it under the table:

```kql
let Added = Events
    | where event_type == "withdrawal_address_added"
    | project user_id, address, added_time = timestamp;
Events
| where event_type == "withdrawal"
| join kind=inner Added on user_id, address
| where timestamp between (added_time .. added_time + 60m)
| distinct user_id
```

**New in this query** (read this first):
- A second `let`: `Added` is a small table with only the "new address" events. `added_time = timestamp` renames the column so you don't mix it up with the withdrawal's time.
- The lines starting with spaces belong to the `let` above them. The spaces are only for reading.
- `join kind=inner Added on user_id, address` sticks each withdrawal to the "new address" event with the same customer and the same address. `kind=inner` = keep every row that has a match on both sides.
- **Always write `kind=`.** Without it, KQL uses a different default (`innerunique`) that keeps only one row per key on the left side and can silently drop matches.
- `60m` means 60 minutes. KQL also knows `h` (hours) and `d` (days).
- `between (a .. b)` = from `a` up to and including `b`. Note the two dots.

In a real Sentinel rule, the first step on `Events` would also be a time window like `| where timestamp > ago(1h)`. It's left out here because the practice data is from October and November 2026.

**Reading questions** (answer them yourself first):
1. What is in `Added`?
2. Why does the `join` use `user_id` **and** `address`?
3. Which customer will be missing because of the last `where`, and why?

<details><summary>Answers</summary>

1. Only the "new address" events: customer, address and the time it was added.
2. So a withdrawal only matches the address that same customer just added.
3. `U00098`, the traveller in Thailand. They added the address and withdrew about 26 hours later. That's outside the 60 minutes.
</details>

**Predict first:** how many customers will it find? Then run it.

<details><summary>Answer</summary>

5: `U00005`, `U00918`, `U00226`, `U00287` and `U00669`. The same 5 as in SQL: 2 SIM-swap victims and 3 false alarms for this detection.
</details>

### Exercise 13: a quick fix, and why it's a trap
**New: filtering after a join.** You can add a `where` at any step. This keeps only withdrawals above 1000 euro:
```kql
| where amount_eur > 1000
```

**Your question:** add one `where` line (above `distinct`) so that only the 2 SIM-swap victims are left. Look at the columns of the 5 results: which value do only the 2 victims have?

<details><summary>Hint</summary>

Run the query without `distinct user_id` to see all columns. You'll also see `user_id1` and `address1`: the join copies the columns of `Added`, and KQL adds a `1` to names it already has. Compare `network`.
</details>
<details><summary>Answer</summary>

```kql
let Added = Events
    | where event_type == "withdrawal_address_added"
    | project user_id, address, added_time = timestamp;
Events
| where event_type == "withdrawal"
| join kind=inner Added on user_id, address
| where timestamp between (added_time .. added_time + 60m)
| where network == "mobile"
| distinct user_id
```
2 customers: `U00005` and `U00918`.
</details>
<details><summary>Think question: why is this a trap?</summary>

You picked a column that happens to split **this** data, by looking at the answers. That's called **overfitting**. An attacker on home internet or a VPN slips through, and many honest customers use their phone. A good rule describes the **attack**: an SMS password reset shortly before the new address. You build that next.
</details>

### Exercise 14: the strong rule
**New: joining a third piece.** You can make another `let` and join it too. This one holds the SMS password resets:
```kql
let ResetSms = Events
    | where event_type == "password_reset" and auth_method == "sms"
    | project user_id, reset_time = timestamp;
```
To combine it, you join on `user_id` and check that the reset came at most 1 hour **before** the new address: `reset_time between (added_time - 1h .. added_time)`.

**Your question:** build the full rule: `Added`, `ResetSms`, the withdrawal within 60 minutes, and the reset within 1 hour before the new address. No `network` filter.

<details><summary>Hint</summary>

Put both `let` blocks above `Events`. After the first `join` and its `where`, add `| join kind=inner ResetSms on user_id` and then `| where reset_time between (added_time - 1h .. added_time)`.
</details>
<details><summary>Answer</summary>

```kql
let Added = Events
    | where event_type == "withdrawal_address_added"
    | project user_id, address, added_time = timestamp;
let ResetSms = Events
    | where event_type == "password_reset" and auth_method == "sms"
    | project user_id, reset_time = timestamp;
Events
| where event_type == "withdrawal"
| join kind=inner Added on user_id, address
| where timestamp between (added_time .. added_time + 60m)
| join kind=inner ResetSms on user_id
| where reset_time between (added_time - 1h .. added_time)
| distinct user_id
```
2 customers: `U00005` and `U00918`. Same result as exercise 13, but now because of **how the attack works**, not because of one lucky column. Write this reasoning in the Blind spots and False positives sections of the ATO-001 README.
</details>

### Exercise 15: save it, and update your SQL
1. In the folder `detections/ATO-001-sim-swap-takeover`, make a new file `detection.kql`:
   - **Windows:** right-click → **New** → **Text Document**, rename it to `detection.kql` and say **Yes** to the extension warning.
   - **Mac:** open TextEdit, choose **Format → Make Plain Text**, and save it as `detection.kql`.
2. Paste your strong rule from exercise 14 in it (without the practice table) and save.
3. **Now in SQL (retrieval):** open `detection.sql` from week 1 and add the same idea: a third copy of `events`, called `r`, for the SMS reset. Run the test.

<details><summary>Hint</summary>

Add this between the existing `JOIN` and `WHERE`:
```sql
JOIN events r
  ON r.user_id = a.user_id
 AND r.event_type = 'password_reset'
 AND r.auth_method = 'sms'
```
And add one more line to the `WHERE`:
```sql
  AND (julianday(a.timestamp) - julianday(r.timestamp)) * 24 * 60 BETWEEN 0 AND 60
```
</details>
<details><summary>Answer</summary>

```sql
SELECT DISTINCT a.user_id AS entity
FROM events a
JOIN events w
  ON w.user_id = a.user_id
 AND w.address = a.address
 AND w.event_type = 'withdrawal'
JOIN events r
  ON r.user_id = a.user_id
 AND r.event_type = 'password_reset'
 AND r.auth_method = 'sms'
WHERE a.event_type = 'withdrawal_address_added'
  AND (julianday(w.timestamp) - julianday(a.timestamp)) * 24 * 60 BETWEEN 0 AND 60
  AND (julianday(a.timestamp) - julianday(r.timestamp)) * 24 * 60 BETWEEN 0 AND 60;
```
The test shows ATO-001 as **PASS**: caught 2, false alarms 0, missed 0. Set SQL and KQL to **done** in the README of ATO-001.
</details>

---

## Day 5: on your own

No examples, no hints. Only the [KQL cheat sheet](cheatsheet-kql.md).

### Exercise 16: tornadoes
**Your question:** which 3 states had the most `"Tornado"` events in `StormEvents`? Biggest first.

<details><summary>Answer</summary>

```kql
StormEvents
| where EventType == "Tornado"
| summarize Total = count() by State
| top 3 by Total
```
`TEXAS` 216, `KANSAS` 161 and `OKLAHOMA` 58.
</details>

### Exercise 17: busy withdrawers
**Your question:** in the practice table (`Events`), which customers made more than 2 withdrawals?

<details><summary>Answer</summary>

```kql
Events
| where event_type == "withdrawal"
| summarize Total = count() by user_id
| where Total > 2
```
`U00226` with 4 and `U00669` with 3.

Got every customer? You forgot `where Total > 2` after the `summarize`.
</details>

### Exercise 18: week 2 quiz
Answer from memory first, then run to check.

1. `StormEvents | where State == "texas" | count`
2. `StormEvents | summarize Total = count() by State | sort by Total` : is the first row the biggest or the smallest?
3. What goes wrong if you write `join` without `kind=`?
4. Which one keeps all other columns: `extend` or `project`?

<details><summary>Answers</summary>

1. **0.** `==` is case-sensitive. Use `"TEXAS"` or `=~`.
2. **The biggest.** KQL sorts biggest first by default, the opposite of SQL.
3. KQL then uses `innerunique`, which can silently drop matches. Always write `kind=inner` (or another kind) yourself.
4. **`extend`.** `project` keeps only what you name.
</details>

You can now say honestly: "I can write KQL with filters, time windows, aggregations, thresholds and joins, and I turned one detection into a tested rule in both SQL and KQL."

---

## Day 6 (extra): what Sentinel queries use every day

Optional. Do it when days 1 to 5 feel easy. These five show up in almost every real Sentinel or Defender query.

### Exercise 19: count only some rows (`countif`)
**New: `countif()`** counts only the rows where a condition is true, inside `summarize`:
```kql
StormEvents
| summarize StormsWithCropDamage = countif(DamageCrops > 0) by State
| top 5 by StormsWithCropDamage
```
`IOWA` is on top with 359. One `summarize` can now hold a total **and** a conditional count, like "logins" and "failed logins" per user.

**Your question:** for each state, show all storms **and** the storms with crop damage. Top 5 by crop damage.

<details><summary>Answer</summary>

```kql
StormEvents
| summarize Total = count(), StormsWithCropDamage = countif(DamageCrops > 0) by State
| top 5 by StormsWithCropDamage
```
`IOWA` 2337 storms, 359 with crop damage.
</details>

### Exercise 20: fields inside JSON
Real logs often hide details in a JSON column. In Sentinel's `SigninLogs`, the location sits inside `LocationDetails`. `StormEvents` has one too, called `StormSummary`:
```kql
StormEvents
| take 1
| project StormSummary
```
You see something like `{"TotalDamages":0, ..., "Details":{"Description":"...","Location":"ATLANTIC SOUTH"}}`.

**New: reading a field inside JSON.** Use dots to walk into it, and `tostring()` to turn it into normal text:
```kql
StormEvents
| extend Location = tostring(StormSummary.Details.Location)
| where Location == "ATLANTIC SOUTH"
| count
```
193.

**Your question:** how many storms have a `TotalDamages` (inside `StormSummary`) above 1,000,000? Numbers use `toreal()` instead of `tostring()`.

<details><summary>Answer</summary>

```kql
StormEvents
| where toreal(StormSummary.TotalDamages) > 1000000
| count
```
658.
</details>

### Exercises 21 to 23: back to your exchange
Paste the [practice table](week2-events.kql) above each of these.

**Exercise 21: everything one customer did (`make_set`).** `make_set()` collects all the different values into one list:
```kql
Events
| summarize Countries = make_set(country), Networks = make_set(network) by user_id
```
**Predict first:** which customer has more than one country?

<details><summary>Answer</summary>

`U00226`: `["NL","SG"]` and `["residential","hosting"]`. A customer suddenly using a server in Singapore next to their home network is exactly what an analyst looks for.
</details>

**Exercise 22: the latest event per customer (`arg_max`).** `arg_max(timestamp, *)` keeps, per group, the whole row with the highest `timestamp`:
```kql
Events
| summarize arg_max(timestamp, *) by user_id
| project user_id, timestamp, event_type
```
**Predict first:** what kind of event is everyone's latest?

<details><summary>Answer</summary>

A `withdrawal`, for all 7 customers. In a SOC you use `arg_max` for "the last sign-in per user" or "the latest status per device".
</details>

**Exercise 23: what's missing (`leftanti`).** `join kind=leftanti` keeps the rows on the left that have **no** match on the right. Like `LEFT JOIN ... IS NULL` in SQL:
```kql
Events
| where event_type == "withdrawal"
| join kind=leftanti (Events | where event_type == "password_reset") on user_id
| distinct user_id
```
**Predict first:** which customers withdrew without ever resetting their password?

<details><summary>Answer</summary>

4: `U00287`, `U00098`, `U00669` and `U00226`. The other three (`U00005`, `U00918`, `U00355`) had a reset. Note that two of these four are attack victims too (poisoning and credential stuffing): a reset is a signal for SIM swap, not for every attack.
</details>
