# Week 1: SQL

Open `data/exchange.db` in DB Browser for SQLite (tab "Execute SQL"). No database yet? Run `python data/generate_exchange_logs.py` first.

Keep your practice queries in `learning/week1.sql`. Your real detection goes in `detections/ATO-001-sim-swap-takeover/detection.sql`.

## Day 1: SELECT and WHERE
1. Show the first 10 rows of `events`.
2. Show only the events of user `U00005`.
3. Show all events where `event_type` is `password_reset`.

## Day 2: ORDER BY, COUNT, JOIN
4. Count how many events there are per `event_type`.
5. Show the 10 biggest withdrawals, biggest first.
6. Join `events` with `users` and show the user's name and `mfa_method` next to each withdrawal.

## Day 3: Look around like an analyst
7. Which users logged in from a country that is not their home country? (Compare `events.country` with `users.country`.)
8. Which `network` types exist, and how many logins came from each?

## Day 4: Your first detection
9. Find every user who withdrew to an address they added **less than 1 hour earlier**.

   Hint: join `events` with itself. One side is `withdrawal_address_added`, the other is `withdrawal`, matched on `user_id` and `address`. SQLite compares times with `julianday()`.

10. Put that query in `detections/ATO-001-sim-swap-takeover/detection.sql` (return the users as a column named `entity`) and run:

    ```
    python tests/run_detections.py
    ```

    It tells you how many attacks you caught, how many false alarms you raised and how many you missed.

11. You will probably get false alarms. Look at those users: what is different about a real SIM-swap takeover? Think about `auth_method`, `network`, `device_id` and the `mfa_changed` event. Improve the query until the false alarms are gone, and write each version down in the Validation table of the detection README.
