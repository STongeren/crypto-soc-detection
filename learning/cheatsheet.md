# Spiekbriefje SQL

Zet dit naast DB Browser. Niets hoef je te onthouden: kopieer een voorbeeld en verander alleen wat **dik** staat.

## Deel 1: de bouwstenen

| Ik wil... | Zo schrijf je het | Let op |
|---|---|---|
| alles zien, maar maar een paar regels | `SELECT * FROM events LIMIT 10;` | `*` = alle kolommen |
| alleen bepaalde kolommen | `SELECT timestamp, user_id, event_type FROM events;` | kolommen scheiden met een komma |
| één klant | `SELECT * FROM events WHERE user_id = 'U00005';` | tekst altijd tussen `' '` |
| twee voorwaarden tegelijk | `... WHERE event_type = 'login' AND country = 'RU';` | `AND` = allebei waar |
| één van twee | `... WHERE country = 'RU' OR country = 'VN';` | `OR` = één van de twee |
| uit een lijstje | `... WHERE country IN ('RU', 'VN', 'SG');` | korter dan veel `OR` |
| alles behalve | `... WHERE country != 'NL';` | `!=` = is niet |
| groter of kleiner | `... WHERE amount_eur > 5000;` | getallen zonder `' '` |
| is leeg | `... WHERE ticket_id IS NULL;` | niet `= NULL`, dat werkt niet |
| welke waarden bestaan er | `SELECT DISTINCT network FROM events;` | elke waarde maar één keer |
| tellen | `SELECT COUNT(*) FROM events WHERE event_type = 'login';` | geeft één getal |
| tellen per soort | `SELECT event_type, COUNT(*) FROM events GROUP BY event_type;` | wat in `GROUP BY` staat, staat ook na `SELECT` |
| sorteren, grootste eerst | `... ORDER BY amount_eur DESC;` | `ASC` = kleinste eerst |
| top 5 | `... ORDER BY amount_eur DESC LIMIT 5;` | `ORDER BY` komt vóór `LIMIT` |
| naam van de klant erbij | `SELECT e.timestamp, u.name FROM events e JOIN users u ON u.user_id = e.user_id;` | `e` en `u` zijn korte namen voor de tabellen |
| tijd tussen twee events in minuten | `(julianday(b.timestamp) - julianday(a.timestamp)) * 24 * 60` | `julianday` rekent een datum om naar een getal |

**De volgorde is altijd:** `SELECT` → `FROM` → `JOIN` → `WHERE` → `GROUP BY` → `ORDER BY` → `LIMIT`

**Regels die beginnen met `--`** slaat SQL over. Gebruik ze voor je eigen notities.

## Deel 2: wat er in de database staat

### Tabel `events` (één regel = één ding dat iemand deed)

| Kolom | Wat het is | Mogelijke waarden (aantal regels) |
|---|---|---|
| `event_type` | wat er gebeurde | `login` (20219), `support_account_view` (6939), `withdrawal` (1171), `deposit` (969), `withdrawal_address_added` (86), `password_reset` (64), `mfa_changed` (2) |
| `result` | lukte het | `success` (28464), `failure` (986) |
| `auth_method` | hoe iemand bewees wie hij is | `(leeg)` (9165), `password+sms` (8821), `password+totp` (8223), `password+passkey` (2186), `password` (989), `email` (62), `sms` (4) |
| `network` | soort internetverbinding | `residential` (22235), `corporate` (6939), `hosting` (263), `mobile` (13) |
| `actor` | wie het deed | `customer` (22511), `support_agent` (6939) |
| `asset` | welke crypto | `(leeg)` (27310), `USDC` (552), `SOL` (545), `BTC` (531), `ETH` (512) |
| `country` | land van het IP-adres | `NL` (20740), `ES` (2378), `DE` (2321), `BE` (2012), `FR` (1723), `SG` (263), `VN` (5), `RU` (5), `TH` (3) |

**Kolommen zonder vaste lijst:**
- `event_id`: uniek nummer, zoals `E0000001`
- `timestamp`: tijd in UTC, zoals `2026-10-10T02:50:00Z`
- `user_id`: klant, zoals `U00005`
- `ip`, `device_id` (zoals `dev-123456`), `user_agent` (app of browser)
- `amount_eur`: bedrag in euro (bij `deposit` en `withdrawal`)
- `address`: wallet-adres `0x...` (bij `deposit`, `withdrawal`, `withdrawal_address_added`)
- `agent_id`: supportmedewerker, zoals `AG03` (alleen bij `support_account_view`)
- `ticket_id`: zoals `T-123456`. Leeg = geen ticket.

### Wat betekenen de waarden?
| Waarde | Betekenis |
|---|---|
| `login` | inloggen (kijk naar `result`: `success` of `failure`) |
| `password_reset` | wachtwoord opnieuw ingesteld |
| `mfa_changed` | tweestapsverificatie veranderd |
| `withdrawal_address_added` | nieuw adres toegevoegd om crypto naartoe te sturen |
| `withdrawal` | crypto de exchange uit gestuurd |
| `deposit` | crypto binnengekomen |
| `support_account_view` | een supportmedewerker opende het account van een klant |
| `residential` / `mobile` / `hosting` / `corporate` | thuis-internet / telefoonnetwerk / server in een datacenter / kantoor van de exchange |

### Tabel `users` (één regel = één klant)
| Kolom | Mogelijke waarden |
|---|---|
| `country` | `NL` (610), `ES` (104), `DE` (101), `FR` (96), `BE` (89) |
| `mfa_method` | `sms` (457), `totp` (427), `passkey` (116) |

Andere kolommen: `user_id`, `name`, `signup_date`, `balance_eur`, `home_device`.

## Deel 3: als het niet werkt
| Wat je ziet | Waarschijnlijk |
|---|---|
| 0 resultaten | spelfout in een waarde. Check met `SELECT DISTINCT kolom FROM events;` |
| `no such column` | spelfout in een kolomnaam. Kijk in het DB Schema-paneel |
| `syntax error` | een `'` of `,` vergeten, of de volgorde klopt niet (zie de volgorde hierboven) |
| `ambiguous column name` | bij een JOIN: zet de tabelnaam ervoor, zoals `e.user_id` |
