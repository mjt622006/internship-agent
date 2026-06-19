"""
==================================================
  INTERNSHIP AGENT v4
  MacBook Air M2/M3 | Free | Auto Google Sheet
  + PDF Resume Reading
  + SimplifyJobs GitHub (updated daily)
  + internlist.org via SerpApi
==================================================
"""

import ollama
import os
import datetime
import time
import json
import re
import urllib.request
import gspread
from google.oauth2.service_account import Credentials

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# PDF reading
try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# SerpApi searching
try:
    from serpapi import GoogleSearch
    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False


# ==================================================
# ✏️  STEP A — YOUR INFO
# ==================================================

MY_INFO = {
    "name":       os.getenv("AGENT_NAME", "Your Name"),
    "school":     os.getenv("AGENT_SCHOOL", "Your School"),
    "grade":      os.getenv("AGENT_GRADE", "Your Year"),
    "email":      os.getenv("AGENT_EMAIL", "you@example.com"),
    "phone":      os.getenv("AGENT_PHONE", "000-000-0000"),
    "skills": [
        "Supply chain management",
        "Logistics",
        "Microsoft Office",
        "Leadership",
        "Team collaboration",
    ],
    "activities": [
        "Vice President, National Society of Black Engineers (NSBE)",
        "Student Athlete, Football and Track and Field",
        "Musician, Drummer at Dwelling Place Worship Center",
    ],
}

# ==================================================
# ✏️  STEP B — YOUR RESUME PDF
# ==================================================

RESUME_FILENAME = "resume.pdf"

# ==================================================
# ✏️  STEP C — YOUR KNOWN INTERNSHIPS
# ==================================================

INTERNSHIPS = []

# ==================================================
# ✏️  STEP D — API KEYS
# ==================================================

SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")   # set in .env — see .env.example

# ==================================================
# ✏️  STEP E — SEARCH SETTINGS
# ==================================================

# What to search for on internlist.org and via SerpApi:
SEARCH_QUERIES = [
    "supply chain intern 2026 Texas site:internlist.org",
    "logistics intern 2026 DFW site:internlist.org",
    "procurement intern summer 2026 Texas",
    "operations intern 2026 Dallas Fort Worth",
]

RESULTS_PER_QUERY = 3
DISCOVERED_FILE   = "discovered_internships.json"

# Keywords to filter SimplifyJobs listings by
# (only internships matching these will be added)
SIMPLIFY_KEYWORDS = [
    "supply chain", "procurement", "logistics",
    "operations", "warehouse", "inventory",
]

# ==================================================
# ⚙️  SETTINGS
# ==================================================

AI_MODEL      = "llama3:latest"
OUTPUT_FOLDER = os.path.expanduser("~/Desktop/internship_agent/cover_letters")
LOG_FILE      = os.path.expanduser("~/Desktop/internship_agent/agent_log.txt")
CREDENTIALS_FILE = "google_credentials.json"

# The agent will AUTO-CREATE this sheet in your Google Drive
# You don't need to create it manually
NEW_SHEET_NAME = "2026 Personal Growth & Career Tracker"
SHEET_TAB_NAME = "Internships"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_HEADERS = [
    "Date", "Company", "Role", "Location",
    "Deadline", "Status", "Cover Letter File", "Source", "Notes",
]

# SimplifyJobs GitHub — updated daily with real internship listings
SIMPLIFY_URL = (
    "https://raw.githubusercontent.com/SimplifyJobs/"
    "Summer2026-Internships/dev/.github/scripts/listings.json"
)


# ==================================================
# 🔧  HELPERS
# ==================================================

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full = f"[{timestamp}] {message}"
    print(full)
    with open(LOG_FILE, "a") as f:
        f.write(full + "\n")


def setup_folders():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        log(f"📁 Created folder: {OUTPUT_FOLDER}/")


def check_ai_running():
    try:
        models = ollama.list()
        names = [m.model for m in models.models]
        if not any(AI_MODEL in n for n in names):
            print(f"\n❌ Model '{AI_MODEL}' not found! Run: ollama pull llama3\n")
            return False
        return True
    except Exception:
        print("\n❌ Ollama isn't running! Run: brew services start ollama\n")
        return False


def load_discovered():
    path = os.path.expanduser(f"~/Desktop/internship_agent/{DISCOVERED_FILE}")
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_discovered(internships):
    path = os.path.expanduser(f"~/Desktop/internship_agent/{DISCOVERED_FILE}")
    with open(path, "w") as f:
        json.dump(internships, f, indent=2)


