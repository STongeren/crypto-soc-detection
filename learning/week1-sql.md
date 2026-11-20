# Week 1: SQL

**Zo werkt elke opdracht:**
1. **Voorbeeld:** plak het in DB Browser (tabblad **Execute SQL**), druk op **Ctrl + Enter** en lees wat elk stukje doet.
2. **Jouw vraag:** schrijf zelf de query. Gebruik [het spiekbriefje](cheatsheet.md), dat is geen valsspelen.
3. Kom je er niet uit? Klik op **Hint**. Pas als je zelf een antwoord hebt, klik je op **Antwoord** om te checken.
4. **Denkvraag:** dit is wat een SOC-analist zich afvraagt. Denk eerst zelf na, klik dan pas.

Bij sommige vragen moet je eerst **voorspellen**. Gok gewoon. Een gok die fout blijkt, onthoud je beter dan een antwoord dat je alleen leest.

3 opdrachten per dag, ongeveer 20 minuten.

---

## Dag 1: kijken

### Opdracht 1: de eerste regels
**Voorbeeld:**
```sql
SELECT * FROM events LIMIT 10;
```
`*` betekent alle kolommen. `LIMIT 10` betekent: alleen de eerste 10 regels.

Wil je niet alle kolommen? Schrijf dan de namen in plaats van `*`, met een komma ertussen:
```sql
SELECT user_id, country FROM events LIMIT 10;
```

**Jouw vraag:** laat alleen de kolommen `timestamp`, `user_id` en `event_type` zien, en maar 5 regels.

<details><summary>Hint</summary>

Vervang `*` door de namen van de kolommen, met een komma ertussen.
</details>
<details><summary>Antwoord</summary>

```sql
SELECT timestamp, user_id, event_type FROM events LIMIT 5;
```
</details>

### Opdracht 2: het tweede slachtoffer
**Voorbeeld:**
```sql
SELECT * FROM events WHERE user_id = 'U00005';
```
`WHERE` is een filter: je ziet alleen de regels van deze klant.

In het voorbeeld zie je klant `U00005`. Hij woont in België (`BE`), maar er staan ook regels uit Rusland (`RU`) in: daar kwam de aanval vandaan.

**Jouw vraag:** klant `U00918` is ook gehackt. Laat alleen de kolom `country` van deze klant zien. Uit welk vreemd land kwam de aanval?

<details><summary>Hint</summary>

Combineer opdracht 1 en het voorbeeld: kies de kolom `country` na `SELECT`, en verander de `user_id`.
</details>
<details><summary>Antwoord</summary>

```sql
SELECT country FROM events WHERE user_id = 'U00918';
```
Je ziet vooral `NL`: daar woont ze. Daartussen staat een paar keer `VN`, Vietnam. Daar kwam de aanval vandaan.
</details>

### Opdracht 3: welke netwerken bestaan er
**Voorbeeld:**
```sql
SELECT DISTINCT event_type FROM events;
```
`DISTINCT` laat elke waarde maar één keer zien. Zo zie je wat er in een kolom kan staan.

**Voorspel eerst:** hoeveel soorten netwerk zijn er, denk je?
**Jouw vraag:** welke soorten `network` zitten er in de data?

<details><summary>Antwoord</summary>

```sql
SELECT DISTINCT network FROM events;
```
4: `residential` (thuis), `corporate` (kantoor van de exchange), `mobile` (telefoon) en `hosting` (een server in een datacenter).
</details>
<details><summary>Denkvraag: welke van de vier zou jij als klant nooit gebruiken om in te loggen?</summary>

`hosting`. Een gewoon mens logt niet in vanaf een server in een datacenter. Een script dat duizenden wachtwoorden probeert wel.
</details>

---

## Dag 2: filteren en tellen

### Opdracht 4: 2FA veranderd
**Voorbeeld:**
```sql
SELECT * FROM events WHERE event_type = 'password_reset';
```

**Jouw vraag:** hoe vaak werd de tweestapsverificatie (2FA) veranderd? Zoek in het spiekbriefje hoe dat event heet.

