"""
==================================================
  INTERNSHIP AGENT — Web Dashboard
  Run: python3 dashboard.py
  Then open: http://localhost:5000
==================================================
"""

from flask import Flask, render_template_string, jsonify, request
import os, json, subprocess, datetime, glob

app = Flask(__name__)

BASE = os.path.expanduser("~/Desktop/internship_agent")
COVER_LETTERS_DIR = os.path.join(BASE, "cover_letters")
DISCOVERED_FILE   = os.path.join(BASE, "discovered_internships.json")
LOG_FILE          = os.path.join(BASE, "agent_log.txt")

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Internship Agent</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
<style>
  :root {
    --bg:      #0D0F14;
    --surface: #13161E;
    --card:    #1A1E2A;
    --border:  #252A38;
    --gold:    #E8B84B;
    --gold2:   #F5D78E;
    --white:   #F0F2F8;
    --muted:   #6B7280;
    --green:   #34D399;
    --red:     #F87171;
    --blue:    #60A5FA;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--white);
    font-family: 'DM Mono', monospace;
    min-height: 100vh;
  }

  /* ── SIDEBAR ── */
  .layout { display: flex; min-height: 100vh; }

  .sidebar {
    width: 240px;
    background: var(--surface);
    border-right: 1px solid var(--border);
    padding: 32px 0;
    position: fixed;
    height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .logo {
    padding: 0 24px 32px;
    border-bottom: 1px solid var(--border);
  }

  .logo h1 {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 18px;
    color: var(--gold);
    letter-spacing: -0.5px;
    line-height: 1.2;
  }

  .logo p {
    font-size: 10px;
    color: var(--muted);
    margin-top: 4px;
    letter-spacing: 1px;
    text-transform: uppercase;
  }

  .nav { padding: 24px 0; flex: 1; }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 24px;
    cursor: pointer;
    color: var(--muted);
    font-size: 12px;
    letter-spacing: 0.5px;
    transition: all 0.2s;
    border-left: 2px solid transparent;
  }

  .nav-item:hover { color: var(--white); background: var(--card); }
  .nav-item.active { color: var(--gold); border-left-color: var(--gold); background: rgba(232,184,75,0.05); }
  .nav-icon { font-size: 16px; }

  .run-btn {
    margin: 0 16px 24px;
    padding: 14px;
    background: var(--gold);
    color: #0D0F14;
    border: none;
    border-radius: 8px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.5px;
    cursor: pointer;
    transition: all 0.2s;
    width: calc(100% - 32px);
  }

  .run-btn:hover { background: var(--gold2); transform: translateY(-1px); }
  .run-btn:active { transform: translateY(0); }
  .run-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

  /* ── MAIN ── */
  .main {
    margin-left: 240px;
    flex: 1;
    padding: 40px;
    max-width: calc(100vw - 240px);
  }

  .page { display: none; }
  .page.active { display: block; }

  .page-header {
    margin-bottom: 32px;
  }

  .page-header h2 {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 28px;
    color: var(--white);
    letter-spacing: -1px;
  }

  .page-header p {
    color: var(--muted);
    font-size: 12px;
    margin-top: 6px;
  }

  /* ── STATS ── */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 32px;
  }

  .stat-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    position: relative;
    overflow: hidden;
  }

  .stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--gold);
  }

  .stat-label {
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 8px;
  }

  .stat-value {
    font-family: 'Syne', sans-serif;
    font-size: 32px;
    font-weight: 800;
    color: var(--gold);
  }

  .stat-sub {
    font-size: 10px;
    color: var(--muted);
    margin-top: 4px;
  }

  /* ── CARDS ── */
  .card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
  }

  .card-title {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 14px;
    color: var(--white);
    margin-bottom: 16px;
    letter-spacing: 0.5px;
  }

  /* ── TABLE ── */
  .table-wrap { overflow-x: auto; }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
  }

  th {
    text-align: left;
    padding: 10px 16px;
    color: var(--muted);
    font-size: 10px;
    letter-spacing: 1px;
    text-transform: uppercase;
    border-bottom: 1px solid var(--border);
    font-weight: 500;
  }

  td {
    padding: 12px 16px;
    border-bottom: 1px solid rgba(37,42,56,0.5);
    color: var(--white);
    vertical-align: middle;
  }

  tr:hover td { background: rgba(232,184,75,0.03); }

  .badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.5px;
  }

  .badge-ready   { background: rgba(52,211,153,0.15); color: var(--green); }
  .badge-review  { background: rgba(232,184,75,0.15); color: var(--gold); }
  .badge-reject  { background: rgba(248,113,113,0.15); color: var(--red); }
  .badge-applied { background: rgba(96,165,250,0.15); color: var(--blue); }

  /* ── LOG ── */
  .log-box {
    background: #080A0F;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
    font-size: 11px;
    line-height: 1.8;
    max-height: 400px;
    overflow-y: auto;
    white-space: pre-wrap;
    color: #8B9BB4;
  }

  .log-box .log-success { color: var(--green); }
  .log-box .log-error   { color: var(--red); }
  .log-box .log-info    { color: var(--gold); }

  /* ── COVER LETTER VIEWER ── */
  .letter-list { list-style: none; }

  .letter-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
    cursor: pointer;
    transition: background 0.15s;
    border-radius: 6px;
  }

  .letter-item:hover { background: rgba(232,184,75,0.05); }

  .letter-name {
    font-size: 12px;
    color: var(--white);
  }

  .letter-date {
    font-size: 10px;
    color: var(--muted);
    margin-top: 2px;
  }

  .letter-content {
    display: none;
    background: #080A0F;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 24px;
    margin-top: 16px;
    font-size: 12px;
    line-height: 2;
    white-space: pre-wrap;
    color: #C0CAD8;
    max-height: 500px;
    overflow-y: auto;
  }

  /* ── STATUS SELECTOR ── */
  select {
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--white);
    padding: 4px 8px;
    border-radius: 6px;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    cursor: pointer;
  }

  /* ── RUNNING INDICATOR ── */
  .running-indicator {
    display: none;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    background: rgba(232,184,75,0.1);
    border: 1px solid rgba(232,184,75,0.3);
    border-radius: 8px;
    margin-bottom: 20px;
    font-size: 12px;
    color: var(--gold);
  }

  .running-indicator.show { display: flex; }

  .dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--gold);
    animation: pulse 1s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }

  /* ── EMPTY STATE ── */
  .empty {
    text-align: center;
    padding: 48px;
    color: var(--muted);
    font-size: 12px;
  }

  .empty span { font-size: 32px; display: block; margin-bottom: 12px; }

  /* ── SCROLLBAR ── */
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
</style>
</head>
<body>

