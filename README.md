# 🤖 Internship Agent

**Automated internship discovery and cover-letter generation using local LLM + Python automation.**

> Build and deploy a production-grade job search agent that discovers opportunities and writes tailored cover letters—all running locally on your machine. No APIs required (except optional SerpApi).

---

## ✨ What This Does

1. **Discovers** internship listings from:
   - [SimplifyJobs](https://github.com/SimplifyJobs/Summer2026-Internships) (updated daily, 500+ real listings)
   - Google Search via [SerpApi](https://serpapi.com) (optional, configurable keywords)

2. **Filters** by your custom keywords (e.g., "supply chain", "logistics", "operations")

3. **Generates** personalized cover letters using [Ollama](https://ollama.ai) (free, runs locally—no paid LLM API)

4. **Logs everything** to Google Sheets (auto-creates spreadsheet if needed)

5. **Serves** a beautiful dashboard at `http://localhost:5000` to review output

---

## 🏗️ Architecture

```
agent.py (Core Pipeline)
├── 1. Fetch listings
│  ├── fetch_from_simplify() → SimplifyJobs GitHub
│  └── search_serpapi()      → Google + internlist.org
├── 2. Filter & deduplicate
│  └── Match your keywords, skip duplicates
├── 3. Generate cover letters
│  └── Ollama + llama3 model (local, no API costs)
├── 4. Save locally
│  └── ~/Desktop/internship_agent/cover_letters/
└── 5. Log to Google Sheets (optional)
     └── Auto-create "2026 Career Tracker" sheet

dashboard.py (Web UI)
├── Flask backend
└── React-like frontend (vanilla JS)
    ├── Dashboard (stats, recent activity)
    ├── Discovered (browse found jobs)
    ├── Cover Letters (read all generated letters)
    └── Agent Log (full audit trail)
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.9+**
- **Ollama** (free, local LLM runtime)
- **pip / venv**

### 1. Clone & Install

```bash
git clone https://github.com/mjt622006/internship-agent.git
cd internship-agent
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Install Ollama & Download Model

```bash
# macOS / Linux
brew install ollama
ollama pull llama3
ollama serve  # Start the Ollama service (keep running in background)

# Or manually download from https://ollama.ai
```

### 3. Configure Your Profile

```bash
cp .env.example .env
```

Edit `.env` with your info:
```env
AGENT_NAME=Your Name
AGENT_SCHOOL=Your University
AGENT_GRADE=Junior
AGENT_EMAIL=you@university.edu
AGENT_PHONE=555-123-4567
SERPAPI_KEY=<optional—get free key at serpapi.com>
```

### 4. (Optional) Set Up Google Sheets

- Create a [Google Cloud Service Account](https://cloud.google.com/docs/authentication/getting-started) with Sheets + Drive API enabled
- Download the JSON key and save as `google_credentials.json` in this directory (already git-ignored)
- *Without this, the agent works fine but won't auto-log to Google Sheets*

### 5. Run It

```bash
# Option A: Command-line only
python3 agent.py

# Option B: Web dashboard (recommended)
python3 dashboard.py
# Then open http://localhost:5000 in your browser
```

---

## 📊 Dashboard Features

| Feature | Purpose |
|---------|---------|
| **Dashboard** | Quick stats: cover letters generated, internships discovered, last run time |
| **Discovered** | Browse all found internships (company, role, location, apply link) |
| **Cover Letters** | Click to expand and read each generated letter |
| **Agent Log** | Full audit trail of every action (timestamp, status, errors) |

**Run Agent Button** — Trigger a full pipeline run from the UI (takes 10–20 min depending on volume).

---

## ⚙️ Configuration

Edit these settings in `agent.py`:

```python
# Your search queries
SEARCH_QUERIES = [
    "supply chain intern 2026 Texas site:internlist.org",
    "logistics intern 2026 DFW site:internlist.org",
    "procurement intern summer 2026 Texas",
]

# Only include listings with these keywords
SIMPLIFY_KEYWORDS = [
    "supply chain", "procurement", "logistics",
    "operations", "warehouse", "inventory",
]

# LLM to use (llama3 is recommended; try phi, mistral if it's slow)
AI_MODEL = "llama3:latest"
```

---

## 📁 Project Structure

```
internship-agent/
├── agent.py                      # Core automation pipeline
├── dashboard.py                  # Flask web UI
├── check_locations.py            # Debug script to test SimplifyJobs
├── requirements.txt              # Python dependencies
├── .env.example                  # Template for secrets
├── .gitignore                    # Excludes secrets, generated files
└── cover_letters/                # Generated letters (auto-created)
    └── Company_Role_Date.txt
```

### Generated Files (Gitignored)
- `~/Desktop/internship_agent/cover_letters/` — All generated cover letters
- `~/Desktop/internship_agent/discovered_internships.json` — Cache of found jobs
- `~/Desktop/internship_agent/agent_log.txt` — Full execution log
- `google_credentials.json` — Service account key (never commit!)

---

## 🛠️ How It Works

### Discovery Pipeline

**SimplifyJobs** (Primary):
```
1. Fetch listings.json from SimplifyJobs repo (updated daily)
2. Filter by keyword (e.g., "supply chain")
3. Deduplicate against previous runs
4. Extract company, role, location, url
```

**SerpApi** (Secondary, optional):
```
1. Search Google/internlist.org using your queries
2. Parse results with local LLM to extract job details
3. Deduplicate, save to file
```

### Cover Letter Generation

For each discovered internship:
```
1. Read your resume (PDF) or fall back to .env details
2. Build prompt: "Write a cover letter for X role at Y company..."
3. Send to local Ollama (llama3 model)
4. Save as .txt file with metadata header
5. Optionally log to Google Sheets
```

---

## 📈 Performance & Costs

| Component | Cost | Performance |
|-----------|------|-------------|
| **SimplifyJobs** | Free ✅ | 1-2 sec to fetch 500+ listings |
| **Ollama (local)** | Free ✅ | ~30 sec per cover letter (M-series Mac/GPU: 5-10 sec) |
| **SerpApi** | Optional | $0–$20/mo depending on usage |
| **Google Sheets API** | Free ✅ | ~1 sec per row logged |

**Total cost to run agent:** $0 (unless you add SerpApi)

---

## 🔍 What Recruiters See

This project demonstrates:

- **Automation & DevOps** — Orchestrating multiple APIs, error handling, logging
- **Full-Stack** — Backend (Python, Flask), frontend (HTML/CSS/JS), data persistence
- **LLM Integration** — Using local models for production tasks (cost-efficient alternative to APIs)
- **Practical Problem-Solving** — Solves a real student pain point with open-source tools
- **Clean Code** — Well-organized, documented, handles edge cases

---

## 🐛 Troubleshooting

| Error | Fix |
|-------|-----|
| `❌ Ollama isn't running!` | Run `ollama serve` in a new terminal; keep it running in background |
| `❌ Model 'llama3:latest' not found` | Run `ollama pull llama3` |
| `⚠️ No credentials file found` | Google Sheets is optional—agent works without it. Skip if not needed. |
| `❌ pdfplumber not installed` | PDF reading is optional. Agent falls back to `.env` details. |
| `⚠️ SerpApi key not set` | SerpApi is optional. SimplifyJobs alone discovers plenty of jobs. |

---

## 📚 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Core** | Python 3.9+, Ollama (local LLM) |
| **APIs** | urllib, gspread, Google Sheets API, SerpApi |
| **Frontend** | Flask, vanilla HTML/CSS/JS |
| **Data** | JSON (in-memory), Google Sheets |

---

## 🤝 Contributing

Found a bug or want to improve it? Feel free to fork or submit issues!

---

## 📝 License

MIT — Use freely, modify, share.

---

## 🎯 Next Steps

- [ ] Set up `.env` with your info
- [ ] Install Ollama and pull `llama3`
- [ ] Run `python3 agent.py` to test
- [ ] Open `http://localhost:5000` to see the dashboard
- [ ] Review generated cover letters before sending
- [ ] Share with classmates looking to automate their job search!

---

**Happy job hunting! 🚀**

*Built as a portfolio project to showcase automation, full-stack development, and practical AI integration.*
