from pathlib import Path
from .db import get_db_path, connect, init_db, fetch_uncategorized

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def main(profile_id: int = 1):
    db_path = get_db_path(PROJECT_ROOT)
    conn = connect(db_path)
    init_db(conn)

    rows = fetch_uncategorized(conn, profile_id=profile_id, limit=200)
    conn.close()

    print(f"Uncategorized transactions for profile_id={profile_id} (showing {len(rows)}):\n")
    for r in rows:
        # r = (id, profile_id, date, description, amount, category)
        _id, _profile_id, date, desc, amount, category = r
        print(f"{_id:>4} | {date} | {amount:>8.2f} | {desc}")

if __name__ == "__main__":
    main()