<div class="layout">

  <!-- SIDEBAR -->
  <aside class="sidebar">
    <div class="logo">
      <h1>Internship<br>Agent</h1>
      <p>Internship Application Tracker</p>
    </div>

    <nav class="nav">
      <div class="nav-item active" onclick="showPage('dashboard')">
        <span class="nav-icon">⬛</span> Dashboard
      </div>
      <div class="nav-item" onclick="showPage('internships')">
        <span class="nav-icon">🔍</span> Discovered
      </div>
      <div class="nav-item" onclick="showPage('letters')">
        <span class="nav-icon">✉</span> Cover Letters
      </div>
      <div class="nav-item" onclick="showPage('log')">
        <span class="nav-icon">📋</span> Agent Log
      </div>
    </nav>

    <button class="run-btn" id="runBtn" onclick="runAgent()">
      ▶ RUN AGENT NOW
    </button>
  </aside>

  <!-- MAIN -->
  <main class="main">

    <div id="runningIndicator" class="running-indicator">
      <div class="dot"></div>
      Agent is running — this takes 10–20 minutes...
    </div>

    <!-- DASHBOARD -->
    <div id="page-dashboard" class="page active">
      <div class="page-header">
        <h2>Dashboard</h2>
        <p>Your internship hunt at a glance</p>
      </div>

      <div class="stats-grid" id="statsGrid">
        <div class="stat-card">
          <div class="stat-label">Cover Letters</div>
          <div class="stat-value" id="statLetters">—</div>
          <div class="stat-sub">Generated total</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Discovered</div>
          <div class="stat-value" id="statDiscovered">—</div>
          <div class="stat-sub">From SimplifyJobs + SerpApi</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Last Run</div>
          <div class="stat-value" style="font-size:18px;padding-top:8px" id="statLastRun">—</div>
          <div class="stat-sub">Agent activity</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Next Run</div>
          <div class="stat-value" style="font-size:18px;padding-top:8px">3:00 AM</div>
          <div class="stat-sub">Runs nightly</div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Recent Activity</div>
        <div id="recentActivity">
          <div class="empty"><span>📭</span>No activity yet</div>
        </div>
      </div>
    </div>

    <!-- DISCOVERED INTERNSHIPS -->
    <div id="page-internships" class="page">
      <div class="page-header">
        <h2>Discovered Internships</h2>
        <p>All internships found by the agent</p>
      </div>
      <div class="card">
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Company</th>
                <th>Role</th>
                <th>Location</th>
                <th>Source</th>
                <th>Link</th>
              </tr>
            </thead>
            <tbody id="internshipsTable">
              <tr><td colspan="5"><div class="empty"><span>🔍</span>No internships discovered yet</div></td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- COVER LETTERS -->
    <div id="page-letters" class="page">
      <div class="page-header">
        <h2>Cover Letters</h2>
        <p>Click any letter to read it</p>
      </div>
      <div class="card">
        <ul class="letter-list" id="letterList">
          <li><div class="empty"><span>✉</span>No cover letters yet</div></li>
        </ul>
      </div>
    </div>

    <!-- LOG -->
    <div id="page-log" class="page">
      <div class="page-header">
        <h2>Agent Log</h2>
        <p>Full history of agent activity</p>
      </div>
      <div class="card">
        <div class="log-box" id="logBox">Loading log...</div>
      </div>
    </div>

  </main>
