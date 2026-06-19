# Internship Agent

Automated internship discovery and cover-letter generation pipeline. Pulls listings from [SimplifyJobs/Summer2026-Internships](https://github.com/SimplifyJobs/Summer2026-Internships) and (optionally) SerpApi, filters by keyword relevance, generates tailored cover letters with a local LLM (via [Ollama](https://ollama.com)), and logs everything to a Google Sheet. Includes a Flask dashboard for monitoring.

## Components

| File | Purpose |
|---|---|
| `agent.py` | Core pipeline: discovery → filtering → cover letter generation → Google Sheets logging |
| `dashboard.py` | Local Flask web UI to trigger runs and review output |
| `check_locations.py` | Standalone script to spot-check SimplifyJobs listings by keyword |

## Setup

1. **Clone and install dependencies**
   ```bash
   git clone https://github.com/<your-username>/internship-agent.git
   cd internship-agent
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Install and run Ollama** (for local cover letter generation)
   ```bash
   brew install ollama
   ollama pull llama3
   brew services start ollama
   ```

3. **Configure secrets**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your SerpApi key (optional — get one at [serpapi.com](https://serpapi.com)) and personal info.

4. **Google Sheets (optional)**
   - Create a Google Cloud service account with Sheets + Drive API access.
   - Download the JSON key and save it as `google_credentials.json` in this directory (already gitignored).

5. **Resume**
   - Place your resume as `resume.pdf` in this directory, or rely on the `.env` fields as fallback.

## Usage

```bash
python3 agent.py        # run the full pipeline
python3 dashboard.py    # then open http://localhost:5000
```

## Notes

- All secrets are loaded from `.env` — never commit this file.
- `cover_letters/`, `discovered_internships.json`, and `agent_log.txt` are generated locally and gitignored.
- Cover letters are AI-generated and should be reviewed before sending.
