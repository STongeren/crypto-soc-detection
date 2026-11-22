# SQL cheat sheet

Keep this open next to DB Browser. You don't have to memorize anything: copy an example and change only what you need.

## Part 1: the building blocks

| I want to... | Write it like this | Watch out |
|---|---|---|
| see everything, but only a few rows | `SELECT * FROM events LIMIT 10;` | `*` = all columns |
| see only some columns | `SELECT timestamp, user_id, event_type FROM events;` | separate columns with a comma |
| one customer | `SELECT * FROM events WHERE user_id = 'U00005';` | text always goes between `' '` |
| two conditions at once | `... WHERE event_type = 'login' AND country = 'RU';` | `AND` = both must be true |
| one of two | `... WHERE country = 'RU' OR country = 'VN';` | `OR` = either one |
| from a list | `... WHERE country IN ('RU', 'VN', 'SG');` | shorter than many `OR`s |
| everything except | `... WHERE country != 'NL';` | `!=` = is not. Rows where the value is `NULL` are dropped too |
| bigger or smaller | `... WHERE amount_eur > 5000;` | numbers without `' '` |
| is empty | `... WHERE ticket_id IS NULL;` | not `= NULL`, that doesn't work |
| which values exist | `SELECT DISTINCT network FROM events;` | each value only once |
| count | `SELECT COUNT(*) FROM events WHERE event_type = 'login';` | gives one number |
| count different values | `SELECT COUNT(DISTINCT user_id) FROM events;` | each customer counts once |
| count per type | `SELECT event_type, COUNT(*) FROM events GROUP BY event_type;` | what's in `GROUP BY` also goes after `SELECT` |
| only groups above a threshold | `... GROUP BY country HAVING COUNT(*) > 2000;` | `WHERE` filters rows before grouping, `HAVING` filters groups after |
| sort, biggest first | `... ORDER BY amount_eur DESC;` | `ASC` = smallest first |
| top 5 | `... ORDER BY amount_eur DESC LIMIT 5;` | `ORDER BY` comes before `LIMIT` |
| add the customer's name | `SELECT e.timestamp, u.name FROM events e JOIN users u ON u.user_id = e.user_id;` | `e` and `u` are short names for the tables |
| keep rows without a match (find what's missing) | `... FROM users u LEFT JOIN events e ON e.user_id = u.user_id AND e.event_type = 'deposit' WHERE e.user_id IS NULL;` | conditions about the right table go in `ON`, not `WHERE` |
| label rows | `CASE WHEN amount_eur >= 1000 THEN 'big' ELSE 'normal' END AS size` | the first `WHEN` that is true wins |
| give a column a new name | `SELECT user_id AS entity FROM events;` | the test looks for a column called `entity` |
| minutes between two events | `(julianday(b.timestamp) - julianday(a.timestamp)) * 24 * 60` | `julianday` turns a date into a number of days |
| a range | `... BETWEEN 0 AND 60` | from 0 up to and including 60 |

**The order is always:** `SELECT` → `FROM` → `JOIN` → `WHERE` → `GROUP BY` → `HAVING` → `ORDER BY` → `LIMIT`

**Lines that start with `--`** are skipped by SQL. Use them for your own notes.

## Part 2: what's in the database

### Table `events` (one row = one thing someone did)

| Column | What it is | Possible values (number of rows). `NULL` = empty: find it with `IS NULL` |
|---|---|---|
| `event_type` | what happened | `login` (20219), `support_account_view` (6939), `withdrawal` (1171), `deposit` (969), `withdrawal_address_added` (86), `password_reset` (64), `mfa_changed` (2) |
| `result` | did it work | `success` (28464), `failure` (986) |
| `auth_method` | how the person proved who they are | `NULL` (9165), `password+sms` (8820), `password+totp` (8223), `password+passkey` (2186), `password` (990), `email` (62), `sms` (4) |
| `network` | type of internet connection | `residential` (22235), `corporate` (6939), `hosting` (263), `mobile` (13) |
| `actor` | who did it | `customer` (22511), `support_agent` (6939) |
| `asset` | which crypto | `NULL` (27310), `USDC` (552), `SOL` (545), `BTC` (531), `ETH` (512) |
| `country` | country of the IP address | `NL` (20740), `ES` (2378), `DE` (2321), `BE` (2012), `FR` (1723), `SG` (263), `VN` (5), `RU` (5), `TH` (3) |

**Columns without a fixed list:**
- `event_id`: unique number, like `E0000001`
- `timestamp`: time in UTC, like `2026-10-10T02:50:00Z`
- `user_id`: customer, like `U00005`
- `ip`, `device_id` (like `dev-123456`), `user_agent` (app or browser)
- `amount_eur`: amount in euro (for `deposit` and `withdrawal`)
- `address`: wallet address `0x...` (for `deposit`, `withdrawal`, `withdrawal_address_added`)
- `agent_id`: support agent, like `AG03` (only for `support_account_view`)
- `ticket_id`: like `T-123456`. Empty = no ticket.

### What do the values mean?
| Value | Meaning |
|---|---|
| `login` | logging in (look at `result`: `success` or `failure`) |
| `password_reset` | password was reset |
| `mfa_changed` | two-factor authentication was changed |
| `withdrawal_address_added` | new address added to send crypto to |
| `withdrawal` | crypto sent out of the exchange |
| `deposit` | crypto came in |
| `support_account_view` | a support agent opened a customer's account |
| `residential` / `mobile` / `hosting` / `corporate` | home internet / phone network / server in a data center / the exchange's office |

### Table `users` (one row = one customer)
| Column | Possible values |
|---|---|
| `country` | `NL` (610), `ES` (104), `DE` (101), `FR` (96), `BE` (89) |
| `mfa_method` | `sms` (457), `totp` (427), `passkey` (116) |

Other columns: `user_id`, `name`, `signup_date`, `balance_eur`, `home_device`.

## Part 3: when it doesn't work
| What you see | Probably |
|---|---|
| 0 results | a typo in a value. Check with `SELECT DISTINCT column FROM events;` |
| `no such column` | a typo in a column name. Look in the DB Schema panel |
| `syntax error` | a missing `'` or `,`, or the order is wrong (see the order above) |
| `ambiguous column name` | in a JOIN: put the table name in front, like `e.user_id` |