<details><summary>Hint</summary>

Kijk in deel 2 van het spiekbriefje, bij `event_type`.
</details>
<details><summary>Antwoord</summary>

```sql
SELECT * FROM events WHERE event_type = 'mfa_changed';
```
2 keer, bij `U00005` en `U00918`: de twee slachtoffers.
</details>

### Opdracht 5: e-mail of sms
**Voorbeeld:**
```sql
SELECT * FROM events
WHERE event_type = 'password_reset' AND auth_method = 'sms';
```
`AND` betekent: allebei moet waar zijn.

**Nieuw: tellen.** Wil je niet alle regels zien, maar alleen hoeveel het er zijn? Zet dan `COUNT(*)` in plaats van `*`:
```sql
SELECT COUNT(*) FROM events
WHERE event_type = 'password_reset' AND auth_method = 'sms';
```
Je krijgt één getal: 2.

**Voorspel eerst:** gaan er meer resets via e-mail of via sms?
**Jouw vraag:** tel hoeveel resets via e-mail gingen.

<details><summary>Hint</summary>

Neem de query met `COUNT(*)` en verander alleen `'sms'` in `'email'`.
</details>
<details><summary>Antwoord</summary>

```sql
SELECT COUNT(*) FROM events
WHERE event_type = 'password_reset' AND auth_method = 'email';
```
62. Via sms waren het er maar 2.
</details>
<details><summary>Denkvraag: wat zegt dat verschil je?</summary>

Gewone klanten resetten via e-mail. De twee resets via sms waren allebei de aanvallers. Een reset via sms is dus een sterk signaal, zeker in combinatie met een ander land.
</details>

### Opdracht 6: landen
**Voorbeeld:**
```sql
SELECT event_type, COUNT(*) FROM events GROUP BY event_type;
```
`GROUP BY` maakt groepjes. `COUNT(*)` telt hoeveel regels in elk groepje zitten.

**Jouw vraag:** uit welke landen komen de events, en hoe vaak? Welke landen zijn vreemd voor een Nederlandse exchange?

<details><summary>Hint</summary>

Vervang `event_type` door `country`, op allebei de plekken.
</details>
<details><summary>Antwoord</summary>

```sql
SELECT country, COUNT(*) FROM events GROUP BY country;
```
`NL` komt het vaakst voor (20740). Vreemd zijn `SG`, `RU`, `VN` en `TH`.
</details>
<details><summary>Denkvraag: is elk vreemd land een aanval?</summary>

Nee. `TH` is een klant op vakantie in Thailand. Een detectie die alleen op "ander land" let, geeft valse meldingen. Daarom combineer je signalen.
</details>

---

## Dag 3: sorteren en koppelen

### Opdracht 7: de grootste opname in bitcoin
**Voorbeeld:**
```sql
SELECT timestamp, user_id, amount_eur, asset FROM events
WHERE event_type = 'withdrawal'
ORDER BY amount_eur DESC LIMIT 5;
```
`ORDER BY ... DESC` sorteert van groot naar klein.

**Jouw vraag:** wat is de grootste opname in BTC, en van welke klant?

<details><summary>Hint</summary>

Voeg een tweede voorwaarde toe aan de `WHERE`, met `AND`.
</details>
<details><summary>Antwoord</summary>

```sql
SELECT timestamp, user_id, amount_eur, asset FROM events
WHERE event_type = 'withdrawal' AND asset = 'BTC'
ORDER BY amount_eur DESC LIMIT 5;
```
Klant `U00227`, 7061.17 euro.
</details>

### Opdracht 8: logins vanaf servers
**Voorbeeld:**
```sql
SELECT COUNT(*) FROM events
WHERE event_type = 'login' AND network = 'hosting';
```
Dit geeft 261 logins.

**Nieuw: verschillende klanten tellen.** `COUNT(*)` telt regels. Logt één klant 10 keer in, dan telt hij 10 keer mee. Wil je weten hoeveel *verschillende* klanten het zijn? Combineer dan `COUNT` met `DISTINCT` uit opdracht 3:
```sql
SELECT COUNT(DISTINCT user_id) FROM events
WHERE event_type = 'password_reset';
```
Dit telt hoeveel verschillende klanten hun wachtwoord resetten. Elke klant telt maar één keer.

