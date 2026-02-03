from pathlib import Path
from .db import (
    get_db_path,
    connect,
    init_db,
    add_rule_if_not_exists,
    apply_rules,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_RULES = [
    ("odido", "Mobiel abonnement / Internet"),
    ("ziggo", "Mobiel abonnement / Internet"),
    ("albert heijn", "Boodschappen"),
    ("jumbo", "Boodschappen"),
    ("salaris", "Inkomen"),
]

def main():
    conn = connect(get_db_path(PROJECT_ROOT))
    init_db(conn)

    for keyword, category in DEFAULT_RULES:
        add_rule_if_not_exists(conn, keyword, category)

    apply_rules(conn)
    conn.close()

    print("Default rules ensured & applied.")

if __name__ == "__main__":
    main()
