PROJECT CONTEXT CHECKPOINT

Project: Python budget app
Stack: Python, pandas, SQLite, VS Code, venv

Structuur:
- src/budgetting/
  - ingest.py (CSV → pandas → SQLite)
  - db.py (transactions + rules tables)
  - show_inbox.py (laat uncategorized transacties zien)
  - apply_rules.py (past categorisatieregels toe)

Huidige status:
- CSV ingest werkt
- budget.db wordt aangemaakt
- transacties worden opgeslagen
- rules-tabel bestaat
- apply_rules vult category automatisch
- inbox is leeg na regels

Concepten:
- SQL-denken vertaald naar Python
- def ≈ view/stored procedure
- SQL wordt uitgevoerd binnen db.py

Volgende stap:
- regels toevoegen via input / API
- of FastAPI toevoegen

## Next session: fix UI after profile migration
- /docs is Swagger UI, real UI is at /
- API rows now return: [id, profile_id, date, description, amount, category]
- Update JS destructuring:
  const [id, profile_id, date, description, amount, category] = t;
- Add profile_id=1 to all fetch calls:
  /transactions/uncategorized, /categories, /apply-rules, /rules
- Ensure api.py uses add_user_rule and apply_rules(conn, profile_id=...)