</div>

<script>
// ── NAVIGATION ──────────────────────────────────────────────
function showPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('page-' + name).classList.add('active');
  event.currentTarget.classList.add('active');

  if (name === 'log') loadLog();
  if (name === 'letters') loadLetters();
  if (name === 'internships') loadInternships();
  if (name === 'dashboard') loadDashboard();
}

// ── DASHBOARD ───────────────────────────────────────────────
async function loadDashboard() {
  const res = await fetch('/api/stats');
  const data = await res.json();
  document.getElementById('statLetters').textContent = data.letters;
  document.getElementById('statDiscovered').textContent = data.discovered;
  document.getElementById('statLastRun').textContent = data.last_run || 'Never';

  const activity = document.getElementById('recentActivity');
  if (data.recent_log.length === 0) {
    activity.innerHTML = '<div class="empty"><span>📭</span>No activity yet</div>';
    return;
  }
  activity.innerHTML = '<div class="log-box">' +
    data.recent_log.map(line => {
      if (line.includes('✅') || line.includes('💾') || line.includes('📊'))
        return `<span class="log-success">${line}</span>`;
      if (line.includes('❌'))
        return `<span class="log-error">${line}</span>`;
      if (line.includes('🚀') || line.includes('🔍') || line.includes('✍'))
        return `<span class="log-info">${line}</span>`;
      return line;
    }).join('\\n') + '</div>';
}

// ── RUN AGENT ───────────────────────────────────────────────
async function runAgent() {
  const btn = document.getElementById('runBtn');
  const indicator = document.getElementById('runningIndicator');
  btn.disabled = true;
  btn.textContent = '⏳ RUNNING...';
  indicator.classList.add('show');

  try {
    const res = await fetch('/api/run', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      btn.textContent = '✅ DONE!';
      setTimeout(() => {
        btn.textContent = '▶ RUN AGENT NOW';
        btn.disabled = false;
        indicator.classList.remove('show');
        loadDashboard();
      }, 3000);
    } else {
      btn.textContent = '❌ ERROR';
      setTimeout(() => {
        btn.textContent = '▶ RUN AGENT NOW';
        btn.disabled = false;
        indicator.classList.remove('show');
      }, 3000);
    }
  } catch (e) {
    btn.textContent = '❌ ERROR';
    btn.disabled = false;
    indicator.classList.remove('show');
  }
}

// ── INTERNSHIPS ─────────────────────────────────────────────
async function loadInternships() {
  const res = await fetch('/api/internships');
  const data = await res.json();
  const tbody = document.getElementById('internshipsTable');

  if (data.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5"><div class="empty"><span>🔍</span>No internships discovered yet — run the agent first</div></td></tr>';
    return;
  }

  tbody.innerHTML = data.map(i => `
    <tr>
      <td><strong>${i.company}</strong></td>
      <td>${i.role}</td>
      <td>${i.location}</td>
      <td><span class="badge badge-ready">${i.source || 'SimplifyJobs'}</span></td>
      <td>${i.url ? `<a href="${i.url}" target="_blank" style="color:var(--gold);text-decoration:none;">Apply →</a>` : '—'}</td>
    </tr>
  `).join('');
}