# ==================================================
# 📄  RESUME READING
# ==================================================

def read_resume():
    resume_path = os.path.expanduser(
        f"~/Desktop/internship_agent/{RESUME_FILENAME}"
    )
    if not PDF_AVAILABLE:
        log("⚠️  pdfplumber not installed — using MY_INFO")
        return None
    if not os.path.exists(resume_path):
        log(f"⚠️  Resume PDF not found — using MY_INFO")
        return None
    try:
        text = ""
        with pdfplumber.open(resume_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            log(f"✅ Resume loaded ({len(text)} characters)")
            return text.strip()
        log("⚠️  Resume appears empty — using MY_INFO")
        return None
    except Exception as e:
        log(f"⚠️  Resume read error: {e} — using MY_INFO")
        return None


def build_resume_from_info():
    skills     = "\n".join(f"- {s}" for s in MY_INFO["skills"])
    activities = "\n".join(f"- {a}" for a in MY_INFO["activities"])
    return f"""
Name: {MY_INFO['name']}
School: {MY_INFO['school']}
Year: {MY_INFO['grade']}
Email: {MY_INFO['email']}
Phone: {MY_INFO['phone']}
Skills:\n{skills}
Activities:\n{activities}
"""


# ==================================================
# 🔍  INTERNSHIP DISCOVERY
# ==================================================

def fetch_from_simplify():
    """
    Pulls internship listings from the SimplifyJobs GitHub repo.
    This repo is maintained daily by the Pitt CS Club and has
    hundreds of real, verified internship listings.
    Filters by your SIMPLIFY_KEYWORDS so you only get relevant ones.
    """
    log("📦 Fetching listings from SimplifyJobs GitHub (updated daily)...")
    try:
        req = urllib.request.Request(
            SIMPLIFY_URL,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())

        previously_found = load_discovered()
        known_companies  = {i["company"].lower() for i in INTERNSHIPS}
        known_companies |= {i["company"].lower() for i in previously_found}

        new_found = []
        for listing in data:
            # Skip closed listings
            if not listing.get("active", True):
                continue

            title    = listing.get("title", "")
            company  = listing.get("company_name", "")
            location = listing.get("locations", ["Remote"])
            url      = listing.get("url", "")

            # Handle location — can be a list
            if isinstance(location, list):
                location = location[0] if location else "Remote"

            # Only include listings matching your keywords
            title_lower = title.lower()
            if not any(kw in title_lower for kw in SIMPLIFY_KEYWORDS):
                continue

            # Skip duplicates
            if company.lower() in known_companies:
                continue


            new_found.append({
                "company":     company,
                "role":        title,
                "location":    location,
                "deadline":    "Rolling",
                "description": f"Role: {title} at {company}. Apply via the company's official career portal.",
                "url":         url,
                "source":      "SimplifyJobs",
            })

            known_companies.add(company.lower())

            if len(new_found) >= 25:  # cap at 10 new per run
                break

        log(f"   ✅ {len(new_found)} new listing(s) from SimplifyJobs")
        return new_found

    except Exception as e:
        log(f"   ⚠️  SimplifyJobs fetch failed: {e}")
        return []


def search_serpapi():
    """
    Searches internlist.org and Google for supply chain/logistics
    internships using SerpApi.
    """
    if not SEARCH_AVAILABLE:
        log("⚠️  serpapi not installed — skipping SerpApi search")
        return []

    if not SERPAPI_KEY:
        log("⚠️  SerpApi key not set — skipping SerpApi search")
        return []

    log("🔍 Searching internlist.org and Google via SerpApi...")

    previously_found = load_discovered()
    known_urls       = {i.get("url", "") for i in previously_found}
    known_companies  = {i["company"].lower() for i in INTERNSHIPS}
    known_companies |= {i["company"].lower() for i in previously_found}

    all_results = []

    for query in SEARCH_QUERIES:
        log(f"   Searching: {query}")
        try:
            search  = GoogleSearch({"q": query, "num": RESULTS_PER_QUERY, "api_key": SERPAPI_KEY})
            results = search.get_dict().get("organic_results", [])
            for r in results:
                url = r.get("link", "")
                if url and url not in known_urls:
                    all_results.append({
                        "url":     url,
                        "title":   r.get("title", ""),
                        "snippet": r.get("snippet", ""),
                    })
                    known_urls.add(url)
            time.sleep(1)
        except Exception as e:
            log(f"   ⚠️  Search error: {e}")

    if not all_results:
        log("   No new results found")
        return []

    log(f"   Found {len(all_results)} result(s) — extracting details with AI...")

    new_internships = []
    for result in all_results[:8]:
        try:
            prompt = f"""
Internship search result:
Title:   {result['title']}
Snippet: {result['snippet']}
URL:     {result['url']}

Is this an internship listing? If yes, extract and respond ONLY in this JSON:
{{
  "company": "Company Name",
  "role": "Job Title",
  "location": "City, State or Remote",
  "deadline": "Rolling",
  "description": "2-3 sentences about the role",
  "url": "{result['url']}",
  "source": "SerpApi"
}}
If NOT an internship, respond with exactly: {{"skip": true}}
"""
            response = ollama.chat(
                model=AI_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            text = response["message"]["content"].strip()
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            data = json.loads(text.strip())

            if data.get("skip"):
                continue

            company = data.get("company", "").lower()
            if company and company not in known_companies:
                new_internships.append(data)
                known_companies.add(company)
                log(f"   ✅ Found: {data['role']} at {data['company']}")

        except Exception as e:
            log(f"   ⚠️  Parse error: {e}")
            continue

    log(f"   ✅ {len(new_internships)} new listing(s) from SerpApi")
    return new_internships


def discover_internships():
    """Runs both discovery methods and combines results."""
    previously_found = load_discovered()

    simplify_results = fetch_from_simplify()
    serpapi_results  = search_serpapi()

    all_new = simplify_results + serpapi_results

    # Save for next run
    save_discovered(previously_found + all_new)

    log(f"🔍 Total new internships found: {len(all_new)}")
    return all_new


# ==================================================
# ✍️  COVER LETTERS
# ==================================================

def build_prompt(internship, resume_text):
    return f"""
You are helping a college student write a professional internship cover letter.
Be confident, genuine, and enthusiastic. No clichés.
Keep it under 300 words. 3 short paragraphs. Real cover letter format.

=== STUDENT RESUME ===
{resume_text}

=== INTERNSHIP ===
Company:  {internship['company']}
Role:     {internship['role']}
Location: {internship['location']}
Details:  {internship['description']}

=== INSTRUCTIONS ===
- Paragraph 1: Open with something SPECIFIC about this company or role. No "I am writing to..."
- Paragraph 2: Connect 2-3 real things from the resume to what the role needs.
- Paragraph 3: Warm, confident close. Include email and phone.
- Sound like a real person. Don't invent anything not in the resume.
"""


def generate_cover_letter(internship, resume_text):
    log(f"✍️  Writing: {internship['role']} at {internship['company']}...")
    try:
        response = ollama.chat(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": "You are a career counselor helping a college student write internship cover letters. Be genuine, specific, and concise."},
                {"role": "user",   "content": build_prompt(internship, resume_text)}
            ]
        )
        return response["message"]["content"]
    except Exception as e:
        log(f"❌ AI error: {e}")
        return None


def save_cover_letter(internship, letter_text):
    date_str     = datetime.datetime.now().strftime("%Y-%m-%d")
    safe_company = re.sub(r'[^\w]', '_', internship["company"])[:30]
    safe_role    = re.sub(r'[^\w]', '_', internship["role"].split("(")[0].strip())[:30]
    filename     = f"{safe_company}_{safe_role}_{date_str}.txt"
    filepath     = os.path.join(OUTPUT_FOLDER, filename)

    with open(filepath, "w") as f:
        f.write(f"COVER LETTER\n")
        f.write(f"Company:   {internship['company']}\n")
        f.write(f"Role:      {internship['role']}\n")
        f.write(f"Location:  {internship['location']}\n")
        f.write(f"Deadline:  {internship['deadline']}\n")
        f.write(f"Source:    {internship.get('url', 'Manual')}\n")
        f.write(f"Generated: {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n")
        f.write("=" * 60 + "\n\n")
        f.write(letter_text)
        f.write("\n\n" + "=" * 60 + "\n")
        f.write("⚠️  REVIEW BEFORE SENDING — AI can make mistakes!\n")

    log(f"💾 Saved: {filename}")
    return filename


# ==================================================
# 📊  GOOGLE SHEETS — AUTO-CREATE
# ==================================================

def setup_google_sheets():
    """
    Connects to Google Sheets and AUTO-CREATES the spreadsheet
    if it doesn't exist yet. No manual setup needed.
    """
    base       = os.path.expanduser("~/Desktop/internship_agent/")
    creds_path = os.path.join(base, CREDENTIALS_FILE)

    if not os.path.exists(creds_path):
        log(f"⚠️  No credentials file found — skipping Google Sheets")
        return None, None

    try:
        creds  = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
        client = gspread.authorize(creds)

        # Try to open existing sheet first
        try:
            sheet = client.open(NEW_SHEET_NAME)
            log(f"✅ Found existing sheet: '{NEW_SHEET_NAME}'")
        except gspread.exceptions.SpreadsheetNotFound:
            # Create it from scratch — no manual work needed!
            sheet = client.create(NEW_SHEET_NAME)
            log(f"✅ Created new Google Sheet: '{NEW_SHEET_NAME}'")

            # Share it with yourself so you can actually see it
            # Get your email from the credentials file
            with open(creds_path) as f:
                cred_data = json.load(f)
            service_email = cred_data.get("client_email", "")
            log(f"   Service account: {service_email}")
            log(f"   ⚠️  Open Google Drive to find '{NEW_SHEET_NAME}' — it was shared with your service account.")
            log(f"   To see it yourself, open the sheet URL from Google Drive.")

        # Get or create the Applications tab
        try:
            worksheet = sheet.worksheet(SHEET_TAB_NAME)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title=SHEET_TAB_NAME, rows=1000, cols=10)
            log(f"📋 Created tab: '{SHEET_TAB_NAME}'")

        # Add headers if empty
        existing = worksheet.get_all_values()
        if not existing or existing[0] != SHEET_HEADERS:
            worksheet.clear()
            worksheet.insert_row(SHEET_HEADERS, 1)
            # Format header row bold
            worksheet.format("A1:I1", {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.2, "green": 0.6, "blue": 0.9}
            })
            log("📋 Added headers to sheet")

        # Return both the client and worksheet
        return client, worksheet

    except Exception as e:
        log(f"⚠️  Google Sheets error: {e}")
        return None, None


