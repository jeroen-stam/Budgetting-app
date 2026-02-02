from pathlib import Path
import pandas as pd

from .db import get_db_path, connect, init_db, save_transactions


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_CSV = PROJECT_ROOT / "data" / "raw" / "sample.csv"


def read_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]

    required = {"date", "description", "amount"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV mist kolommen: {missing}")

    df["amount"] = (
        df["amount"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    return df[["date", "description", "amount"]]


def main():
    print(f"Reading: {RAW_CSV}")

    df = read_csv(RAW_CSV)

    print("Columns:", list(df.columns))
    print(df.head())

    db_path = get_db_path(PROJECT_ROOT)
    conn = connect(db_path)
    init_db(conn)

    inserted = save_transactions(conn, df)
    conn.close()

    print(f"Saved {inserted} rows to {db_path}")


if __name__ == "__main__":
    main()