**Voorspel eerst:** komen die 261 hosting-logins van veel verschillende klanten, of van een paar?
**Jouw vraag:** bij hoeveel verschillende klanten werd er vanaf `hosting` ingelogd?

<details><summary>Hint</summary>

Neem het nieuwe voorbeeld, en gebruik de `WHERE` van de hosting-query erboven.
</details>
<details><summary>Antwoord</summary>

```sql
SELECT COUNT(DISTINCT user_id) FROM events
WHERE event_type = 'login' AND network = 'hosting';
```
260 verschillende klanten.
</details>
<details><summary>Denkvraag: welke aanval is dit?</summary>

Credential stuffing. Eén server probeert gelekte wachtwoorden bij honderden accounts. Bijna alles mislukt, maar een paar komen binnen. Tel maar met `AND result = 'success'` erbij: dat zijn er 4. Daarvoor bouw je later detectie CS-001.
</details>

### Opdracht 9: wie is het slachtoffer
**Voorbeeld:**
```sql
SELECT e.timestamp, e.event_type, u.name
FROM events e
JOIN users u ON u.user_id = e.user_id
WHERE e.user_id = 'U00005';
```
Wat er nieuw is:
- `JOIN users` plakt de tabel `users` aan `events`, zodat je de naam naast elk event ziet.
- `events e` en `users u`: `e` en `u` zijn korte namen voor de twee tabellen.
- `e.timestamp` betekent: de kolom `timestamp` uit tabel `e`. `u.name` is de kolom `name` uit tabel `u`.
- `ON u.user_id = e.user_id` zegt welke regels bij elkaar horen: die met dezelfde klant.

**Jouw vraag:** wat is de naam van `U00918`, en welke `mfa_method` heeft die klant?

<details><summary>Hint</summary>

Voeg `u.mfa_method` toe na `SELECT`, en verander de `user_id`.
</details>
<details><summary>Antwoord</summary>

```sql
SELECT e.timestamp, e.event_type, u.name, u.mfa_method
FROM events e
JOIN users u ON u.user_id = e.user_id
WHERE e.user_id = 'U00918';
```
Sara de Wit, met `sms`.
</details>
<details><summary>Denkvraag: waarom maakt `sms` haar kwetsbaar?</summary>

Wie haar telefoonnummer overneemt (SIM-swap), krijgt ook haar sms-codes. Met een authenticator-app of passkey had dit niet gewerkt.
</details>

---

## Dag 4: je eerste detectie

### Opdracht 10: hoe snel ging het?
**Nieuw: meerdere waarden tegelijk.** Wil je twee soorten events zien? Zet ze in een lijstje met `IN`:
```sql
SELECT timestamp, event_type FROM events
WHERE user_id = 'U00918'
  AND event_type IN ('password_reset', 'mfa_changed');
```
`IN ('a', 'b')` betekent: de waarde is `a` of `b`.

**Jouw vraag:** hoeveel minuten zaten er bij `U00005` tussen het toevoegen van een nieuw adres (`withdrawal_address_added`) en de opname (`withdrawal`)?

<details><summary>Hint</summary>

Neem het voorbeeld hierboven. Verander de klant in `U00005` en de twee events in `'withdrawal_address_added'` en `'withdrawal'`. Kijk dan naar `timestamp`.
</details>
<details><summary>Antwoord</summary>

```sql
SELECT timestamp, event_type, address FROM events
WHERE user_id = 'U00005'
  AND event_type IN ('withdrawal_address_added', 'withdrawal');
```
4 minuten: 02:50 nieuw adres, 02:54 opname.
</details>

### Opdracht 11: lees een echte detectie
Dit is een detectie: hij zoekt opnames naar een adres dat minder dan 60 minuten eerder is toegevoegd. Lees hem regel voor regel met het spiekbriefje ernaast.

