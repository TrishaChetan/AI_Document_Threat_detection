# Security AI

**AI-Powered Web Vulnerability Assessment Platform**

Security AI takes vulnerability scan reports (OWASP ZAP XML or JSON reports), parses them, uses an AI model to generate risk analysis and remediation recommendations, and produces a downloadable PDF report — all through a web dashboard.

---

## Features

- **Upload & Parse** — Upload OWASP ZAP reports in XML or JSON (`zap-baseline.py -x`/`-J`). Findings from every scanned site in the report are included
- **AI-Powered Analysis** — Uses an LLM (via NVIDIA's API) to generate contextual recommendations for each finding
- **Risk Scoring** — 0–100 score plus a Critical/High/Medium/Low rating. The worst finding sets a floor and extra findings add risk with diminishing returns, so scores stay comparable instead of all hitting 100
- **PDF Reports** — Auto-generates a downloadable PDF summary of each scan
- **Scan History** — View, retrieve, and delete past scans
- **Dashboard Stats** — Knowledge base statistics and scan summaries at a glance

---

## Tech Stack

**Backend**
- Python 3.11+
- FastAPI + Uvicorn
- SQLite / MongoDB (data layer — see setup)
- OpenAI-compatible client (NVIDIA API) for AI recommendations
- ReportLab + python-docx for report generation
- lxml + BeautifulSoup for XML parsing

**Frontend**
- React 19 + Vite
- Tailwind CSS
- Axios, React Router, Recharts

---

## Project Structure

```
.
├── backend/
│   ├── ai/              # LLM service & recommendation engine
│   ├── api/             # FastAPI routes (scan, upload, stats)
│   ├── data/            # Knowledge base data
│   ├── database/        # DB connection & scan repository
│   ├── parsers/         # ZAP XML + JSON report parsing
│   ├── reports/         # PDF report generation
│   ├── schemas/         # Pydantic models
│   ├── services/        # Core scan/analysis pipeline
│   ├── main.py          # Entry point
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/         # Axios API client
│   │   ├── components/  # UI components (Navbar, Sidebar, etc.)
│   │   └── pages/       # Dashboard, Upload, Results
│   └── package.json
├── reports/zap/         # Sample ZAP scan reports
└── tests/                # Backend unit tests
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js (LTS) + npm
- A running MongoDB instance (local or Atlas) **or** SQLite (no setup needed)
- An NVIDIA API key ([build.nvidia.com](https://build.nvidia.com))

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
pip install pymongo openai
```

Create `backend/.env`:
```
NVIDIA_API_KEY=your_key_here
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=your_model_name
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=guardex_db
```

Run the backend:
```bash
uvicorn api.app:app --reload
```
Backend runs at `http://127.0.0.1:8000`

### Frontend Setup

```bash
cd frontend
npm install
```

Create `frontend/.env`:
```
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

Run the frontend:
```bash
npm run dev
```
Frontend runs at `http://localhost:5173`

---

## Comparing Two Scans

See what a release fixed, what it introduced and what is still open:

```bash
cd backend
python compare_scans.py ../reports/zap/xml/dvwa_scan_01.xml ../reports/zap/xml/dvwa_scan_02.xml
```

```
Trend: REGRESSED  ·  4 new (0 High)  ·  1 fixed (0 High)  ·  8 still open  ·  0 changed severity
```

Findings are matched on title, CWE, URL path and parameter, ignoring host, port and query string, so a re-scan against a different environment still lines up. The command exits with code 1 when the newer scan introduces any High finding, so it can gate a CI pipeline. The same comparison is available as `POST /api/v1/compare` (multipart fields `baseline` and `current`, XML or JSON).

## Exporting Findings (SARIF / CSV)

```bash
cd backend
python export_findings.py ../reports/zap/xml/dvwa_scan_01.xml --format sarif -o zap.sarif
python export_findings.py report.json --format csv -o findings.csv
```

**SARIF 2.1.0** is the format GitHub code scanning reads: upload the file (for example with `github/codeql-action/upload-sarif` in a workflow) and every ZAP finding appears in the repository's **Security** tab, ranked by severity with CWE tags and the fix advice. **CSV** is sorted High → Informational with HTML stripped from descriptions, ready for a spreadsheet or ticket import. Also available as `POST /api/v1/export?format=sarif|csv`.

## Remediation Plan (fix tickets with due dates)

```bash
cd backend
python remediation_plan.py ../reports/zap/xml/webgoat_scan_01.xml            # Markdown
python remediation_plan.py report.json --format csv -o plan.csv --sla high=14,medium=60
```

Scanners list symptoms; teams fix causes. The plan groups findings that share one fix into a single ticket — CSP, anti-clickjacking and X-Content-Type-Options become *"Add missing HTTP security headers"* in the web-server config; the cookie-flag findings become *"Harden session cookie flags"* — and keeps everything else as one ticket per alert type. Each ticket says where the fix lives (server config or application code), a rough effort (S/M/L), how to fix it, and the affected URLs and CWEs.

Due dates come from a severity SLA counted from the scan date (High 30 days, Medium 90, Low 180 by default; override with `--sla`), and overdue tickets are flagged, most urgent first. Informational findings are left out unless you pass `--include-info`. Also available as `POST /api/v1/remediation-plan?format=json|md|csv`.

## Running Tests

From the repository root:

```bash
pip install pytest
pytest tests
```

`tests/conftest.py` puts `backend/` on the import path. Scripts that call the NVIDIA API run only when `NVIDIA_API_KEY` is set, and the batch scripts run only when `backend/temp_uploads/` exists.

## API Endpoints

| Method | Endpoint                  | Description                       |
|--------|----------------------------|------------------------------------|
| GET    | `/api/v1/health`           | Health check                       |
| POST   | `/api/v1/scan`             | Upload ZAP XML/JSON report & run analysis |
| GET    | `/api/v1/scans`            | Get all past scans                 |
| GET    | `/api/v1/scans/{scan_id}`  | Get a specific scan                |
| DELETE | `/api/v1/scans/{scan_id}`  | Delete a scan                      |
| POST   | `/api/v1/upload/xml`       | Upload and parse raw XML           |
| GET    | `/api/v1/stats`            | Knowledge base statistics          |

---

## License

This project is for educational purposes as part of a college project.

## Contributors

- TrishaChetan
