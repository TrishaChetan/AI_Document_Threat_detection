\# Security AI



\*\*AI-Powered Web Vulnerability Assessment Platform\*\*



Security AI takes vulnerability scan reports (XML format, e.g. from OWASP ZAP), parses them, uses an AI model to generate risk analysis and remediation recommendations, and produces a downloadable PDF report — all through a web dashboard.



\---



\## Features



\- \*\*Upload \& Parse\*\* — Upload XML vulnerability scan reports for automatic parsing

\- \*\*AI-Powered Analysis\*\* — Uses an LLM (via NVIDIA's API) to generate contextual recommendations for each finding

\- \*\*Risk Scoring\*\* — Calculates an overall risk score per scan

\- \*\*PDF Reports\*\* — Auto-generates a downloadable PDF summary of each scan

\- \*\*Scan History\*\* — View, retrieve, and delete past scans

\- \*\*Dashboard Stats\*\* — Knowledge base statistics and scan summaries at a glance



\---



\## Tech Stack



\*\*Backend\*\*

\- Python 3.11+

\- FastAPI + Uvicorn

\- SQLite / MongoDB (data layer — see setup)

\- OpenAI-compatible client (NVIDIA API) for AI recommendations

\- ReportLab + python-docx for report generation

\- lxml + BeautifulSoup for XML parsing



\*\*Frontend\*\*

\- React 19 + Vite

\- Tailwind CSS

\- Axios, React Router, Recharts



\---



\## Project Structure



```

.

├── backend/

│   ├── ai/              # LLM service \& recommendation engine

│   ├── api/             # FastAPI routes (scan, upload, stats)

│   ├── data/            # Knowledge base data

│   ├── database/        # DB connection \& scan repository

│   ├── parsers/         # XML report parsing

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



\---



\## Getting Started



\### Prerequisites

\- Python 3.11+

\- Node.js (LTS) + npm

\- A running MongoDB instance (local or Atlas) \*\*or\*\* SQLite (no setup needed)

\- An NVIDIA API key (\[build.nvidia.com](https://build.nvidia.com))



\### Backend Setup



```bash

cd backend

python -m venv venv

venv\\Scripts\\activate        # Windows

\# source venv/bin/activate   # macOS/Linux



pip install -r requirements.txt

pip install pymongo openai

```



Create `backend/.env`:

```

NVIDIA\_API\_KEY=your\_key\_here

NVIDIA\_BASE\_URL=https://integrate.api.nvidia.com/v1

NVIDIA\_MODEL=your\_model\_name

MONGODB\_URI=mongodb://localhost:27017/

MONGODB\_DATABASE=guardex\_db

```



Run the backend:

```bash

uvicorn api.app:app --reload

```

Backend runs at `http://127.0.0.1:8000`



\### Frontend Setup



```bash

cd frontend

npm install

```



Create `frontend/.env`:

```

VITE\_API\_BASE\_URL=http://127.0.0.1:8000/api/v1

```



Run the frontend:

```bash

npm run dev

```

Frontend runs at `http://localhost:5173`



\---



\## API Endpoints



| Method | Endpoint                  | Description                       |

|--------|----------------------------|------------------------------------|

| GET    | `/api/v1/health`           | Health check                       |

| POST   | `/api/v1/scan`             | Upload XML report \& run analysis   |

| GET    | `/api/v1/scans`            | Get all past scans                 |

| GET    | `/api/v1/scans/{scan\_id}`  | Get a specific scan                |

| DELETE | `/api/v1/scans/{scan\_id}`  | Delete a scan                      |

| POST   | `/api/v1/upload/xml`       | Upload and parse raw XML           |

| GET    | `/api/v1/stats`            | Knowledge base statistics          |



\---



\## License



This project is for educational purposes as part of a college project.



\## Contributors



\- TrishaChetan

