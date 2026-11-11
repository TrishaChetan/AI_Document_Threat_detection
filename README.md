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
