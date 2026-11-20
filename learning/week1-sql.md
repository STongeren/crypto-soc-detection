# Week 1: SQL

**Zo werkt elke opdracht:**
1. Kopieer het **voorbeeld** in DB Browser (tabblad Execute SQL) en druk op Ctrl + Enter.
2. Verander alleen het ding dat bij **Jouw beurt** staat.
3. Check je uitkomst bij **Goed als**.

Houd [het spiekbriefje](cheatsheet.md) ernaast open. 3 opdrachten per dag, ongeveer 20 minuten.

---

## Dag 1: kijken

### Opdracht 1: de eerste regels
**Voorbeeld:**
```sql
SELECT * FROM events LIMIT 10;
```
**Jouw beurt:** laat er 5 zien in plaats van 10.
**Goed als:** je 5 regels ziet.

### Opdracht 2: één klant
**Voorbeeld:**
```sql
SELECT * FROM events WHERE user_id = 'U00005';
```
**Jouw beurt:** bekijk klant `U00918`.
**Goed als:** je 30 regels ziet. Kijk naar de kolom `country`: deze klant is ook gehackt. Zie je vanuit welk land?

### Opdracht 3: welke waarden bestaan er
**Voorbeeld:**
```sql
SELECT DISTINCT event_type FROM events;
```
**Jouw beurt:** doe hetzelfde voor de kolom `network`.
**Goed als:** je 4 waarden ziet: `residential`, `corporate`, `mobile`, `hosting`.

---

## Dag 2: filteren en tellen

### Opdracht 4: één soort event
**Voorbeeld:**
```sql
SELECT * FROM events WHERE event_type = 'password_reset';
```
**Jouw beurt:** zoek alle `mfa_changed` events.
**Goed als:** je 2 regels ziet. Herken je de klanten?

### Opdracht 5: twee voorwaarden
**Voorbeeld:**
```sql
SELECT * FROM events
WHERE event_type = 'password_reset' AND auth_method = 'sms';
```
**Jouw beurt:** verander `'sms'` in `'email'`.
**Goed als:** je 62 regels ziet. Gewone klanten resetten via e-mail, de aanvallers via sms. Dat verschil is een aanwijzing.

### Opdracht 6: tellen per soort
**Voorbeeld:**
```sql
SELECT event_type, COUNT(*) FROM events GROUP BY event_type;
```
**Jouw beurt:** tel per `country` in plaats van per `event_type`. Let op: verander het op allebei de plekken.
**Goed als:** `NL` het meeste voorkomt (20740) en je ook `SG`, `RU`, `VN` en `TH` ziet.

---

## Dag 3: sorteren en koppelen

### Opdracht 7: de grootste opnames
**Voorbeeld:**
```sql
SELECT timestamp, user_id, amount_eur, asset FROM events
WHERE event_type = 'withdrawal'
ORDER BY amount_eur DESC LIMIT 5;
```
**Jouw beurt:** laat alleen de grootste opnames in `'BTC'` zien. (Voeg `AND asset = 'BTC'` toe na de `WHERE`-regel.)
**Goed als:** bovenaan klant `U00227` staat met 7061.17.

### Opdracht 8: logins vanaf een server
**Voorbeeld:**
```sql
SELECT COUNT(*) FROM events
WHERE event_type = 'login' AND network = 'hosting';
```
**Jouw beurt:** tel de logins vanaf `'mobile'`.
**Goed als:** je 3 krijgt. Gewone mensen loggen thuis in. 261 logins vanaf een server in een datacenter is vreemd: dat is een script, geen mens.

### Opdracht 9: de naam erbij
**Voorbeeld:**
```sql
SELECT e.timestamp, e.event_type, e.amount_eur, u.name
FROM events e
JOIN users u ON u.user_id = e.user_id
WHERE e.user_id = 'U00005';
```
**Jouw beurt:** doe hetzelfde voor `U00918`.
**Goed als:** je de naam Sara de Wit ziet.

---

## Dag 4: je eerste detectie

### Opdracht 10: wanneer kwam het nieuwe adres?
**Voorbeeld:**
```sql
SELECT timestamp, event_type, address FROM events
WHERE user_id = 'U00005'
  AND event_type IN ('withdrawal_address_added', 'withdrawal');
```
**Jouw beurt:** kijk naar de tijden. Hoeveel minuten na het toevoegen van het adres ging het geld eruit?
**Goed als:** je 4 minuten vindt (02:50 → 02:54).

### Opdracht 11: het patroon bij alle klanten
Dit is een detectie: opnames naar een adres dat minder dan 60 minuten eerder is toegevoegd. Je hoeft hem niet zelf te bedenken: lees hem regel voor regel met het spiekbriefje ernaast.

**Voorbeeld:**
```sql
SELECT DISTINCT a.user_id AS entity
FROM events a                                   -- a = het toevoegen van het adres
JOIN events w                                   -- w = de opname
  ON w.user_id = a.user_id
 AND w.address = a.address
 AND w.event_type = 'withdrawal'
WHERE a.event_type = 'withdrawal_address_added'
  AND (julianday(w.timestamp) - julianday(a.timestamp)) * 24 * 60 BETWEEN 0 AND 60;
```
**Goed als:** je 5 klanten krijgt.

### Opdracht 12: laat de test het nakijken
1. Open `detections/ATO-001-sim-swap-takeover/detection.sql` in Kladblok.
2. Plak de query van opdracht 11 onder de regels met `--`, en sla op.
3. Open PowerShell en typ:
   ```
   cd D:\crypto-soc-detection
   python tests\run_detections.py
   ```
**Goed als:** bij ATO-001 staat: Caught 2, False alarms 3, Missed 0.

Je ving beide aanvallen, maar je gaf ook 3 valse meldingen. Die eruit krijgen is week 2. Wil je alvast kijken wat er anders is aan de 5 klanten? Draai dan dit:
```sql
SELECT user_id, timestamp, event_type, network, country, auth_method
FROM events
WHERE user_id IN ('U00005', 'U00918', 'U00226', 'U00287', 'U00669')
  AND event_type IN ('password_reset', 'mfa_changed', 'withdrawal_address_added');
```
Twee klanten hebben iets wat de andere drie niet hebben. Wat?
