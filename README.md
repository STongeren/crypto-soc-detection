# crypto-soc-detection

Detection engineering for a crypto exchange: account takeover, credential stuffing, insider access and address poisoning.

I'm a Cyber Security student (HvA, Netherlands) learning the tools that crypto-exchange SOC teams use. Every detection here follows the [Alerting and Detection Strategy](https://github.com/palantir/alerting-detection-strategy-framework) format, is tested automatically against labelled data, and gets built in five languages: SQL, KQL, SPL, Python and Sigma.

## Follow along

Want to learn this with me? **[Setup: everything you need](SETUP.md)** has the downloads for Windows, Mac and Linux. You only need two things to start: the dataset and DB Browser for SQLite. Then go to [week 1](learning/week1-sql.md).

## Detections

| ID | What it catches | ATT&CK | SQL | KQL | SPL | Python | Sigma |
|---|---|---|---|---|---|---|---|
| [ATO-001](detections/ATO-001-sim-swap-takeover) | Account takeover after a SIM swap | T1451, T1078, T1657 | in progress | | | | |
| [CS-001](detections/CS-001-credential-stuffing) | Credential stuffing from one source | T1110.004 | | | | | |
| [INS-001](detections/INS-001-support-agent-no-ticket) | Support agent opening accounts without a ticket | T1078 | | | | | |
| [AP-001](detections/AP-001-address-poisoning) | Withdrawal to a poisoned look-alike address | T1657 | | | | | |

## How it is tested

`data/generate_exchange_logs.py` builds a synthetic exchange: 1,000 users, about 29,000 events over 45 days. Logins, resets, 2FA changes, deposits, withdrawals and support-agent account views.

- **Hidden attacks:** 2 SIM-swap takeovers, 1 credential-stuffing wave, 1 insider support agent, 2 address-poisoning victims.
- **Look-alikes that should not alert:** a traveller, a user who forgot their password, an active trader, and an agent on a busy incident day.
- **Labels:** the answers live in `tests/ground_truth.json`.

`tests/run_detections.py` runs every detection against the labelled data (`detection.sql` against `exchange.db`, `detection.py` against the JSON log) and reports what it caught, the false alarms and what it missed. KQL and SPL versions are tested by hand in Azure Data Explorer and Splunk.

```
python data/generate_exchange_logs.py
python tests/run_detections.py
```

Everything is synthetic: no real people, IPs or wallet addresses.

## Repo layout

```
data/          dataset generator (output files are created locally, not committed)
detections/    one folder per detection: ADS write-up + implementations
tests/         ground truth and the scoring script
learning/      weekly exercises I work through
```

## Roadmap

Ordered by how often crypto SOC job postings ask for each skill (10 postings checked in November 2026).

| Week | Skill | Asked in |
|---|---|---|
| 1 | [SQL](learning/week1-sql.md) | foundation (and 4 of 5 investigations postings) |
| 2 | [KQL (Microsoft Sentinel)](learning/week2-kql.md) | 5 of 10 name KQL or a close cousin |
| 3 | [SPL (Splunk)](learning/week3-spl.md) | SIEM in 10 of 10 |
| 4 | [Python + alert enrichment](learning/week4-python.md) | 7 of 10 |
| 5 | Sigma + tuning false positives | detection engineering |
| 6 | Identity logs + AWS CloudTrail | 6 and 7 of 10 |
| 7 | EDR + phishing triage | 7 and 3 of 10 |
| 8 | Incident report | case writing in 5 of 10 |
| + | Optional: blockchain tracing, Kubernetes | plus, not required |
