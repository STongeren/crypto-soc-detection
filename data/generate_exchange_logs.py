"""Generate a synthetic crypto-exchange log dataset for detection engineering practice.

Everything is fake: no real people, IPs or wallet addresses.

Hidden in the data (ground truth in tests/ground_truth.json):
  ATO                 account takeover after a SIM swap (SMS reset, 2FA change, new address, balance out)
  CRED_STUFFING       one hosting IP tries many accounts; a few logins succeed
  INSIDER             a support agent opens many high-balance accounts without a ticket, at night
  ADDRESS_POISONING   a dust deposit from a look-alike address, later the victim withdraws to it

Plus benign look-alikes that a good detection should NOT flag:
  a traveller abroad, a legitimate reset followed by a normal withdrawal,
  an active trader with many withdrawals, and support agents bulk-handling tickets.

Outputs (this folder):
  users.csv, events.csv, events.jsonl, exchange.db (SQLite: tables users, events)
and ../tests/ground_truth.json

Run:  python data/generate_exchange_logs.py
"""
import csv
import json
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

SEED = 2027
HERE = Path(__file__).parent
TESTS = HERE.parent / "tests"
START = datetime(2026, 10, 1)
DAYS = 45
N_USERS = 1000
N_AGENTS = 12

rng = random.Random(SEED)

COUNTRIES = ["NL"] * 6 + ["BE", "DE", "FR", "ES"]
ASSETS = ["BTC", "ETH", "USDC", "SOL"]
UA = {
    "ios": "ExchangeApp/5.12 (iPhone; iOS 18.4)",
    "android": "ExchangeApp/5.12 (Android 15; Pixel 8)",
    "web": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/141.0",
    "mac": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) Safari/605.1",
    "script": "python-requests/2.32",
}
PREFIX = {"NL": "10.31", "BE": "10.32", "DE": "10.49", "FR": "10.33", "ES": "10.34",
          "US": "10.1", "TH": "10.66", "RU": "198.51", "VN": "203.0", "SG": "192.0"}
FIRST = ["Sam", "Noa", "Liam", "Emma", "Daan", "Julia", "Finn", "Sara", "Milan", "Lotte",
         "Bram", "Eva", "Luuk", "Anna", "Jesse", "Fleur", "Thijs", "Iris", "Ruben", "Mila"]
LAST = ["de Vries", "Jansen", "Bakker", "Visser", "Smit", "Meijer", "de Boer", "Mulder",
        "Bos", "Vos", "Peters", "Hendriks", "Dekker", "Brouwer", "de Wit", "Dijkstra"]


def ip_in(country):
    return f"{PREFIX[country]}.{rng.randint(0, 255)}.{rng.randint(1, 254)}"


def new_address():
    return "0x" + "".join(rng.choice("0123456789abcdef") for _ in range(40))


def lookalike(addr):
    """Same first 6 and last 4 characters, different middle (what address poisoning relies on)."""
    middle = "".join(rng.choice("0123456789abcdef") for _ in range(32))
    return addr[:6] + middle + addr[-4:]


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


users = []
for i in range(1, N_USERS + 1):
    country = rng.choice(COUNTRIES)
    platform = rng.choice(["ios", "android", "web", "mac"])
    users.append({
        "user_id": f"U{i:05d}",
        "name": f"{rng.choice(FIRST)} {rng.choice(LAST)}",
        "country": country,
        "signup_date": (START - timedelta(days=rng.randint(30, 1500))).strftime("%Y-%m-%d"),
        "balance_eur": round(rng.lognormvariate(7.3, 1.4), 2),
        "mfa_method": rng.choices(["sms", "totp", "passkey"], [45, 45, 10])[0],
        "home_ip": ip_in(country),
        "home_device": f"dev-{rng.randint(100000, 999999)}",
        "platform": platform,
        "addresses": [new_address() for _ in range(rng.randint(1, 3))],
    })
by_id = {u["user_id"]: u for u in users}
agents = [f"AG{i:02d}" for i in range(1, N_AGENTS + 1)]