```sql
SELECT DISTINCT a.user_id AS entity
FROM events a
JOIN events w
  ON w.user_id = a.user_id
 AND w.address = a.address
 AND w.event_type = 'withdrawal'
WHERE a.event_type = 'withdrawal_address_added'
  AND (julianday(w.timestamp) - julianday(a.timestamp)) * 24 * 60 BETWEEN 0 AND 60;
```

**Nieuw in deze query** (lees dit eerst):
- `AS entity` geeft de kolom een andere naam. De test zoekt naar een kolom die `entity` heet.
- `FROM events a JOIN events w` gebruikt dezelfde tabel twee keer, met twee korte namen. Net als `e` en `u` in opdracht 9, maar nu twee keer `events`.
- Na `ON` staan nu drie voorwaarden met `AND`. Een regel uit `a` en een regel uit `w` horen alleen bij elkaar als alle drie kloppen.
- `julianday(...)` maakt van een tijd een getal in dagen. Het verschil × 24 × 60 = het aantal minuten ertussen.
- `BETWEEN 0 AND 60` betekent: van 0 tot en met 60.

**Leesvragen** (beantwoord ze eerst zelf):
1. Wat is `a`, en wat is `w`?
2. Waarom staat `w.address = a.address` erin?
3. Wat rekent de laatste regel uit?

<details><summary>Antwoorden</summary>

1. Twee keer dezelfde tabel `events`. `a` is het toevoegen van een adres, `w` is de opname.
2. Zodat je alleen opnames vindt naar het adres dat net werd toegevoegd.
3. Het aantal minuten tussen toevoegen en opnemen. Alleen 0 tot 60 minuten telt.
</details>

**Voorspel eerst:** hoeveel klanten vindt deze detectie? Draai hem daarna.

<details><summary>Antwoord</summary>

5 klanten. Maar je weet dat er maar 2 SIM-swap-slachtoffers zijn...
</details>

### Opdracht 12: laat de test het nakijken
1. Ga in Verkenner naar `D:\crypto-soc-detection\detections\ATO-001-sim-swap-takeover`.
2. Rechtsklik op `detection.sql` → **Openen met** → **Kladblok**.
3. Plak de query van opdracht 11 onder de regels die met `--` beginnen. Sla op met **Ctrl + S**.
4. Druk op de Windows-toets, typ `PowerShell` en druk op Enter.
5. Typ deze twee regels, elk gevolgd door Enter:
   ```
   cd D:\crypto-soc-detection
   python tests\run_detections.py
   ```

Je krijgt een tabel. De kolommen betekenen:
- **Caught:** aanvallen die je detectie vond
- **False alarms:** klanten die je ten onrechte aanwees
- **Missed:** aanvallen die je detectie miste
- **TODO:** detecties die nog leeg zijn (die doe je later)

Bij ATO-001 zie je: Caught 2, False alarms 3, Missed 0. Je ving beide aanvallen, maar ook 3 klanten die geen SIM-swap-slachtoffer waren.

**Jouw vraag:** zoek uit wat de 2 echte slachtoffers hebben en de 3 andere niet. Draai dit, en vergelijk de kolommen:
```sql
SELECT user_id, timestamp, event_type, network, country, auth_method
FROM events
WHERE user_id IN ('U00005', 'U00918', 'U00226', 'U00287', 'U00669')
  AND event_type IN ('password_reset', 'mfa_changed', 'withdrawal_address_added');
```

<details><summary>Hint</summary>

Kijk welke klanten een `password_reset` of `mfa_changed` hebben, en via welk `network`.
</details>
<details><summary>Antwoord</summary>

Alleen `U00005` en `U00918` hadden een `password_reset` en een `mfa_changed` via `sms`, vanaf een `mobile` netwerk, vlak voor de opname. De andere drie zijn ook aanvallen, maar van een ander soort: credential stuffing en address poisoning. Daar bouw je aparte detecties voor.

In week 2 verbeter je ATO-001 tot hij alleen de 2 echte slachtoffers vindt. Schrijf je aanpak alvast in de README van de detectie.
</details>
