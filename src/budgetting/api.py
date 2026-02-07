from pathlib import Path
from fastapi import FastAPI, Body
from fastapi.responses import HTMLResponse

from .db import (
    get_db_path,
    connect,
    init_db,
    fetch_transactions,
    fetch_uncategorized,
    fetch_categories,
    add_user_rule,
    apply_rules,
    update_transaction_category,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
app = FastAPI(title="Budgetting API")


def get_conn():
    """Helper functie: maakt database connectie en initialiseert tabellen"""
    conn = connect(get_db_path(PROJECT_ROOT))
    init_db(conn)
    return conn


# ========== API ENDPOINTS ==========

@app.get("/transactions")
def transactions(profile_id: int = 1, limit: int = 50):
    """Haal alle transacties op voor een profiel"""
    conn = get_conn()
    rows = fetch_transactions(conn, profile_id=profile_id, limit=limit)
    conn.close()
    return rows


@app.get("/transactions/uncategorized")
def uncategorized(profile_id: int = 1, limit: int = 50):
    """Haal alleen uncategorized transacties op (de inbox)"""
    conn = get_conn()
    rows = fetch_uncategorized(conn, profile_id=profile_id, limit=limit)
    conn.close()
    return rows


@app.get("/categories")
def categories(profile_id: int = 1):
    """Haal alle beschikbare categorieën op (uit rules)"""
    conn = get_conn()
    cats = fetch_categories(conn, profile_id=profile_id)
    conn.close()
    return cats


@app.post("/rules")
def create_rule(profile_id: int = 1, keyword: str = "", category: str = ""):
    """Maak een nieuwe rule aan: keyword → category"""
    if not keyword or not category:
        return {"error": "keyword and category are required"}

    conn = get_conn()
    add_user_rule(conn, profile_id=profile_id, keyword=keyword, category=category)
    conn.close()
    return {"status": "rule added", "profile_id": profile_id, "keyword": keyword, "category": category}


@app.post("/apply-rules")
def run_rules(profile_id: int = 1):
    """Pas alle rules toe op uncategorized transacties"""
    conn = get_conn()
    apply_rules(conn, profile_id=profile_id)
    conn.close()
    return {"status": "rules applied", "profile_id": profile_id}


@app.post("/transaction/{transaction_id}/set-category")
def set_category(transaction_id: int, payload: dict = Body(...)):
    """Update de categorie van één specifieke transactie"""
    category = payload.get("category")
    if not category:
        return {"error": "category is required"}

    conn = get_conn()
    update_transaction_category(conn, transaction_id, category)
    conn.close()
    return {"status": "ok", "transaction_id": transaction_id, "category": category}


# ========== UI (HTML) ==========

@app.get("/", response_class=HTMLResponse)
def home():
    """Serve de UI als HTML page"""
    return """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Budget Inbox</title>
  <style>
    body { 
      font-family: Arial, sans-serif; 
      margin: 24px; 
      max-width: 900px; 
    }
    h1 { 
      margin-bottom: 8px; 
    }
    .row { 
      display: grid; 
      grid-template-columns: 90px 1fr 120px 220px 120px; 
      gap: 10px;
      align-items: center; 
      padding: 10px; 
      border: 1px solid #ddd; 
      border-radius: 10px; 
      margin: 10px 0; 
    }
    .muted { 
      color: #666; 
      font-size: 12px; 
    }
    .desc { 
      white-space: nowrap; 
      overflow: hidden; 
      text-overflow: ellipsis; 
    }
    input, select, button { 
      padding: 8px; 
    }
    button { 
      cursor: pointer; 
    }
    .top { 
      display: flex; 
      gap: 12px; 
      align-items: center; 
      margin-bottom: 18px; 
    }
  </style>
</head>
<body>
  <h1>Uncategorized Inbox</h1>
  <div class="muted">Kies categorie per transactie. Optioneel: vul keyword in om meteen een rule aan te maken.</div>

  <div class="top">
    <button onclick="loadAll()">Refresh</button>
    <button onclick="applyRules()">Apply rules</button>
    <div class="muted" id="status"></div>
  </div>

  <div id="list"></div>

<script>
// ========== HELPER FUNCTIES ==========

async function fetchJSON(url, opts) {
  // Doet een fetch en parst het antwoord als JSON
  const res = await fetch(url, opts);
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(txt || res.statusText);
  }
  return await res.json();
}

function escapeHtml(str) {
  // Voorkomt XSS: maakt < > & " ' veilig voor HTML
  return String(str)
    .replaceAll("&","&amp;")
    .replaceAll("<","&lt;")
    .replaceAll(">","&gt;")
    .replaceAll('"',"&quot;")
    .replaceAll("'","&#039;");
}

// ========== MAIN FUNCTIES ==========

async function loadAll() {
  document.getElementById("status").textContent = "Loading...";
  
  // Haal tegelijk transacties EN categorieën op (Promise.all = parallel)
  const [tx, cats] = await Promise.all([
    fetchJSON("/transactions/uncategorized?profile_id=1&limit=200"),
    fetchJSON("/categories?profile_id=1")
  ]);

  const list = document.getElementById("list");
  list.innerHTML = "";

  if (tx.length === 0) {
    list.innerHTML = "<p>✅ Inbox is leeg.</p>";
    document.getElementById("status").textContent = "";
    return;
  }

  // Loop door elke transactie en maak een HTML row
  tx.forEach(t => {
    // Backend geeft arrays terug: [id, profile_id, date, description, amount, category]
    const [id, profile_id, date, description, amount, category] = t;

    const row = document.createElement("div");
    row.className = "row";

    row.innerHTML = `
      <div class="muted">#${id}</div>
      <div class="desc" title="${escapeHtml(description)}">${escapeHtml(description)}</div>
      <div style="text-align:right">€${Number(amount).toFixed(2)}</div>

      <div>
        <select id="cat-${id}">
          ${cats.map(c => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join("")}
        </select>
        <div class="muted">keyword (optional):</div>
        <input id="kw-${id}" placeholder="bijv: odido" />
      </div>

      <div>
        <button onclick="save(${id})">Save</button>
      </div>
    `;

    list.appendChild(row);
    
    // Zet de huidige category als selected in de dropdown
    const sel = document.getElementById(`cat-${id}`);
    sel.value = category || "Uncategorized";
  });

  document.getElementById("status").textContent = `Loaded ${tx.length} items`;
}

async function save(id) {
  // 1) Haal de gekozen waarden op uit de HTML inputs
  const category = document.getElementById(`cat-${id}`).value;
  const keyword = document.getElementById(`kw-${id}`).value.trim();

  // 2) Update de transactie met de nieuwe categorie
  await fetchJSON(`/transaction/${id}/set-category`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({category})
  });

  // 3) Als er een keyword is ingevuld: maak een rule aan
  if (keyword.length > 0) {
    const params = new URLSearchParams({
      profile_id: 1,
      keyword: keyword, 
      category: category
    });
    await fetchJSON(`/rules?` + params.toString(), { method: "POST" });
  }

  // 4) Refresh de lijst (de transactie verdwijnt nu uit de inbox)
  await loadAll();
}

async function applyRules() {
  // Pas alle bestaande rules toe op de inbox
  await fetchJSON("/apply-rules?profile_id=1", { method: "POST" });
  await loadAll();
}

// ========== START ==========
// Laad de inbox zodra de pagina geladen is
loadAll();
</script>
</body>
</html>
"""