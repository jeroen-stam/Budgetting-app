from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]  # <-- project root
RAW_CSV = PROJECT_ROOT / "data" / "raw" / "sample.csv"


def read_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]

    required = {"date", "description", "amount"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV mist kolommen: {missing}. Gevonden: {list(df.columns)}")

    df["amount"] = (
        df["amount"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    df["date"] = df["date"].astype(str)
    df["description"] = df["description"].astype(str)

    return df[["date", "description", "amount"]]


def main():
    print(f"Reading: {RAW_CSV}")
    df = read_csv(RAW_CSV)
    print("Columns:", list(df.columns))
    print(df.head(10))


if __name__ == "__main__":
    main()
