# Instagram Lead Generator 🚀

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688.svg)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063.svg)](https://docs.pydantic.dev/)
[![Tests](https://img.shields.io/badge/Tests-Pytest%20Passing-brightgreen.svg)](https://pytest.org/)

An automated, asynchronous lead generation and data extraction engine designed to gather contact information from public and business Instagram profiles at scale. Built with anti-bot evasion, randomized jitter pacing, local SQLite caching, and dual CLI & REST API interfaces.

---

## 🌟 Key Features

- **Rich Data Extraction:** Extracts verified public metadata including business name, biography, category, verified phone numbers, direct emails, physical business addresses, external website URLs, follower counts, and engagement stats.
- **Intelligent Contact & Link Parsing:** Filters out social redirect links (e.g., Facebook, TikTok) to isolate actual business domains, and leverages regex normalizers for phone and email extraction.
- **Anti-Bot & Rate-Limiting Protection:** Implements session cookie-based authentication, configurable pacing delays with randomized jitter (8–20s default), and controlled concurrency to safeguard scraping sessions.
- **Smart Duplicate Prevention & Caching:** Integrated SQLite database (`scraper_cache.db`) ensures profiles are never scraped twice, conserving bandwidth and avoiding duplicate output.
- **Dual Interface:**
  - **CLI Tool:** Fast command-line interface for ad-hoc queries or bulk processing from `.xlsx` / `.csv` spreadsheets.
  - **REST API (FastAPI):** Asynchronous endpoints with background job queues for headless production pipelines.
- **Multi-Format Export:** Clean exports to Excel (`.xlsx`), CSV, or JSON.
- **Test Suite Included:** Unit tests covering normalizers, extractors, and edge cases.

---

## 🏗️ Architecture

```
InstagramLeadGenerator/
├── src/
│   ├── api/             # FastAPI REST endpoints & background task runners
│   ├── config/          # Pydantic-based configuration management (.env)
│   ├── export/          # Export handlers (Excel/CSV/JSON) & SQLite cache manager
│   ├── extractor/       # Regex & NLP-based bio, email, and phone extractors
│   ├── parser/          # Profile response normalization & link filters
│   ├── scraper/         # Private API scraper, concurrency controllers, & proxy manager
│   ├── utils/           # Normalizers, cleaners, and logging configuration
│   └── cli.py           # CLI entry point
├── tests/               # Pytest unit tests
├── InputDate/           # Input directory for lead files (.xlsx / .csv)
├── OutputData/          # Export directory for processed leads
├── requirements.txt     # Production dependencies
└── .env.example         # Template configuration
```

---

## ⚡ Quick Start

### 1. Clone & Install Dependencies

```powershell
# Clone the repository
git clone https://github.com/maitreyagit/InstagramLeadGenerator.git
cd InstagramLeadGenerator

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example configuration:
```powershell
cp .env.example .env
```

| Setting | Default | Description |
|---|---|---|
| `CONCURRENCY` | `1` | Recommended: `1` for the private API to avoid rate limits |
| `MIN_DELAY` | `8` | Minimum seconds between consecutive requests |
| `MAX_DELAY` | `20` | Maximum seconds between consecutive requests |
| `RETRIES` | `3` | Number of retry attempts on transient network errors |
| `EXPORT_FORMAT` | `excel` | Export format: `excel`, `csv`, or `json` |
| `OUTPUT_FOLDER` | `OutputData` | Destination folder for exported files |

### 3. Authentication (One-Time Setup)

The engine authenticates via session cookies—no plain-text passwords stored:
1. Log into Instagram in your web browser.
2. Open DevTools (`F12`) → **Application** tab → **Cookies** → `https://www.instagram.com`.
3. Copy the value of the `sessionid` cookie.
4. Run the interactive login command:
   ```powershell
   python -m src.cli --login
   ```
5. Paste your `sessionid`. Your session state is saved locally to `auth_state.json`.

---

## 💻 Usage

### Command Line Interface (CLI)

#### Scrape a Single Profile
```powershell
python -m src.cli "nike"
```

#### Bulk Process from Spreadsheet
Place your `.xlsx` or `.csv` lead list into `InputDate/` (usernames in the first column), then execute:
```powershell
python -m src.cli "InputDate/sample_leads.csv"
```
Scraped results are automatically formatted and exported to `OutputData/`.

---

### REST API (FastAPI)

Start the API server:
```powershell
uvicorn src.api.main:app --reload
```
Open interactive Swagger documentation at `http://127.0.0.1:8000/docs`.

- `POST /scrape` — Scrape an individual profile synchronously.
- `POST /bulk` — Submit a batch of targets to the asynchronous background worker queue.
- `GET /status/{job_id}` — Check status and retrieve output for an asynchronous bulk job.

---

## 🧪 Running Tests

Ensure all extraction and normalization logic passes:
```powershell
python -m pytest
```

---

## 🛡️ Best Practices & Disclaimer

- **Anti-Bot Pacing:** Instagram aggressively monitors request frequency. Keep `CONCURRENCY=1` and maintain randomized delays (8–20s) to simulate natural human activity.
- **Educational / Internal Use:** This software is intended for legitimate research and marketing operations complying with applicable terms of service and data privacy laws.
