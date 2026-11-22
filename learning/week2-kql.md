# Week 2: KQL

KQL (Kusto Query Language) is the language of Microsoft Sentinel, Microsoft Defender and Azure Data Explorer. Bitpanda's SOC Analyst job asks for it. It looks like SQL, but it reads top to bottom: you start with a table and pipe it through steps.

Same rules as week 1: example first, then your question, hints and answers hidden, predict before you look. Every query and answer below was tested in the free practice environment. Keep the [KQL cheat sheet](cheatsheet-kql.md) open next to it.

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
- `take 5` = give me 5 rows (like `LIMIT 5` in SQL)
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
`take` gives random rows, so your 10 rows can be different from someone else's. That's fine.
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
`where` filters, like in SQL. Two differences:
- KQL compares with **two** equals signs: `==`. One `=` gives an error.
- Text can go between `"double"` or `'single'` quotes. Both work.

Two conditions? Use `and`, just like `AND` in SQL:
```kql
StormEvents
| where State == "TEXAS" and EventType == "Hail"
| count
```

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

## Day 2: sorting, calculating and counting per group

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

### Exercise 5: calculate a new column
**Example:**
```kql
StormEvents
| where State == "TEXAS" and EventType == "Flood"
| top 5 by DamageProperty
| project StartTime, EndTime, Duration = EndTime - StartTime
```
`Duration = EndTime - StartTime` makes a new column called `Duration`: the end time minus the start time. KQL can subtract times directly. SQL needed `julianday` for that.

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
- `Total = count()` counts the rows per group and calls that column `Total`.
- `sort by Total desc` puts the biggest first. (`asc` = smallest first.)

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

---

## Day 3: your own exchange data

Now you leave the storms and go back to your crypto exchange.

### How the practice table works
Open **[week2-events.kql](week2-events.kql)**. It contains 23 events from your exchange: password resets, 2FA changes, new withdrawal addresses and withdrawals of 7 customers. Some are attacks, some are normal.

It starts with `let Events = datatable(...)`. What's new:
- `datatable(...)` builds a small table right inside your query. First the column names and types, then the rows.
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

### Exercise 7: the SMS resets
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

### Exercise 8: count per network
**Your question:** count how many of the 23 events came from each `network`. Use exercise 6 as your example.

<details><summary>Hint</summary>

`summarize Total = count() by network`
</details>
<details><summary>Answer</summary>

```kql
Events
| summarize Total = count() by network
| sort by Total desc
```
`residential` 11, `mobile` 10, `hosting` 2.
</details>
<details><summary>Think question: which 2 events came from a data-center server, and why is that strange?</summary>

Both are from `U00226` in `SG`: a new address and a withdrawal 2 minutes later. Customers don't use servers in data centers. This account was taken over in the credential-stuffing attack.
</details>

### Exercise 9: spot the poisoned address
**Example (under the table):**
```kql
Events
| where user_id == "U00669"
| project timestamp, event_type, address
```

**Your question:** run it and compare the addresses of the 4 rows. What's strange about the last two?

<details><summary>Hint</summary>

Look at the first 6 and the last 4 characters of each address. Then look at the middle.
</details>
<details><summary>Answer</summary>

The first two withdrawals go to `0x2e2ef17c...916a`. The last two rows use `0x2e2ee9a6...916a`. Same start (`0x2e2e`), same end (`916a`), different middle. The customer copied a look-alike address an attacker had planted in their history and sent 8,693.85 euro to it. That's **address poisoning**. You'll build detection AP-001 for this later.
</details>

---

## Day 4: your detection in KQL

### Exercise 10: read the detection
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
- `join kind=inner Added on user_id, address` sticks each withdrawal to the "new address" event with the same customer and the same address. `kind=inner` = only keep rows that have a match on both sides.
- `60m` means 60 minutes. KQL also knows `h` (hours) and `d` (days).
- `between (a .. b)` = from `a` up to and including `b`. Note the two dots.

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

### Exercise 11: tune it
**New: filtering after a join.** You can add a `where` at any step. This keeps only withdrawals above 1000 euro:
```kql
| where amount_eur > 1000
```

**Your question:** add one `where` line (above `distinct`) so that only the 2 SIM-swap victims are left. Look at the columns of the 5 results: which value do only the 2 victims have?

<details><summary>Hint</summary>

Run the query without `distinct user_id` to see all columns. Compare `network`.
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
<details><summary>Think question: is "network == mobile" a good rule for a real SOC?</summary>

It works on this data, but an attacker on home internet or a VPN slips through. And many honest customers use their phone. A stronger rule combines signals: an SMS password reset and a 2FA change shortly before the new address. Write this down in the Blind spots section of the ATO-001 README. That's exactly the kind of thinking a SOC team wants to see.
</details>

### Exercise 12: save it in your repo
1. In File Explorer (Mac: Finder), go to the folder `detections/ATO-001-sim-swap-takeover`.
2. Make a new file called `detection.kql`. On Windows: right-click → **New** → **Text Document**, and rename it to `detection.kql` (say **Yes** when Windows warns about the file extension). On Mac: open TextEdit, choose **Format → Make Plain Text**, and save it as `detection.kql`.
3. Paste your tuned query from exercise 11 in it (without the practice table) and save.
4. In the README of ATO-001, set KQL to **done** in the Implementations table.

Your detection now exists in two languages. Next week: Splunk.
