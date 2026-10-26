# PhishGuard 🛡️
### CSC 4162 – Programming in Python | Mid-Term Group Project

A desktop application that detects phishing emails using a hybrid Rule-Based + Naïve Bayes classifier, built entirely with Python standard libraries, NumPy, and pandas.

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python main.py
```

---

## Project Structure

```
Phishing_Email_Detector/
│
├── main.py                  # Entry point
├── requirements.txt         # numpy, pandas
│
├── src/
│   ├── constants.py         # All file paths & config
│   ├── core/
│   │   ├── email_record.py  # EmailRecord data class
│   │   ├── file_handler.py  # CSV & JSON I/O
│   │   ├── validators.py    # Input validation
│   │   ├── analysis.py      # RuleEngine + NaiveBayesModel + NumPy metrics
│   │   ├── detector.py      # PhishingDetector (combines rule + Bayes)
│   │   └── manager.py       # EmailManager (CRUD + history + statistics)
│   └── gui/
│       └── gui.py           # PhishGuardApp (6-tab Tkinter interface)
│
├── data/
│   ├── data.csv             # Full dataset
│   ├── sample_emails.csv    # ~200-row balanced sample for demo
│   ├── model.json           # Trained Naïve Bayes weights
│   ├── history.json         # Scan history log
│   └── blacklist.json       # Blacklisted sender domains
│
├── tests/
│   ├── test_email_record.py
│   ├── test_validators.py
│   ├── test_detector.py
│   └── test_manager.py
│
├── screenshots/             # 8 required screenshots (Day 19)
└── report/                  # Final PDF report
```

---

## Libraries

| Library | Purpose |
|---------|---------|
| **Tkinter** | GUI – tabs, forms, tables, message boxes |
| **NumPy** | Confusion matrix, accuracy, precision, recall, F1 |
| **pandas** | CSV loading, filtering/search, statistics, export |
| Standard library | `csv`, `json`, `os`, `re`, `math`, `random`, `datetime` |

---

## Team

| Role | Member | Modules |
|------|--------|---------|
| A | _Member 1_ | `email_record`, `file_handler`, `validators` |
| B | _Member 2_ | `analysis`, `detector` |
| C | _Member 3_ | `gui`, `main` |
| D | _Member 4_ | `manager`, testing, README, report |
