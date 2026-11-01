# 🛡️ PhishGuard API Server — Phishing Email Detector (Backend)

A modular, lightweight **Python Flask REST API** powering the PhishGuard Phishing Email Detection & Threat Intelligence Platform.

The server handles high-performance streaming, filtering, and CRUD operations over a **71,000+ record email corpus** (`data.csv`), manages active threat domain intelligence (`blacklist.json`), logs operational audit trails (`history.json`), and computes statistical distributions using **NumPy** and **pandas**.

---

## 🚀 Key Modules & Architecture

The backend is built around a clean, decoupled **Blueprint architecture**:

```
Phishing_Email_Detector_Server/
├── app.py                      # Application factory, blueprint registration & CORS
├── requirements.txt            # Python dependencies (flask, flask-cors, pandas, numpy)
│
├── Dataset/                    # Dataset Management & CRUD Module
│   ├── dataset_service.py      # CSV I/O, fast in-memory indexing, search, & pagination
│   ├── email_record.py         # EmailRecord data model, domain & URL regex extractors
│   └── routes.py               # Blueprint: /api/dataset endpoints
│
├── Blacklist/                  # Threat Domain Intelligence Module
│   ├── blacklist_service.py    # Domain normalization, validation, & blacklist.json I/O
│   └── routes.py               # Blueprint: /api/blacklist endpoints
│
├── History/                    # Activity & Audit History Module
│   ├── history_service.py      # Structured audit logging & history.json persistence
│   └── routes.py               # Blueprint: /api/history endpoints
│
├── Analysis/                   # Statistical Analytics Module
│   ├── analytics_service.py    # NumPy risk calculations, token frequencies, & summaries
│   └── routes.py               # Blueprint: /api/analytics endpoints
│
└── data/                       # Persistent Data Storage
    ├── data.csv                # 71,000+ email dataset records
    ├── blacklist.json          # Active blocked domain registry
    └── history.json            # Operational activity audit logs
```

---

## 📡 API Reference & Endpoints

### 1. Dataset Management (`/api/dataset`)

| Method | Endpoint | Description | Query / Body Parameters |
|---|---|---|---|
| `GET` | `/api/dataset` | Retrieve paginated email records | `page` (default: 1), `per_page` (default: 20, max: 200), `all` (`true`\|`false`) |
| `GET` | `/api/dataset/search` | Search & filter corpus records | `q` (query string), `label` (`0` or `1`), `domain` (filter domain), `page`, `per_page` |
| `POST` | `/api/dataset` | Create a new email record in `data.csv` | Body: `{ sender, receiver, subject, body, label, date? }` |
| `PUT` | `/api/dataset/<id>` | Update an existing email record | Body: `{ sender?, receiver?, subject?, body?, label? }` |
| `DELETE` | `/api/dataset/<id>` | Delete an email record from `data.csv` | Path parameter: `id` |
| `GET` | `/api/dataset/export` | Export filtered dataset records as CSV | `q`, `label`, `domain` (triggers direct CSV file download) |

---

### 2. Threat Domain Blacklist (`/api/blacklist`)

| Method | Endpoint | Description | Query / Body Parameters |
|---|---|---|---|
| `GET` | `/api/blacklist` | List all blacklisted threat domains | None |
| `POST` | `/api/blacklist` | Add a domain or sender to the blacklist | Body: `{ "domain": "malicious-host.com" }` |
| `DELETE` | `/api/blacklist/<domain>` | Remove a domain from the blacklist | Path parameter: `domain` (e.g. `malicious-host.com`) |

---

### 3. Activity & Audit History (`/api/history`)

| Method | Endpoint | Description | Query / Body Parameters |
|---|---|---|---|
| `GET` | `/api/history` | Retrieve activity audit records | `action` (`ADD`, `EDIT`, `DELETE`, `VIEW`, `BLACKLIST_ADD`, `BLACKLIST_REMOVE`), `entity_type`, `limit` (default: 200) |
| `POST` | `/api/history/log` | Record a user or system audit event | Body: `{ action, entity_type, entity_id, summary, details, actor }` |
| `DELETE` | `/api/history/<id>` | Delete a single history entry | Path parameter: `id` |
| `DELETE` | `/api/history` | Clear all activity history records | None |

