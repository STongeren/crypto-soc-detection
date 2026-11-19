# CS-001: Credential stuffing from one source

> Alerting and Detection Strategy (ADS) format, based on the
> [Palantir ADS framework](https://github.com/palantir/alerting-detection-strategy-framework).
> Fill in every section in your own words. Delete the guiding questions when done.

**Status:** TODO

## Goal
One source tries leaked username/password pairs against many accounts in a short time. A few logins succeed.

_What exactly should this alert catch, in one or two sentences?_

## Categorization
T1110.004 Credential Stuffing, T1078 Valid Accounts

## Strategy abstract
_How does the detection work, in plain words? Which events, which fields, which time window?_

## Technical context
_What does a SOC analyst need to know to understand this alert? Which tables and fields in `data/exchange.db`?_

## Blind spots and assumptions
_What would this detection miss? What are you assuming about the data?_

## False positives
_Which normal behaviour could look like this? (Hint: the dataset contains look-alikes on purpose.)_

## Validation
Run `python tests/run_detections.py`. Paste the result line for this detection here.

| Version | True positives | False positives | Missed | What changed |
|---|---|---|---|---|
| v1 | | | | first version |

## Priority
_Low, medium or high? Why?_

## Response
_What should the analyst do when this fires? First 3 steps._

## Implementations
| Language | File | Status |
|---|---|---|
| SQL (SQLite) | `detection.sql` | TODO |
| KQL | `detection.kql` | TODO |
| SPL | `detection.spl` | TODO |
| Python | `detection.py` | TODO |
| Sigma | `detection.yml` | TODO |