events = []
COLS = ["event_id", "timestamp", "user_id", "event_type", "result", "ip", "country", "network",
        "device_id", "user_agent", "auth_method", "amount_eur", "asset", "address",
        "actor", "agent_id", "ticket_id"]


def add(dt, u, etype, **kw):
    e = {
        "timestamp": iso(dt),
        "user_id": u["user_id"] if u else None,
        "event_type": etype,
        "result": kw.get("result", "success"),
        "ip": kw.get("ip", u["home_ip"] if u else None),
        "country": kw.get("country", u["country"] if u else None),
        "network": kw.get("network", "residential"),
        "device_id": kw.get("device", u["home_device"] if u else None),
        "user_agent": kw.get("ua", UA[u["platform"]] if u else None),
        "auth_method": kw.get("auth"),
        "amount_eur": kw.get("amount"),
        "asset": kw.get("asset"),
        "address": kw.get("address"),
        "actor": kw.get("actor", "customer"),
        "agent_id": kw.get("agent"),
        "ticket_id": kw.get("ticket"),
    }
    events.append(e)


def at(day, h0=7, h1=23):
    return START + timedelta(days=day, hours=rng.randint(h0, h1), minutes=rng.randint(0, 59), seconds=rng.randint(0, 59))


# ---------- Normal customer behaviour ----------
for u in users:
    activity = rng.choice([0.15, 0.3, 0.5, 0.8])
    for day in range(DAYS):
        if rng.random() > activity:
            continue
        t = at(day)
        if rng.random() < 0.04:
            add(t - timedelta(seconds=rng.randint(20, 90)), u, "login", result="failure", auth="password")
        add(t, u, "login", auth="password+" + u["mfa_method"])
        if rng.random() < 0.06:
            add(t + timedelta(minutes=rng.randint(1, 40)), u, "withdrawal",
                amount=round(min(u["balance_eur"] * rng.uniform(0.02, 0.25), 8000), 2),
                asset=rng.choice(ASSETS), address=rng.choice(u["addresses"]))
        if rng.random() < 0.05:
            add(t + timedelta(minutes=rng.randint(1, 40)), u, "deposit",
                amount=round(rng.uniform(20, 1500), 2), asset=rng.choice(ASSETS), address=new_address())
    if rng.random() < 0.05:
        add(at(rng.randint(0, DAYS - 1)), u, "password_reset", auth="email")
    if rng.random() < 0.08:
        a = new_address()
        u["addresses"].append(a)
        add(at(rng.randint(0, DAYS - 2)), u, "withdrawal_address_added", address=a)

# ---------- Normal support work ----------
for day in range(DAYS):
    for ag in agents:
        if rng.random() < 0.25:  # day off
            continue
        for _ in range(rng.randint(8, 25)):
            u = rng.choice(users)
            add(at(day, 8, 17), u, "support_account_view", actor="support_agent", agent=ag,
                ticket=f"T-{rng.randint(100000, 999999)}", ip=f"10.200.{agents.index(ag)}.10",
                country="NL", network="corporate", device=f"corp-{ag}", ua=UA["web"])

truth = {"ATO": [], "CRED_STUFFING": {"ip": None, "compromised_users": []}, "INSIDER": [],
         "ADDRESS_POISONING": [], "BENIGN_LOOKALIKES": []}
used = set()


def pick(filter_fn):
    pool = [u for u in users if u["user_id"] not in used and filter_fn(u)]
    u = rng.choice(pool)
    used.add(u["user_id"])
    return u


