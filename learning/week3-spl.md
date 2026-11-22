# Week 3: Splunk (SPL)

Splunk is one of the most used SIEMs in the world, and every crypto SOC posting asks for SIEM skills. Its language is SPL (Search Processing Language). Like KQL, it reads left to right through pipes: start with the data, then each `|` is one step.

This week you load **your own exchange data** into Splunk and do the same investigations as in weeks 1 and 2. By the end, ATO-001, CS-001 and INS-001 exist in SPL too.

Same rules as before: example first, then your question, hints and answers hidden, predict before you look. Keep the [SPL cheat sheet](cheatsheet-spl.md) open. Every search below was tested in Splunk on the course data.

---

## Before you start (30 minutes, once)

### Install Splunk
1. Go to [splunk.com/en_us/download/splunk-enterprise.html](https://www.splunk.com/en_us/download/splunk-enterprise.html). Make a free Splunk account when it asks.
2. Download the version for your computer:
   - **Windows:** the `.msi` file. Double-click it, tick the license box, and click **Customize Options** if you want to install it somewhere else (for example on your D: drive). Choose a username and password for Splunk and **write them down**. Click through until it's done.
   - **Mac:** the `.dmg` file. Open it and follow the installer. It asks for a username and password: **write them down**.
3. Open your browser at **http://localhost:8000** and log in with that username and password.

You get a 60-day trial. After that you can switch to the free license that never expires: **Settings → Licensing → Change license group → Free license**. Everything in this week works with the free license, **except exercise 10** (alerts): do that one during the trial.

### Load your exchange data
1. In Splunk, click **Settings** (top right) → **Add Data** → **Upload**.
2. Click **Select File** and pick `data/events.csv` from the repo. (No file? Download [exchange-dataset.zip](https://github.com/STongeren/crypto-soc-detection/releases/latest/download/exchange-dataset.zip) and unzip it into `data`.)
3. Click **Next**. On "Set Source Type", choose **csv** if it isn't chosen already. In the preview, check that the **_time** column shows dates in October and November 2026. Click **Next**.
4. On "Input Settings", leave **Index** on **Default** (that's `main`). Click **Review**, then **Submit**.
5. Click **Start Searching**.

### How to search
- Click **Search** in the menu on the left (or open the **Search & Reporting** app). The first time, Splunk offers a tour: click **Skip**.
- The search box is at the top. Type a search and press **Enter**.
- Next to the search box, the language should say **SPL** (newer versions also offer SPL2). This course uses SPL.
- **Important:** next to the search box is the **time picker**. Set it to **All time**. The data is from October and November 2026, so "Last 24 hours" shows nothing.
- Results appear below. The **Statistics** tab shows tables, the **Events** tab shows raw events.
- Splunk shows times in **your own time zone**. The data is in UTC, so in the Netherlands you see times 1 or 2 hours later than in the CSV. That's normal.

---

## Day 1: SQL and KQL to SPL

### Exercise 1: count and look
**Example:**
```spl
index=main sourcetype=csv
| stats count
```
- `index=main sourcetype=csv` = all events from your upload (like `FROM events`).
- `|` = then, just like in KQL.
- `stats count` = count them.

You get 29450.

Now look at a few events and only some fields:
```spl
index=main sourcetype=csv
| head 5
| table _time user_id event_type
```
- `head 5` = the first 5 results (like `take 5` / `LIMIT 5`). Splunk shows the newest first.
- `table` = only these fields, as a table (like `project`). In SPL you separate fields with spaces. Commas also work.
- `_time` is Splunk's own time field. It made it from your `timestamp` column.

**Your question:** show 10 events with only `_time`, `user_id`, `country` and `network`.

<details><summary>Answer</summary>

```spl
index=main sourcetype=csv
| head 10
| table _time user_id country network
```
</details>

### Exercise 2: filter
**Example:**
```spl
index=main sourcetype=csv event_type=password_reset auth_method=sms
| table _time user_id country
```
- In SPL you filter right in the first line: `field=value`.
- Two filters next to each other mean **both** must be true (an invisible `AND`).
- Quotes around the value are only needed when it has spaces or special characters.

You get the two SIM-swap resets: `U00918` from `VN` and `U00005` from `RU` (newest first).

Now count all password resets:
```spl
index=main sourcetype=csv event_type=password_reset
| stats count
```
64.

**Predict first:** KQL's `==` is case-sensitive. What do you get with `event_type=PASSWORD_RESET`?

<details><summary>Answer</summary>

The same 64 resets as with `password_reset`. In SPL, **values** in the search are not case-sensitive. Field **names** are: `Event_Type=password_reset` finds nothing.
</details>

**Your question:** count the password resets that went through `email`.

<details><summary>Hint</summary>

Put the filters in the first line, then `| stats count`.
</details>
<details><summary>Answer</summary>

```spl
index=main sourcetype=csv event_type=password_reset auth_method=email
| stats count
```
62.
</details>

### Exercise 3: which values exist, and how often
**Example:**
```spl
index=main sourcetype=csv
| stats count by event_type
```
`stats count by event_type` = one row per value, with how often it appears. Like `GROUP BY` and `summarize count() by`.

**Your question:** count per `network`, biggest first.

**New: sorting.** `| sort - count` sorts the `count` column biggest first. The `-` means descending. Without it, smallest first.

<details><summary>Answer</summary>

```spl
index=main sourcetype=csv
| stats count by network
| sort - count
```
`residential` 22235, `corporate` 6939, `hosting` 263, `mobile` 13.
</details>
<details><summary>Think question: one more SPL shortcut</summary>

`| top network` does the same in one step, and also adds a percentage column. Try it.
</details>

---

## Day 2: thresholds, distinct counts and time

**Warm-up (from memory, in DB Browser):** write the SQL that shows the countries with more than 2000 events.
<details><summary>Answer</summary>

```sql
SELECT country, COUNT(*) FROM events GROUP BY country HAVING COUNT(*) > 2000;
```
</details>

### Exercise 4: a threshold
In SPL a threshold is a `where` after the `stats`, just like in KQL:
```spl
index=main sourcetype=csv
| stats count by country
| where count > 2000
```
You get `BE`, `DE`, `ES` and `NL`.

**Your question:** which event types happen more than 1000 times?

<details><summary>Answer</summary>

```spl
index=main sourcetype=csv
| stats count by event_type
| where count > 1000
```
`login`, `support_account_view` and `withdrawal`.
</details>

### Exercise 5: counting different values
**New: `dc()`** means distinct count: how many **different** values. Like `COUNT(DISTINCT ...)` and `dcount()`.
```spl
index=main sourcetype=csv event_type=login network=hosting
| stats count dc(user_id)
```
You get `count` 261 and `dc(user_id)` 260: 261 logins from servers, against 260 different customers.

**New: naming a result.** `AS` gives a column a clearer name: `stats count AS logins dc(user_id) AS customers`.

**Your question:** per `ip`, count the failed logins (`result=failure`) and the different customers. Show the IPs with 50 or more failures.

<details><summary>Hint</summary>

Filter `event_type=login result=failure`, then `stats count AS failures dc(user_id) AS customers by ip`, then a `where`.
</details>
<details><summary>Answer</summary>

```spl
index=main sourcetype=csv event_type=login result=failure
| stats count AS failures dc(user_id) AS customers by ip
| where failures >= 50
```
One IP: 257 failures on 257 different customers. That's credential stuffing: one source, many accounts.
</details>

### Exercise 6: time
In Splunk, time works through `_time` and the time picker. Two tools you'll use all the time:

**Per time slot:** `timechart` counts per period and draws it:
```spl
index=main sourcetype=csv event_type=withdrawal
| timechart span=1w count
```
`span=1w` = one point per week. Click the **Visualization** tab to see the chart.

**Relative time in the search itself:** `earliest=-24h` means "from 24 hours ago". It overrides the time picker.
```spl
index=main sourcetype=csv earliest=-24h
| stats count
```
**Predict first:** what do you get?

<details><summary>Answer</summary>

0. The data is from October and November 2026, not from the last 24 hours. In a real SOC, almost every search has a short time range: that's what keeps searches fast.
</details>

**Your question:** count the **failed** logins per day (`span=1d`) and find the day with the most.

<details><summary>Hint</summary>

Filter `event_type=login result=failure`, then `timechart span=1d count`, then sort or look at the chart.
</details>
<details><summary>Answer</summary>

```spl
index=main sourcetype=csv event_type=login result=failure
| timechart span=1d count
| sort - count
```
The top day is the credential-stuffing day: October 21, 2026, with about 275 failed logins. No other day has more than about 26. (Your numbers can differ by a few: Splunk cuts days in your own time zone.)
</details>

---

## Day 3: your detections in SPL

**Warm-up (from memory, in the KQL practice environment):** write the KQL that counts the events per `network` and shows the number of different customers too.
<details><summary>Answer</summary>

```kql
Events
| summarize Total = count(), Customers = dcount(user_id) by network
```
</details>

### Exercise 7: INS-001 (missing values)
**New: empty fields.** In SPL, a field that is empty in the CSV doesn't exist on that event. `ticket_id=*` means "has a ticket". `NOT ticket_id=*` means "has no ticket".

**Example:**
```spl
index=main sourcetype=csv event_type=support_account_view NOT ticket_id=*
| stats count
```
180.

**Your question:** which agent opened accounts without a ticket, and how often?

<details><summary>Answer</summary>

```spl
index=main sourcetype=csv event_type=support_account_view NOT ticket_id=*
| stats count by agent_id
```
`AG07`, 180 times. That's INS-001 in SPL.
</details>

### Exercise 8: CS-001 (a search inside a search)
**New: a subsearch.** A search between `[ ]` runs **first**, and its result becomes a filter for the outer search:
```spl
index=main sourcetype=csv event_type=login result=success
    [ search index=main sourcetype=csv event_type=login result=failure
      | stats count by ip
      | where count >= 50
      | fields ip ]
| stats count by user_id
```
- The part in `[ ]` finds the IPs with 50 or more failures, and `fields ip` hands only the IP back.
- The outer search then only keeps successful logins **from those IPs**.

**Predict first:** how many customers does it find?

<details><summary>Answer</summary>

3: `U00226`, `U00242` and `U00780`, the accounts that were taken over. `U00226` has 2 successful logins: the stuffing one, and the attacker coming back a day later to empty the account.
</details>

**Your question:** change it so it also shows the `country` of those successful logins.

<details><summary>Answer</summary>

Change the last line to `| stats count by user_id country`. All three are `SG`: the server is in Singapore.
</details>

### Exercise 9: ATO-001 (one row per customer)
SQL and KQL used joins for ATO-001. In SPL you often do it differently: you collapse each customer's events into **one row** with `stats`, and then compare the times in that row.

**New:**
- `event_type IN (a, b, c)` = `event_type` is one of these, like `IN` in SQL.
- `eval` makes a new field, like `extend` in KQL.
- `if(condition, a, b)` gives `a` when the condition is true, otherwise `b`. `null()` means empty.
- `min(...)` and `max(...)` inside `stats` take the smallest or biggest value per group. Empty values are skipped.
- Times in `_time` are seconds, so 60 minutes = `3600`.

**Example:**
```spl
index=main sourcetype=csv event_type IN (password_reset, withdrawal_address_added, withdrawal)
| eval reset_sms = if(event_type="password_reset" AND auth_method="sms", _time, null())
| eval added = if(event_type="withdrawal_address_added", _time, null())
| eval withdrawn = if(event_type="withdrawal", _time, null())
| stats min(reset_sms) AS reset_time min(added) AS added_time max(withdrawn) AS last_withdrawal by user_id
| where added_time - reset_time >= 0 AND added_time - reset_time <= 3600
| table user_id reset_time added_time last_withdrawal
```

**Reading questions** (answer them yourself first):
1. What does each `eval` line put in its new field, and when is it empty?
2. After `stats`, how many rows are there per customer?
3. What does the `where` check?

<details><summary>Answers</summary>

1. The time of that kind of event, or empty for every other event. So `reset_sms` is only filled on SMS password resets.
2. One. `stats ... by user_id` collapses all their events into one row.
3. That the new address came 0 to 60 minutes after the SMS reset.
</details>

**Predict first:** which customers are left?

<details><summary>Answer</summary>

`U00005` and `U00918`. The times show up as big numbers: seconds since 1970. Add `| convert ctime(reset_time) ctime(added_time) ctime(last_withdrawal)` at the end to make them readable.
</details>

**Your question:** add the second half of the rule: the last withdrawal came 0 to 60 minutes after the new address.

<details><summary>Hint</summary>

Add `AND last_withdrawal - added_time >= 0 AND last_withdrawal - added_time <= 3600` to the `where` line.
</details>
<details><summary>Answer</summary>

```spl
index=main sourcetype=csv event_type IN (password_reset, withdrawal_address_added, withdrawal)
| eval reset_sms = if(event_type="password_reset" AND auth_method="sms", _time, null())
| eval added = if(event_type="withdrawal_address_added", _time, null())
| eval withdrawn = if(event_type="withdrawal", _time, null())
| stats min(reset_sms) AS reset_time min(added) AS added_time max(withdrawn) AS last_withdrawal by user_id
| where added_time - reset_time >= 0 AND added_time - reset_time <= 3600
    AND last_withdrawal - added_time >= 0 AND last_withdrawal - added_time <= 3600
| table user_id
```
Still `U00005` and `U00918`.
</details>
<details><summary>Think question: what's the weak spot of this approach?</summary>

`min` and `max` look at the first new address and the last withdrawal of the whole period. A customer who added an address in October and was robbed in November would be missed or mixed up. On this data it works, but in production you'd add a time window to the search (for example the last few hours), so each search only sees one attack. Write this down as a blind spot in the ATO-001 README.
</details>

---

## Day 4: make it an alert, save it in your repo

**Warm-up (from memory, in Python):** write the three lines that count the events per `event_type` with `Counter`.
<details><summary>Answer</summary>

```python
from collections import Counter
counts = Counter(e["event_type"] for e in events)
print(counts.most_common())
```
</details>

### Exercise 10: save a search as an alert
In a real SOC, a detection runs by itself on a schedule and creates an alert. In Splunk:

1. Run your INS-001 search from exercise 7.
2. Click **Save As → Alert** (top right, above the search box).
3. Title: `INS-001 support agent without ticket`.
4. Alert type: **Scheduled** → **Run on Cron Schedule**.
   - **Time Range:** All time (your data is old; a real alert would look at the last hour).
   - **Cron Expression:** `*/5 * * * *` (= every 5 minutes).
5. Trigger condition: **Number of Results**, **is greater than** `0`.
6. Trigger action: **Add** → **Add to Triggered Alerts**. Click **Save**.

After 5 minutes, open the alert under **Alerts** (menu on the left, or **Activity → Triggered Alerts** in older versions) and you see it fired. Then **disable** it (Alerts → Edit → Disable), so it doesn't keep running. The exact wording can differ a little between Splunk versions. (Because your data is old, set the alert's time range to **All time** if you want to see it fire. A real alert would look at the last hour.)

### Exercise 11: save your SPL in the repo
1. In each detection folder (`ATO-001...`, `CS-001...`, `INS-001...`), make a file `detection.spl`. Same way as `detection.kql` in week 2: VS Code → New File, or Notepad with "Save as type: All files", or TextEdit with **Format → Make Plain Text**.
2. Paste your final search from exercises 7, 8 and 9 in the matching folder.
3. Set SPL to **done** in the Implementations table of each README.

You now have three detections in three SIEM languages.

---

## Day 5: on your own

No examples, no hints. Only the [SPL cheat sheet](cheatsheet-spl.md).

### Exercise 12: big withdrawals
**Your question:** per country, how many withdrawals above 1000 euro? Biggest first.

<details><summary>Answer</summary>

```spl
index=main sourcetype=csv event_type=withdrawal amount_eur>1000
| stats count by country
| sort - count
```
`NL` 102, `DE` 31, `ES` 16, `FR` 14, `BE` 8, `RU` 1, `VN` 1. The same as week 1, exercise 13 (`RU` and `VN` both have 1, so they can swap places).
</details>

### Exercise 13: everything one customer did
**Your question:** for each customer with a login from `network=hosting`, list all the different countries and networks of **their own** events (`actor=customer`: support-agent events carry the office's country). How many customers used more than one country?

<details><summary>Answer</summary>

```spl
index=main sourcetype=csv actor=customer
    [ search index=main sourcetype=csv event_type=login network=hosting | stats count by user_id | fields user_id ]
| stats values(country) AS countries values(network) AS networks dc(country) AS n_countries by user_id
| where n_countries > 1
```
`values()` lists the different values, like `make_set()` in KQL. All 260 show up, each with their own country plus `SG`, because the stuffing server tried every one of them. A second country alone means nothing here: that's why CS-001 looks at **successful** logins only.
</details>

### Exercise 14: week 3 quiz
Predict first, then check in Splunk.

1. `index=main sourcetype=csv event_type=LOGIN | stats count`
2. `index=main sourcetype=csv | stats count by network | sort count`: is the first row the biggest or the smallest?
3. What does `NOT ticket_id=*` find?
4. Your time picker says "Last 24 hours" and every search gives 0. Why?

<details><summary>Answers</summary>

1. **20219**, the same as `login`. Values are not case-sensitive in SPL.
2. **The smallest** (`mobile`, 13). `sort count` sorts small to big, `sort - count` big to small.
3. Events where `ticket_id` is empty.
4. The data is from 2026-10 and 2026-11. Set the time picker to **All time**.
</details>

You can now say honestly: "I can search, filter, count, set thresholds, use subsearches and build scheduled alerts in Splunk, and I have three detections in SQL, KQL and SPL."

---

## Day 6 (extra): a real attack dataset

Optional, and big (about 320 MB). Splunk's own **Boss of the SOC v3** is a full attack on a fictional brewery, with Windows, cloud and network logs, used in Splunk's competitions.

1. On [github.com/splunk/botsv3](https://github.com/splunk/botsv3), download `botsv3_data_set.tgz` (the link is in its README).
2. Unpack it:
   - **Windows:** in PowerShell, go to your Downloads folder (`cd $HOME\Downloads`) and run `tar -xzf botsv3_data_set.tgz`.
   - **Mac:** double-click the file in Downloads.
3. Move the folder `botsv3_data_set` into Splunk's apps folder:
   - **Windows:** `C:\Program Files\Splunk\etc\apps\` (or the folder you chose when installing, plus `\etc\apps\`).
   - **Mac:** `/Applications/Splunk/etc/apps/`.
4. In Splunk: **Settings → Server controls → Restart Splunk**. Log in again when it's back.
5. Search `index=botsv3 | stats count by sourcetype` (time picker: **All time**) to see what's inside.
6. Pick one sourcetype and use what you learned this week to find something odd.

There are no answers here: this is real investigating.
