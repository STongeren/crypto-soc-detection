# SPL cheat sheet (Splunk)

Keep this open next to Splunk. Copy an example and change only what you need. Time picker: **All time** for the course data.

**Read every search left to right:** first which data (`index=main sourcetype=csv` plus filters), then each `|` is one step.

## The building blocks

| I want to... | SPL | SQL | KQL |
|---|---|---|---|
| all events | `index=main sourcetype=csv` | `FROM events` | `Events` |
| count | `... \| stats count` | `COUNT(*)` | `\| count` |
| a few events | `... \| head 5` | `LIMIT 5` | `\| take 5` |
| only some fields | `... \| table _time user_id event_type` | column list | `\| project` |
| filter | `index=main sourcetype=csv event_type=login` | `WHERE` | `\| where` |
| two filters (both true) | `event_type=login result=failure` | `AND` | `and` |
| one of two | `(country=RU OR country=VN)` | `OR` | `or` |
| from a list | `event_type IN (login, deposit)` | `IN (...)` | `in (...)` |
| not | `NOT country=NL` | `!=` | `!=` |
| has a value / is empty | `ticket_id=*` / `NOT ticket_id=*` | `IS NOT NULL` / `IS NULL` | `isnotempty()` / `isempty()` |
| bigger than | `amount_eur>1000` | `>` | `>` |
| count per group | `\| stats count by country` | `GROUP BY` | `summarize count() by` |
| count different values | `\| stats dc(user_id)` | `COUNT(DISTINCT)` | `dcount()` |
| several results at once | `\| stats count AS logins dc(user_id) AS customers by ip` | two counts | two counts in `summarize` |
| all different values in a list | `\| stats values(country) by user_id` | `GROUP_CONCAT` | `make_set()` |
| smallest / biggest | `\| stats min(_time) max(amount_eur) by user_id` | `MIN` / `MAX` | `min()` / `max()` |
| threshold | `\| stats count by ip \| where count >= 50` | `HAVING` | `\| where` after `summarize` |
| sort, biggest first | `\| sort - count` | `ORDER BY ... DESC` | `\| sort by ... desc` |
| the most common values | `\| top limit=3 country` | `ORDER BY ... LIMIT 3` | `\| top 3 by` |
| new calculated field | `\| eval minutes = (b - a) / 60` | expression | `\| extend` |
| if this, then that | `\| eval size = if(amount_eur >= 1000, "big", "normal")` | `CASE` | `iff()` |
| count per time slot | `\| timechart span=1d count` | (no simple version) | `summarize count() by bin(...)` |
| the last 24 hours | `earliest=-24h` in the first line | (depends) | `ago(1d)` |
| use one search as a filter for another | `... [ search ... \| fields ip ]` | subquery | `join` / `in` |
| readable times | `\| convert ctime(added_time)` | | |

## Watch out

| SPL | Why |
|---|---|
| time picker | set it to **All time** for the course data, or every search gives 0 |
| values are not case-sensitive | `event_type=LOGIN` finds `login` |
| field names are case-sensitive | `Event_Type=login` finds nothing |
| `sort count` vs `sort - count` | small to big vs big to small |
| `_time` is in seconds | 60 minutes = `3600` |
| quotes | needed around values with spaces or special characters: `user_agent="python-requests/2.32"` |
| inside `eval` and `where` | text needs quotes: `if(event_type="login", ...)` |
| empty CSV fields | the field doesn't exist on that event: use `field=*` / `NOT field=*` |
| subsearch `[ ]` | runs first, and must end with `fields` of the field you filter on |

## When it doesn't work

| What you see | Probably |
|---|---|
| no results | time picker isn't on All time, or a typo in a field name (case!) |
| `Error in 'where' command` | text without quotes inside `where` or `eval` |
| `Unknown search command` | a typo after a `\|`, like `stat` instead of `stats` |
| numbers look huge | those are times in seconds: use `\| convert ctime(field)` |
