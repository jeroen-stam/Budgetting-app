from pathlib import Path
from .db import get_db_path, connect, fetch_uncategorized

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def main():
    db_path = get_db_path(PROJECT_ROOT)
    conn = connect(db_path)

    rows = fetch_uncategorized(conn, limit=50)
    conn.close()

    print(f"Uncategorized transactions (showing {len(rows)}):\n")
    for r in rows:
        _id, date, desc, amount, category = r
        print(f"{_id:>4} | {date} | {amount:>8.2f} | {desc}")

if __name__ == "__main__":
    main()
