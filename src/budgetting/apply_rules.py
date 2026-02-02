from pathlib import Path
from .db import get_db_path, connect, init_db, add_rule, apply_rules

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def main():
    conn = connect(get_db_path(PROJECT_ROOT))
    init_db(conn)

    # tijdelijke regels
    add_rule(conn, "Albert Heijn", "Groceries")
    add_rule(conn, "NS", "Transport")
    add_rule(conn, "Salaris", "Income")

    apply_rules(conn)
    conn.close()

    print("Rules applied.")

if __name__ == "__main__":
    main()