# ---------- Attack 1: account takeover after SIM swap (x2) ----------
for day, country in [(9, "RU"), (31, "VN")]:
    u = pick(lambda x: x["mfa_method"] == "sms" and x["balance_eur"] > 3000)
    t = START + timedelta(days=day, hours=rng.randint(1, 4), minutes=rng.randint(0, 59))
    ip, dev, addr = ip_in(country), f"dev-{rng.randint(100000, 999999)}", new_address()
    kw = dict(ip=ip, country=country, network="mobile", device=dev, ua=UA["android"])
    add(t, u, "password_reset", auth="sms", **kw)
    add(t + timedelta(minutes=2), u, "mfa_changed", auth="sms", **kw)
    add(t + timedelta(minutes=3), u, "login", auth="password+totp", **kw)
    add(t + timedelta(minutes=7), u, "withdrawal_address_added", address=addr, **kw)
    add(t + timedelta(minutes=11), u, "withdrawal", amount=round(u["balance_eur"] * 0.96, 2),
        asset="USDC", address=addr, **kw)
    truth["ATO"].append(u["user_id"])

# ---------- Attack 2: credential stuffing (one wave) ----------
cs_ip = ip_in("SG")
truth["CRED_STUFFING"]["ip"] = cs_ip
t0 = START + timedelta(days=20, hours=2, minutes=5)
targets = rng.sample([u for u in users if u["user_id"] not in used], 260)
winners = [u for u in targets if u["mfa_method"] == "passkey"][:0]  # passkeys stop it
weak = [u for u in targets if u["mfa_method"] == "sms"][:3]
for k, u in enumerate(targets):
    tt = t0 + timedelta(seconds=k * 6 + rng.randint(0, 4))
    ok = u in weak
    add(tt, u, "login", result="success" if ok else "failure", auth="password",
        ip=cs_ip, country="SG", network="hosting", device="dev-000000", ua=UA["script"])
for u in weak:
    used.add(u["user_id"])
    truth["CRED_STUFFING"]["compromised_users"].append(u["user_id"])
# one of them gets drained a day later from the same infrastructure
victim = weak[0]
t = t0 + timedelta(days=1, hours=1)
addr = new_address()
kw = dict(ip=cs_ip, country="SG", network="hosting", device="dev-000000", ua=UA["script"])
add(t, victim, "login", auth="password+sms", **kw)
add(t + timedelta(minutes=4), victim, "withdrawal_address_added", address=addr, **kw)
add(t + timedelta(minutes=6), victim, "withdrawal", amount=round(victim["balance_eur"] * 0.9, 2),
    asset="BTC", address=addr, **kw)

# ---------- Attack 3: insider support agent ----------
bad_agent = "AG07"
truth["INSIDER"].append(bad_agent)
rich = sorted(users, key=lambda x: x["balance_eur"], reverse=True)[:250]
for night in (26, 27):
    for u in rng.sample(rich, 90):
        tt = START + timedelta(days=night, hours=rng.randint(0, 3), minutes=rng.randint(0, 59), seconds=rng.randint(0, 59))
        add(tt, u, "support_account_view", actor="support_agent", agent=bad_agent, ticket=None,
            ip="10.200.6.10", country="NL", network="corporate", device="corp-AG07", ua=UA["web"])

# ---------- Attack 4: address poisoning (x2) ----------
for day in (14, 38):
    u = pick(lambda x: x["balance_eur"] > 1500 and len(x["addresses"]) >= 1)
    real = u["addresses"][0]
    fake = lookalike(real)
    t = at(day, 8, 12)
    add(t, u, "deposit", amount=0.0, asset="USDC", address=fake)  # the "dust" from the look-alike
    t2 = t + timedelta(days=2, hours=rng.randint(1, 6))
    add(t2, u, "login", auth="password+" + u["mfa_method"])
    add(t2 + timedelta(minutes=3), u, "withdrawal_address_added", address=fake)
    add(t2 + timedelta(minutes=5), u, "withdrawal", amount=round(u["balance_eur"] * 0.5, 2), asset="USDC", address=fake)
    truth["ADDRESS_POISONING"].append(u["user_id"])

