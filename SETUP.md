# Setup: everything you need

Follow along with me from my videos. Everything here is free.

You only need **two things to start**. The rest you download when you reach that week.

---

## Start here (week 1, 10 minutes)

### 1. Get this repo
No Git needed:
1. On the [repo page](https://github.com/STongeren/crypto-soc-detection), click the green **Code** button → **Download ZIP**.
2. Unzip it:
   - **Windows:** open your Downloads folder, right-click the ZIP → **Extract All** → **Extract**.
   - **Mac:** open your Downloads folder and double-click the ZIP.
3. You now have a folder called `crypto-soc-detection-main`. Move it somewhere you can find it, like your Documents folder.

Know Git? Then:
```
git clone https://github.com/STongeren/crypto-soc-detection.git
```

### 2. Get the dataset
1. Download **[exchange.db](https://github.com/STongeren/crypto-soc-detection/releases/latest/download/exchange.db)** (7 MB). It lands in your Downloads folder.
2. Drag `exchange.db` into the `data` folder inside `crypto-soc-detection-main`.

This is a fake crypto exchange: 1,000 users, about 29,000 events over 45 days, with hidden attacks for you to find.

### 3. Install DB Browser for SQLite
This is where you write your SQL queries.

| Your computer | Download |
|---|---|
| Windows | [Windows installer (64-bit)](https://github.com/sqlitebrowser/sqlitebrowser/releases/download/v3.13.1/DB.Browser.for.SQLite-v3.13.1-win64.msi), or the [no-install zip](https://github.com/sqlitebrowser/sqlitebrowser/releases/download/v3.13.1/DB.Browser.for.SQLite-v3.13.1-win64.zip) |
| Mac | [macOS .dmg](https://github.com/sqlitebrowser/sqlitebrowser/releases/download/v3.13.1/DB.Browser.for.SQLite-v3.13.1.dmg) |
| Linux | `sudo apt install sqlitebrowser` (Ubuntu/Debian), or the [AppImage](https://github.com/sqlitebrowser/sqlitebrowser/releases/download/v3.13.1/DB.Browser.for.SQLite-v3.13.1-x86.64-v2.AppImage) |

All versions: [sqlitebrowser.org/dl](https://sqlitebrowser.org/dl/)

**Installing:**
- **Windows:** double-click the `.msi` file and click **Next** until it's done. (The zip version: extract it, then double-click `DB Browser for SQLite.exe` inside.)
- **Mac:** double-click the `.dmg` file and drag **DB Browser for SQLite** into the **Applications** folder.

### 4. Open the database
1. Open DB Browser for SQLite.
2. Click **Open Database** and pick `exchange.db` in the `data` folder of `crypto-soc-detection-main`.
3. Click the **Execute SQL** tab.
4. Start with [week 1](learning/week1-sql.md). Keep the [cheat sheet](learning/cheatsheet.md) open next to it.

---

## For the test (end of week 1)

The test checks your detections automatically. It needs Python.

| Your computer | Download | Check it works |
|---|---|---|
| Windows | [python.org/downloads](https://www.python.org/downloads/). Tick **"Add python.exe to PATH"** during install | `python --version` |
| Mac | [python.org/downloads](https://www.python.org/downloads/), or `brew install python` with [Homebrew](https://brew.sh) | `python3 --version` |
| Linux | Usually already installed | `python3 --version` |

Run the test from the repo folder. Open a terminal (Windows: Windows key → type `PowerShell` → Enter. Mac: Cmd + Space → type `Terminal` → Return), type `cd ` with a space, drag the `crypto-soc-detection-main` folder into the window, press Enter, then:

| Windows | Mac / Linux |
|---|---|
| `python tests\run_detections.py` | `python3 tests/run_detections.py` |

Want to build the dataset yourself instead of downloading it? Run `python data/generate_exchange_logs.py` (Mac/Linux: `python3`).

---

## Later weeks

Download these when you get there.

| Week | Skill | What you need | Windows | Mac | Linux |
|---|---|---|---|---|---|
| 2 | KQL | Nothing to install. A free Microsoft account. Start with [week 2](learning/week2-kql.md) | [Practice environment in your browser](https://dataexplorer.azure.com/clusters/help/databases/Samples) | same | same |
| 3 | Splunk | Splunk Enterprise (free account, 60-day trial, then a free license that never expires) | [Download](https://www.splunk.com/en_us/download/splunk-enterprise.html) | same page, macOS tab | same page, Linux tab |
| 3 | Splunk | BOTSv3, a real attack dataset (320 MB) | [github.com/splunk/botsv3](https://github.com/splunk/botsv3) | same | same |
| 4 | Python | Python (see above) | | | |
| 5 | Sigma | Nothing to install | [sigconverter.io](https://sigconverter.io) | same | same |
| 6 | Cloud | A free AWS account and the AWS CLI | [AWS CLI](https://aws.amazon.com/cli/) | same page | same page |
| 7 | EDR | Sysmon (Windows only) | [Sysmon](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon) | | |
| 7 | Phishing | Nothing to install | [Message Header Analyzer](https://mha.azurewebsites.net) | same | same |
| + | Blockchain | Nothing to install | [etherscan.io](https://etherscan.io) | same | same |
| + | Kubernetes | Docker Desktop + kind | [Docker Desktop](https://www.docker.com/products/docker-desktop/) and [kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) | same | [Docker Engine](https://docs.docker.com/engine/install/) + kind |

**Nice to have:** a code editor to open the files, like [VS Code](https://code.visualstudio.com/download) (Windows, Mac, Linux). Notepad (Windows) or TextEdit (Mac) also works.

---

## Stuck?

- **"python is not recognized"** (Windows): reinstall Python and tick "Add python.exe to PATH".
- **"data/exchange.db not found"** when running the test: put `exchange.db` inside the `data` folder, not next to it.
- **The Mac says DB Browser can't be opened:** right-click the app → **Open** → **Open**. You only have to do this once.
