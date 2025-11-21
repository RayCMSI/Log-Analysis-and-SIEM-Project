# Log-Analysis-and-SIEM-Project — Mini SIEM

A tiny, end‑to‑end SIEM‐style pipeline:

**ingest logs → store in SQLite → run rules → show alerts on a Flask dashboard.**

---

## Features

* Parse Apache/Nginx *combined* access logs and simple *auth* failed‑login lines
* Store normalized events in SQLite with useful indexes
* Run detection rules (failed login burst, off‑hours activity)
* View Recent Alerts + Top IPs chart (Chart.js) on a Flask dashboard

---

## Repo layout

```
src/
  db.py
  ingest.py
  run_rules.py
  run_loop.py        # optional: continuous rule runner
  dashboard.py
  parsers/
    apache.py
    auth.py
web/
  templates/
    home.html
sample_logs/
  synthetic/
    access.log
    auth.log
```

> Ensure `src/__init__.py` and `src/parsers/__init__.py` exist (empty files) so `from src...` imports work.

---

## Requirements

* **Python 3.10+** (uses `int | None`)
* **pip / venv**
* macOS/Linux shell examples below (Windows users: use PowerShell equivalents)

Optional (recommended):

* `requirements.txt`:

  ```
  flask>=3.0
  ```

---

## Quick start (copy‑paste)

```bash
# 0) Clone and cd
# git clone <your-repo-url>
# cd Log-Analysis-and-SIEM-Project

# 1) Create & activate a virtualenv
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2) Install deps
pip install -r requirements.txt  # or: pip install flask>=3.0

# 3) Seed sample logs (if you don’t have real logs yet)
mkdir -p sample_logs/synthetic
cat > sample_logs/synthetic/access.log <<'EOF'
203.0.113.5 - - [21/Sep/2025:12:00:01 +0000] "GET /login HTTP/1.1" 401 0
203.0.113.5 - - [21/Sep/2025:12:00:12 +0000] "POST /login HTTP/1.1" 401 0
198.51.100.77 - - [21/Sep/2025:12:01:05 +0000] "GET /index.html HTTP/1.1" 200 5120
EOF
cat > sample_logs/synthetic/auth.log <<'EOF'
Sep 21 12:34:56 host sshd[1234]: Failed password for ray from 203.0.113.5 port 5555 ssh2
Sep 21 12:35:01 host sshd[1234]: Failed password for ray from 203.0.113.5 port 5556 ssh2
Sep 21 12:36:10 host sshd[4321]: Failed password for admin from 198.51.100.77 port 5522 ssh2
EOF

# 4) Ingest (creates DB and loads logs)
python -m src.ingest

# 5a) Run rules once
python -m src.run_rules

# 5b) (Optional) Run rules continuously in the background (every 60s)
python -m src.run_loop &               # background job
# To stop later: kill %1   (or: pkill -f "python -m src.run_loop")

# 6) Start the dashboard (foreground)
python -m src.dashboard
# Open http://127.0.0.1:5000
```

---

## How it works

* `src/ingest.py` reads log files and writes normalized rows into `data/db.sqlite3`.
* `src/rules.py` queries `logs` and writes matches into `alerts`.
* `src/run_rules.py` runs all rules once; `src/run_loop.py` repeats every 60s.
* `src/dashboard.py` renders `web/templates/home.html` with Jinja → HTML + Chart.js.

---

## Common tasks

**Reset the database (start fresh)**

```bash
rm -f data/db.sqlite3
python -m src.ingest
python -m src.run_rules
```

**Run everything with logs captured**

```bash
python -m src.run_loop > run_loop.log 2>&1 &
python -m src.dashboard
```

**Tail alerts directly from SQLite**

```bash
sqlite3 data/db.sqlite3 \
  "SELECT ts, rule_id, severity, entity, summary FROM alerts ORDER BY ts DESC LIMIT 10;"
```

---

## Troubleshooting

**“tuple has no attribute isoformat”**

* In `failed_login_burst`, ensure the window start is a subtraction, not a tuple:

  ```python
  wstart = (datetime.utcnow() - timedelta(minutes=window_minutes)).isoformat()
  ```

**“Incorrect number of bindings supplied”**

* Use named parameters in SQL:

  ```sql
  ... ts >= :wstart ... HAVING cnt > :threshold
  ```

  with args `{ "wstart": wstart, "threshold": threshold }`.

**Dashboard shows JS errors or “Chart is not defined”**

* Ensure Chart.js script tag is correct:

  ```html
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  ```
* Ensure you access the page via Flask (`http://127.0.0.1:5000`), not by opening the HTML file directly.

**Editor shows `Declaration or statement expected` near Jinja blocks**

* The template uses Jinja inside `<script>`. This project serializes data first:

  ```html
  <script id="labels-data" type="application/json">{{ labels | tojson }}</script>
  <script id="counts-data" type="application/json">{{ counts | tojson }}</script>
  ```

  Then parse with JS to keep linting happy.

**Imports fail (`ModuleNotFoundError: src...`)**

* Run via modules from the **repo root**:

  ```bash
  python -m src.ingest
  python -m src.dashboard
  ```
* Ensure `src/__init__.py` and `src/parsers/__init__.py` exist.

---

## Optional enhancements

* Add `config.py` or `.env` for thresholds, windows, and hours
* More rules (404 spike, repeated 401 per user, scanner heuristics)
* GeoIP enrichment on ingest, severity badges, API endpoints
* Dockerfile + compose for one‑command spin‑up

---

## License

Add your preferred license (MIT/Apache-2.0).

