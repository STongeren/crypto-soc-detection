# KQL cheat sheet

Keep this open next to the query window. Copy an example and change only what you need.

**Read every query top to bottom:** start with a table, then each `|` line is one step.

## The building blocks

| I want to... | KQL | Same thing in SQL |
|---|---|---|
| count all rows | `Events \| count` | `SELECT COUNT(*) FROM events;` |
| see a few rows | `Events \| take 10` | `SELECT * FROM events LIMIT 10;` |
| see only some columns | `Events \| project timestamp, user_id` | `SELECT timestamp, user_id FROM events;` |
| filter | `Events \| where user_id == "U00005"` | `WHERE user_id = 'U00005'` |
| two conditions | `\| where event_type == "login" and country == "RU"` | `AND` |
| one of two | `\| where country == "RU" or country == "VN"` | `OR` |
| from a list | `\| where country in ("RU", "VN", "SG")` | `IN (...)` |
| everything except | `\| where country != "NL"` | `!=` |
| bigger or smaller | `\| where amount_eur > 5000` | same |
| which values exist | `Events \| distinct network` | `SELECT DISTINCT network ...` |
| count different values | `Events \| distinct user_id \| count` | `COUNT(DISTINCT user_id)` |
| count per group | `Events \| summarize Total = count() by network` | `GROUP BY network` |
| sort, biggest first | `\| sort by Total desc` | `ORDER BY Total DESC` |
| top 5 | `\| top 5 by amount_eur` | `ORDER BY amount_eur DESC LIMIT 5` |
| new calculated column | `\| project Duration = EndTime - StartTime` | `julianday(...)` math |
| give a table a name | `let Added = Events \| where ...;` | (no simple SQL version) |
| stick two tables together | `\| join kind=inner Added on user_id, address` | `JOIN ... ON ...` |
| a time window | `\| where timestamp between (t1 .. t1 + 60m)` | `BETWEEN` |

## Watch out

| KQL | Why |
|---|---|
| `==` to compare | one `=` gives an error (one `=` is for naming a column) |
| `"text"` or `'text'` | both kinds of quotes work |
| `60m`, `2h`, `1d` | minutes, hours, days |
| `between (a .. b)` | two dots, and brackets around it |
| `desc` / `asc` | biggest first / smallest first |
| upper and lower case matter | `Events` works, `events` doesn't |

## The practice environment

- **Run a query:** Shift + Enter, or the **Run** button.
- **An empty line ends a query.** Keep one query together, without empty lines.
- **Durations** look like `1.01:30:00` = 1 day, 1 hour, 30 minutes.
- **Times** look like `2026-10-10T02:54:00Z`: date, `T`, time. `Z` = UTC.

## When it doesn't work

| What you see | Probably |
|---|---|
| `Failed to resolve table or column` | a typo, or wrong upper/lower case |
| `Syntax error` | a missing `\|`, quote, bracket or `;` after a `let` |
| 0 results | the value is spelled differently. Check with `distinct` |
| only part of your query ran | there's an empty line in it |