// ── COVER LETTERS ────────────────────────────────────────────
async function loadLetters() {
  const res = await fetch('/api/letters');
  const data = await res.json();
  const list = document.getElementById('letterList');

  if (data.length === 0) {
    list.innerHTML = '<li><div class="empty"><span>✉</span>No cover letters yet</div></li>';
    return;
  }

  list.innerHTML = data.map((l, idx) => `
    <li>
      <div class="letter-item" onclick="toggleLetter(${idx})">
        <div>
          <div class="letter-name">${l.name}</div>
          <div class="letter-date">${l.date}</div>
        </div>
        <span style="color:var(--muted);font-size:18px" id="arrow-${idx}">›</span>
      </div>
      <div class="letter-content" id="letter-${idx}">${l.content}</div>
    </li>
  `).join('');
}

function toggleLetter(idx) {
  const content = document.getElementById('letter-' + idx);
  const arrow = document.getElementById('arrow-' + idx);
  const isOpen = content.style.display === 'block';
  content.style.display = isOpen ? 'none' : 'block';
  arrow.textContent = isOpen ? '›' : '⌄';
}

// ── LOG ──────────────────────────────────────────────────────
async function loadLog() {
  const res = await fetch('/api/log');
  const data = await res.json();
  const box = document.getElementById('logBox');
  box.innerHTML = data.log.map(line => {
    if (line.includes('✅') || line.includes('💾') || line.includes('📊'))
      return `<span class="log-success">${line}</span>`;
    if (line.includes('❌'))
      return `<span class="log-error">${line}</span>`;
    if (line.includes('🚀') || line.includes('🔍') || line.includes('✍'))
      return `<span class="log-info">${line}</span>`;
    return line;
  }).join('\\n');
  box.scrollTop = box.scrollHeight;
}

// ── INIT ─────────────────────────────────────────────────────
loadDashboard();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/stats")
def stats():
    # Count cover letters
    letters = len(glob.glob(os.path.join(COVER_LETTERS_DIR, "*.txt")))

    # Count discovered internships
    discovered = 0
    if os.path.exists(DISCOVERED_FILE):
        try:
            with open(DISCOVERED_FILE) as f:
                discovered = len(json.load(f))
        except:
            pass

    # Last run from log
    last_run = "Never"
    recent_log = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        recent_log = lines[-20:] if lines else []
        for line in reversed(lines):
            if "Starting Up" in line:
                try:
                    last_run = line.split("]")[0].replace("[", "").strip()
                    last_run = last_run.split(" ")[0]
                except:
                    pass
                break

    return jsonify({
        "letters": letters,
        "discovered": discovered,
        "last_run": last_run,
        "recent_log": recent_log
    })

@app.route("/api/run", methods=["POST"])
def run_agent():
    try:
        script = os.path.join(BASE, "agent.py")
        venv_python = os.path.join(BASE, "venv/bin/python3")
        subprocess.Popen(
            [venv_python, script],
            cwd=BASE,
            stdout=open(LOG_FILE, "a"),
            stderr=subprocess.STDOUT
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/internships")
def internships():
    if not os.path.exists(DISCOVERED_FILE):
        return jsonify([])
    try:
        with open(DISCOVERED_FILE) as f:
            data = json.load(f)
        return jsonify(data)
    except:
        return jsonify([])

@app.route("/api/letters")
def letters():
    files = sorted(
        glob.glob(os.path.join(COVER_LETTERS_DIR, "*.txt")),
        key=os.path.getmtime,
        reverse=True
    )
    result = []
    for filepath in files:
        filename = os.path.basename(filepath)
        mtime = os.path.getmtime(filepath)
        date = datetime.datetime.fromtimestamp(mtime).strftime("%B %d, %Y")
        try:
            with open(filepath) as f:
                content = f.read()
        except:
            content = "Could not read file."
        result.append({
            "name": filename.replace("_", " ").replace(".txt", ""),
            "date": date,
            "content": content
        })
    return jsonify(result)

@app.route("/api/log")
def log():
    if not os.path.exists(LOG_FILE):
        return jsonify({"log": ["No log file found yet."]})
    with open(LOG_FILE) as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    return jsonify({"log": lines[-200:]})

if __name__ == "__main__":
    print("\n✅ Dashboard running at: http://localhost:5000")
    print("   Press Control+C to stop\n")
    app.run(debug=False, port=5000)
