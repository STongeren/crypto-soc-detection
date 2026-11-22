# KQL cheat sheet

Keep this open next to the query window. Copy an example and change only what you need.

**Read every query top to bottom:** start with a table, then each `|` line is one step that works on the result of the step before.

## The building blocks

| I want to... | KQL | Same thing in SQL |
|---|---|---|
| count all rows | `Events \| count` | `SELECT COUNT(*) FROM events;` |
| see a few rows (any rows, for a quick look) | `Events \| take 10` | `SELECT * FROM events LIMIT 10;` |
| see only some columns | `Events \| project timestamp, user_id` | `SELECT timestamp, user_id FROM events;` |
| add a calculated column, keep the rest | `\| extend Duration = EndTime - StartTime` | `julianday(...)` math |
| filter | `Events \| where user_id == "U00005"` | `WHERE user_id = 'U00005'` |
| filter, ignoring upper/lower case | `\| where State =~ "texas"` | (depends on the database) |
| two conditions | `\| where event_type == "login" and country == "RU"` | `AND` |
| one of two | `\| where country == "RU" or country == "VN"` | `OR` |
| from a list | `\| where country in ("RU", "VN", "SG")` | `IN (...)` |
| everything except | `\| where country != "NL"` | `!=` |
| bigger or smaller | `\| where amount_eur > 5000` | same |
| text starts with | `\| where address startswith "0x2e2e"` | `LIKE '0x2e2e%'` |
| text contains a whole word | `\| where user_agent has "python"` | `LIKE '%python%'` |
| empty text | `\| where isempty(auth_method)` | `IS NULL` |
| the last day / hour | `\| where timestamp > ago(1d)` | (depends on the database) |
| which values exist | `Events \| distinct network` | `SELECT DISTINCT network ...` |
| count per group | `Events \| summarize Total = count() by network` | `GROUP BY network` |
| count different values | `\| summarize Customers = dcount(user_id)` | `COUNT(DISTINCT user_id)` |
| several counts at once | `\| summarize Total = count(), Customers = dcount(user_id) by network` | two counts in `SELECT` |
| count per time slot | `\| summarize count() by bin(timestamp, 1h)` | (no simple SQL version) |
| a threshold ("more than N") | `\| summarize Total = count() by user_id \| where Total > 5` | `HAVING COUNT(*) > 5` |
| count only some rows | `\| summarize Failed = countif(result == "failure") by user_id` | `SUM(CASE WHEN ... THEN 1 ELSE 0 END)` |
| all different values in a list | `\| summarize Countries = make_set(country) by user_id` | `GROUP_CONCAT(DISTINCT country)` |
| the latest row per group | `\| summarize arg_max(timestamp, *) by user_id` | (needs a window function in SQL) |
| a field inside JSON | `\| extend City = tostring(LocationDetails.city)` | (depends on the database) |
| rows with no match | `\| join kind=leftanti (Other) on user_id` | `LEFT JOIN ... WHERE ... IS NULL` |
| sort, biggest first | `\| sort by Total desc` | `ORDER BY Total DESC` |
| top 5 | `\| top 5 by amount_eur` | `ORDER BY amount_eur DESC LIMIT 5` |
| draw a line chart | `\| render timechart` | (not in SQL) |
| give a table a name | `let Added = Events \| where ...;` | (no simple SQL version) |
| stick two tables together | `\| join kind=inner Added on user_id, address` | `JOIN ... ON ...` |
| a time window | `\| where timestamp between (t1 .. t1 + 60m)` | `BETWEEN` |

## Watch out

| KQL | Why |
|---|---|
| `==` to compare | one `=` gives a "Semantic Error". (One `=` is only for naming a column, like `Total = count()`.) |
| `==` is case-sensitive | `"texas"` finds nothing when the data says `"TEXAS"`. Use `=~` to ignore case. Rules prefer `==`: faster and exact |
| `"text"` or `'text'` | both kinds of quotes work |
| `60m`, `2h`, `1d` | minutes, hours, days |
| `between (a .. b)` | two dots, brackets around it, both ends included |
| `sort by` / `top` without `asc` or `desc` | biggest first: the **opposite** of SQL |
| `\| count` vs `count()` | `\| count` counts the whole table. `count()` goes inside `summarize` |
| `extend` vs `project` | `extend` adds a column and keeps the rest. `project` keeps only what you name |
| always write `join kind=` | without it KQL uses `innerunique`, which can silently drop matches |
| after a join | columns that exist on both sides get a `1` added (`user_id1`) |
| `take` | gives any rows, not random and not in order. Never use it for an answer |
| `dcount()` | very close but approximate on huge tables. Use `count_distinct()` when it must be exact |
| upper and lower case in names | `Events` works, `events` doesn't |

## The practice environment

- **Run a query:** Shift + Enter, or the **Run** button.
- **An empty line ends a query.** Keep one query together, without empty lines.
- **Durations** look like `1.01:30:00` = 1 day, 1 hour, 30 minutes.
- **Times** look like `2026-10-10T02:54:00Z`: date, `T`, time. `Z` = UTC.
- **In a real SIEM** (Sentinel) the time column is called `TimeGenerated`, and almost every query starts with `| where TimeGenerated > ago(...)`.

## When it doesn't work

| What you see | Probably |
|---|---|
| `Failed to resolve table or column` | a typo, or wrong upper/lower case |
| `Syntax error` / `Semantic error` | one `=` instead of `==`, or a missing `\|`, quote, bracket or `;` after a `let` |
| 0 results | the value is spelled differently (or different case). Check with `distinct` |
| only part of your query ran | there's an empty line in it |
