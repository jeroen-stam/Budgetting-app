from pathlib import Path
import sqlite3
import pandas as pd


# ---------- connection / schema ----------

def get_db_path(project_root: Path) -> Path:
    return project_root / "budget.db"


def connect(db_path: Path) -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def init_db(conn: sqlite3.Connection) -> None:
    # Profiles
    conn.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    # Default profile (id=1)
    conn.execute("INSERT OR IGNORE INTO profiles (id, name) VALUES (1, 'default')")

    # Transactions (multi-profile)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id  INTEGER NOT NULL,
            date        TEXT NOT NULL,
            description TEXT NOT NULL,
            amount      REAL NOT NULL,
            category    TEXT DEFAULT 'Uncategorized',
            FOREIGN KEY (profile_id) REFERENCES profiles(id)
        )
    """)

    # Rules: profile_id NULL = default rules, profile_id = X = user rules
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rules (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NULL,
            keyword    TEXT NOT NULL COLLATE NOCASE,
            category   TEXT NOT NULL,
            FOREIGN KEY (profile_id) REFERENCES profiles(id),
            UNIQUE (profile_id, keyword)
        )
    """)

    # Helpful indexes
    conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_profile ON transactions(profile_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_rules_profile ON rules(profile_id)")

    conn.commit()


# ---------- profiles ----------

def create_profile(conn: sqlite3.Connection, name: str) -> int:
    cur = conn.execute("INSERT INTO profiles (name) VALUES (?)", (name,))
    conn.commit()
    return int(cur.lastrowid)


def list_profiles(conn: sqlite3.Connection):
    cur = conn.execute("SELECT id, name FROM profiles ORDER BY id ASC")
    return cur.fetchall()


# ---------- transactions ----------

def save_transactions(conn: sqlite3.Connection, df: pd.DataFrame, profile_id: int = 1) -> int:
    rows = df[["date", "description", "amount"]].to_records(index=False)

    conn.executemany(
        "INSERT INTO transactions (profile_id, date, description, amount) VALUES (?, ?, ?, ?)",
        [(profile_id, r[0], r[1], float(r[2])) for r in rows],
    )
    conn.commit()
    return len(df)


def fetch_transactions(conn: sqlite3.Connection, profile_id: int = 1, limit: int = 50):
    cur = conn.execute(
        """
        SELECT id, profile_id, date, description, amount, category
        FROM transactions
        WHERE profile_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (profile_id, limit),
    )
    return cur.fetchall()


def fetch_uncategorized(conn: sqlite3.Connection, profile_id: int = 1, limit: int = 50):
    cur = conn.execute(
        """
        SELECT id, profile_id, date, description, amount, category
        FROM transactions
        WHERE profile_id = ?
          AND category = 'Uncategorized'
        ORDER BY id DESC
        LIMIT ?
        """,
        (profile_id, limit),
    )
    return cur.fetchall()


def update_transaction_category(conn: sqlite3.Connection, transaction_id: int, category: str) -> None:
    conn.execute(
        "UPDATE transactions SET category = ? WHERE id = ?",
        (category, transaction_id),
    )
    conn.commit()


# ---------- rules ----------

def add_default_rule(conn: sqlite3.Connection, keyword: str, category: str) -> None:
    # default rule: profile_id = NULL
    conn.execute(
        "INSERT OR IGNORE INTO rules (profile_id, keyword, category) VALUES (NULL, ?, ?)",
        (keyword, category),
    )
    conn.commit()


def add_user_rule(conn: sqlite3.Connection, profile_id: int, keyword: str, category: str) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO rules (profile_id, keyword, category) VALUES (?, ?, ?)",
        (profile_id, keyword, category),
    )
    conn.commit()


def fetch_categories(conn: sqlite3.Connection, profile_id: int = 1):
    # categories from default rules + user rules
    cur = conn.execute(
        """
        SELECT DISTINCT category
        FROM rules
        WHERE profile_id IS NULL OR profile_id = ?
        ORDER BY category ASC
        """,
        (profile_id,),
    )
    cats = [r[0] for r in cur.fetchall()]
    if "Uncategorized" not in cats:
        cats.insert(0, "Uncategorized")
    return cats


def apply_rules(conn: sqlite3.Connection, profile_id: int = 1) -> None:
    """
    Apply default rules first (profile_id IS NULL), then user rules (profile_id = ?).
    We do two UPDATE passes so user rules can override defaults if needed.
    """

    # 1) apply default rules
    conn.execute(
        """
        UPDATE transactions
        SET category = (
            SELECT r.category
            FROM rules r
            WHERE r.profile_id IS NULL
              AND lower(transactions.description) LIKE '%' || lower(r.keyword) || '%'
            LIMIT 1
        )
        WHERE transactions.profile_id = ?
          AND transactions.category = 'Uncategorized'
        """,
        (profile_id,),
    )

    # 2) apply user rules (can override, so we apply even if already categorized)
    conn.execute(
        """
        UPDATE transactions
        SET category = (
            SELECT r.category
            FROM rules r
            WHERE r.profile_id = ?
              AND lower(transactions.description) LIKE '%' || lower(r.keyword) || '%'
            LIMIT 1
        )
        WHERE transactions.profile_id = ?
        """,
        (profile_id, profile_id),
    )

    conn.commit()
