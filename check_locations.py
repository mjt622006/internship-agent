import urllib.request
import json

url = "https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/dev/.github/scripts/listings.json"

req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

with urllib.request.urlopen(req, timeout=15) as r:
    data = json.loads(r.read().decode())

keywords = [
    "supply chain",
    "procurement",
    "logistics",
    "operations",
    "warehouse",
    "inventory",
]

for listing in data[:500]:
    title = listing.get("title", "").lower()
    if any(k in title for k in keywords):
        print(listing.get("company_name"), "|", listing.get("locations"))