---

### 4. Statistical Analysis (`/api/analytics`)

| Method | Endpoint | Description | Response Highlights |
|---|---|---|---|
| `GET` | `/api/analytics/summary` | Executive summary metrics | Total dataset rows, phishing ratio, audited actions count, blocked domains count |
| `GET` | `/api/analytics/scores` | Statistical score distribution | Mean, Standard Deviation, Median, 25th percentile, 75th percentile, Min, Max, and 10-bin histogram |
| `GET` | `/api/analytics/top-keywords` | Frequent phishing keywords | High-frequency deceptive words from `body` where `label = 1` |
| `GET` | `/api/analytics/domain-breakdown` | Origin domain frequency | Top sender domains associated with phishing records |

---

## 💾 Data Models & Schemas

### 1. Email Record (`data/data.csv`)
The primary corpus stores 71,000+ email records with the following attributes:
* **`sender`** *(string)*: Origin email address and sender header.
* **`receiver`** *(string)*: Recipient email address.
* **`date`** *(timestamp)*: Chronological log timestamp.
* **`subject`** *(string)*: Subject line inspected for threat indicators.
* **`body`** *(multiline text)*: Full email body evaluated for phishing keywords and URLs.
* **`label`** *(integer)*: Ground truth classification (`0` = Safe / Legitimate, `1` = Phishing).
* **`urls`** *(extracted array)*: Extracted HTTP/HTTPS hyperlinks and IP links.
* **`domain`** *(extracted hostname)*: Normalized root domain parsed from the sender address.

### 2. Domain Blacklist (`data/blacklist.json`)
```json
[
  "secure-login-attempt.com",
  "verify-account-security.net",
  "update-billing-profile.org"
]
```

### 3. Audit History Log (`data/history.json`)
```json
[
  {
    "id": "hist_1793532838837",
    "timestamp": "2026-11-01T17:35:00+06:00",
    "action": "BLACKLIST_ADD",
    "entity_type": "BLACKLIST",
    "entity_id": "phishing-origin.com",
    "summary": "Added domain phishing-origin.com to active blacklist",
    "actor": "Administrator",
    "details": { "domain": "phishing-origin.com" }
  }
]
```

---

## ⚙️ Installation & Running the Server

### Prerequisites
* **Python**: 3.9 or higher
* **pip**: Python package installer

---

### Step 1: Install Dependencies

```bash
cd Phishing_Email_Detector_Server

# (Optional) Create and activate a virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux / macOS:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

---

### Step 2: Start the Development Server

```bash
python app.py
```

The server binds to `http://0.0.0.0:5000` (accessible at `http://127.0.0.1:5000` locally):

```
============================================================
  PhishGuard API Server running at http://127.0.0.1:5000
  Dataset API:   http://127.0.0.1:5000/api/dataset
  Blacklist API: http://127.0.0.1:5000/api/blacklist
  History API:   http://127.0.0.1:5000/api/history
  Analytics API: http://127.0.0.1:5000/api/analytics/summary
============================================================
```

---

### Step 3: Verify the Server Health

Open a browser or run `curl`:

```bash
curl http://127.0.0.1:5000/
```

Expected JSON response:
```json
{
  "status": "online",
  "service": "PhishGuard API Server",
  "version": "1.0.0",
  "endpoints": [...]
}
```

---

## 🔒 CORS Configuration

Cross-Origin Resource Sharing (CORS) is enabled via `flask-cors` for all routes under `/api/*`, allowing seamless communication with the Next.js frontend client (`http://localhost:3000`).

---

## 📦 Production Deployment

For production deployments, execute the Flask application using a production WSGI server:

### Using Waitress (Windows / Cross-platform):
```bash
pip install waitress
waitress-serve --port=5000 app:app
```

### Using Gunicorn (Linux / macOS):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 📄 License & Attribution

Part of the **PhishGuard Phishing Email Detection & Threat Intelligence Platform**.  
Maintained in `Phishing_Email_Detector_Server` for dataset operations, threat intelligence indexing, and analytical processing.
