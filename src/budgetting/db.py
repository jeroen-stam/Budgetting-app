from pathlib import Path
import sqlite3
import pandas as pd


def get_db_path(project_root: Path) -> Path:
    return project_root / "budget.db"


def connect(db_path: Path) -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT DEFAULT 'Uncategorized'
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            category TEXT NOT NULL
        )
    """)

    conn.commit()


def save_transactions(conn: sqlite3.Connection, df: pd.DataFrame) -> int:
    rows = df[["date", "description", "amount"]].to_records(index=False)
    conn.executemany(
        "INSERT INTO transactions (date, description, amount) VALUES (?, ?, ?)",
        rows
    )
    conn.commit()
    return len(df)

def fetch_transactions(conn: sqlite3.Connection, limit: int = 50):
    cur = conn.execute(
        """
        SELECT id, date, description, amount, category
        FROM transactions
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )
    return cur.fetchall()


def fetch_uncategorized(conn: sqlite3.Connection, limit: int = 50):
    cur = conn.execute(
        """
        SELECT id, date, description, amount, category
        FROM transactions
        WHERE category = 'Uncategorized'
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )
    return cur.fetchall()

def add_rule(conn, keyword: str, category: str):
    conn.execute(
        "INSERT INTO rules (keyword, category) VALUES (?, ?)",
        (keyword, category),
    )
    conn.commit()

def apply_rules(conn: sqlite3.Connection) -> None:
    conn.execute("""
        UPDATE transactions
        SET category = (
            SELECT r.category
            FROM rules r
            WHERE lower(transactions.description) LIKE '%' || lower(r.keyword) || '%'
            LIMIT 1
        )
        WHERE category = 'Uncategorized'
    """)
    conn.commit()

def fetch_categories(conn: sqlite3.Connection):
    # Categories die al bestaan in rules + default 'Uncategorized'
    cur = conn.execute("""
        SELECT DISTINCT category
        FROM rules
        ORDER BY category ASC
    """)
    cats = [r[0] for r in cur.fetchall()]
    if "Uncategorized" not in cats:
        cats.insert(0, "Uncategorized")
    return cats


def update_transaction_category(conn: sqlite3.Connection, transaction_id: int, category: str) -> None:
    conn.execute(
        "UPDATE transactions SET category = ? WHERE id = ?",
        (category, transaction_id),
    )
    conn.commit()


def fetch_transaction(conn: sqlite3.Connection, transaction_id: int):
    cur = conn.execute(
        """
        SELECT id, date, description, amount, category
        FROM transactions
        WHERE id = ?
        """,
        (transaction_id,),
    )
    return cur.fetchone()

def add_rule_if_not_exists(conn, keyword: str, category: str):
    cur = conn.execute(
        "SELECT 1 FROM rules WHERE lower(keyword) = lower(?)",
        (keyword,),
    )
    exists = cur.fetchone()

    if not exists:
        conn.execute(
            "INSERT INTO rules (keyword, category) VALUES (?, ?)",
            (keyword, category),
        )
        conn.commit()

def add_rule_if_not_exists(conn, keyword: str, category: str):
    cur = conn.execute(
        "SELECT 1 FROM rules WHERE lower(keyword) = lower(?)",
        (keyword,),
    )
    exists = cur.fetchone()

    if not exists:
        conn.execute(
            "INSERT INTO rules (keyword, category) VALUES (?, ?)",
            (keyword, category),
        )
        conn.commit()