def log_to_sheets(worksheet, internship, filename):
    try:
        today = datetime.datetime.now().strftime("%B %d, %Y")
        worksheet.append_row([
            internship["company"],
            internship["role"],
            internship["deadline"],
            "No",
            "Cover Letter Ready",
            internship.get("url", ""),
        ])
        log(f"📊 Logged: {internship['company']}")
    except Exception as e:
        log(f"⚠️  Sheets log failed: {e}")


def print_sheet_url(client):
    """Prints the URL of your Google Sheet so you can open it."""
    try:
        sheet = client.open(NEW_SHEET_NAME)
        url   = f"https://docs.google.com/spreadsheets/d/{sheet.id}"
        log(f"📊 Your Google Sheet: {url}")
    except Exception:
        pass


# ==================================================
# 🚀  MAIN
# ==================================================

def run_agent():
    print("\n" + "=" * 60)
    print("  🤖 INTERNSHIP AGENT v4 — Starting Up")
    print("=" * 60 + "\n")

    setup_folders()

    if not check_ai_running():
        return

    # Load resume
    resume_text = read_resume() or build_resume_from_info()

    # Set up Google Sheets (auto-creates if needed)
    client, worksheet = setup_google_sheets()
    if not worksheet:
        print("⚠️  Running without Google Sheets.\n")

    # Discover new internships
    new_internships = discover_internships()

    # Combine all internships
    all_internships = INTERNSHIPS + new_internships
    log(f"🚀 Processing {len(all_internships)} internship(s) "
        f"({len(INTERNSHIPS)} manual + {len(new_internships)} discovered)")

    success = 0
    failed  = 0

    for i, job in enumerate(all_internships, 1):
        print(f"\n--- [{i}/{len(all_internships)}] {job['company']} — {job['role']} ---")

        letter = generate_cover_letter(job, resume_text)

        if letter:
            filename = save_cover_letter(job, letter)
            success += 1
            if worksheet:
                log_to_sheets(worksheet, job, filename)
        else:
            failed += 1

        if i < len(all_internships):
            time.sleep(3)

    print("\n" + "=" * 60)
    log(f"✅ Done! {success} letter(s) saved, {failed} failed.")
    log(f"📁 Cover letters: {OUTPUT_FOLDER}")
    if client:
        print_sheet_url(client)
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_agent()