# ---------- Benign look-alikes ----------
# Traveller: new country and device, adds address, withdraws a small amount a day later
u = pick(lambda x: x["balance_eur"] > 2000)
t = START + timedelta(days=17, hours=15)
dev, addr = f"dev-{rng.randint(100000, 999999)}", new_address()
kw = dict(ip=ip_in("TH"), country="TH", network="mobile", device=dev, ua=UA["ios"])
add(t, u, "login", auth="password+" + u["mfa_method"], **kw)
add(t + timedelta(minutes=25), u, "withdrawal_address_added", address=addr, **kw)
add(t + timedelta(hours=27), u, "withdrawal", amount=round(u["balance_eur"] * 0.05, 2), asset="ETH", address=addr, **kw)
truth["BENIGN_LOOKALIKES"].append({"user_id": u["user_id"], "why": "traveller"})

# Legit reset, then a normal withdrawal to a known address the next day
u = pick(lambda x: True)
t = at(22, 9, 12)
add(t, u, "password_reset", auth="email")
add(t + timedelta(minutes=5), u, "login", auth="password+" + u["mfa_method"])
add(t + timedelta(days=1), u, "withdrawal", amount=round(u["balance_eur"] * 0.3, 2), asset="BTC", address=u["addresses"][0])
truth["BENIGN_LOOKALIKES"].append({"user_id": u["user_id"], "why": "forgot password"})

# Active trader: many withdrawals to known addresses
u = pick(lambda x: x["balance_eur"] > 5000)
for day in range(0, DAYS, 2):
    add(at(day), u, "withdrawal", amount=round(rng.uniform(500, 4000), 2), asset=rng.choice(ASSETS), address=rng.choice(u["addresses"]))
truth["BENIGN_LOOKALIKES"].append({"user_id": u["user_id"], "why": "active trader"})

# Support incident day: an agent views many accounts, all with tickets
for _ in range(120):
    w = rng.choice(users)
    add(at(33, 9, 17), w, "support_account_view", actor="support_agent", agent="AG03",
        ticket=f"T-{rng.randint(100000, 999999)}", ip="10.200.2.10", country="NL",
        network="corporate", device="corp-AG03", ua=UA["web"])
truth["BENIGN_LOOKALIKES"].append({"agent_id": "AG03", "why": "busy incident day, every view has a ticket"})

# ---------- Write files ----------
events.sort(key=lambda e: e["timestamp"])
for n, e in enumerate(events, 1):
    e["event_id"] = f"E{n:07d}"

user_cols = ["user_id", "name", "country", "signup_date", "balance_eur", "mfa_method", "home_device"]
with open(HERE / "users.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=user_cols)
    w.writeheader()
    for u in users:
        w.writerow({k: u[k] for k in user_cols})

with open(HERE / "events.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    for e in events:
        w.writerow({k: e[k] for k in COLS})

with open(HERE / "events.jsonl", "w", encoding="utf-8") as f:
    for e in events:
        f.write(json.dumps({k: e[k] for k in COLS}) + "\n")

db = HERE / "exchange.db"
if db.exists():
    db.unlink()
con = sqlite3.connect(db)
con.execute("CREATE TABLE users (" + ", ".join(f"{c} {'REAL' if c == 'balance_eur' else 'TEXT'}" for c in user_cols) + ")")
con.execute("CREATE TABLE events (" + ", ".join(f"{c} {'REAL' if c == 'amount_eur' else 'TEXT'}" for c in COLS) + ")")
con.executemany(f"INSERT INTO users VALUES ({','.join('?' * len(user_cols))})", [tuple(u[k] for k in user_cols) for u in users])
con.executemany(f"INSERT INTO events VALUES ({','.join('?' * len(COLS))})", [tuple(e[k] for k in COLS) for e in events])
con.execute("CREATE INDEX ix_events_user ON events(user_id, timestamp)")
con.execute("CREATE INDEX ix_events_type ON events(event_type)")
con.commit()
con.close()

TESTS.mkdir(exist_ok=True)
(TESTS / "ground_truth.json").write_text(json.dumps(truth, indent=2), encoding="utf-8")
print(f"{len(users)} users, {len(events)} events, {DAYS} days -> {HERE}")
