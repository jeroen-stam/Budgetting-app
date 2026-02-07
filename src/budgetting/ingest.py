"""
CSV Ingest Script - Import bank transactions from CSV

Usage:
  # Default: importeert data/raw/sample.csv
  python -m src.budgetting.ingest

  # Custom CSV pad
  python -m src.budgetting.ingest /pad/naar/andere.csv
  
  # Custom profile
  python -m src.budgetting.ingest sample.csv --profile-id 2
"""

import sys
from pathlib import Path
import pandas as pd

from .db import get_db_path, connect, init_db, save_transactions


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CSV = PROJECT_ROOT / "data" / "raw" / "sample.csv"


def read_csv(path: Path) -> pd.DataFrame:
    """
    Leest CSV en normaliseert de data.
    
    - Kolommen worden lowercase gemaakt
    - Komma's in bedragen worden punten (1.234,56 → 1234.56)
    - Checkt of verplichte kolommen aanwezig zijn
    """
    df = pd.read_csv(path)
    
    # Normaliseer kolom namen (spaties weg, lowercase)
    df.columns = [c.strip().lower() for c in df.columns]

    # Check verplichte kolommen
    required = {"date", "description", "amount"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV mist kolommen: {missing}")

    # Fix Nederlandse/Europese getallen: 1.234,56 → 1234.56
    df["amount"] = (
        df["amount"]
        .astype(str)
        .str.replace(".", "", regex=False)  # verwijder duizendtal separator
        .str.replace(",", ".", regex=False)  # komma → punt
        .astype(float)
    )

    return df[["date", "description", "amount"]]


def ingest_csv(csv_path: Path, profile_id: int = 1) -> int:
    """Import CSV naar database en return aantal rows"""
    
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV niet gevonden: {csv_path}")
    
    print(f"📂 Reading: {csv_path}")
    
    # Lees en valideer CSV
    df = read_csv(csv_path)
    
    print(f"   Columns: {list(df.columns)}")
    print(f"   Rows: {len(df)}")
    print("\nPreview:")
    print(df.head())
    
    # Database connectie
    db_path = get_db_path(PROJECT_ROOT)
    conn = connect(db_path)
    init_db(conn)
    
    # Import
    print(f"\n💾 Importing to profile_id={profile_id}...")
    inserted = save_transactions(conn, df, profile_id=profile_id)
    conn.close()
    
    print(f"✅ Saved {inserted} rows to {db_path}")
    return inserted


def main():
    """
    Main functie met command-line argument support.
    
    Backwards compatible: zonder argumenten gebruikt het DEFAULT_CSV
    """
    
    # Default waarden
    csv_path = DEFAULT_CSV
    profile_id = 1
    
    # Parse command-line argumenten
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        # Eerste argument is CSV pad
        csv_path = Path(sys.argv[1])
    
    # Check for --profile-id
    if "--profile-id" in sys.argv:
        try:
            idx = sys.argv.index("--profile-id")
            profile_id = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            print("❌ Error: --profile-id requires a number")
            print("   Example: python -m src.budgetting.ingest sample.csv --profile-id 2")
            sys.exit(1)
    
    # Run import
    try:
        count = ingest_csv(csv_path, profile_id=profile_id)
        
        print(f"\n🎯 Next steps:")
        print(f"   1. Apply rules:  python -m src.budgetting.apply_rules")
        print(f"   2. Start API:    uvicorn src.budgetting.api:app --reload")
        print(f"   3. Open browser: http://localhost:8000")
        
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print(f"\n💡 Tip: Zet je CSV in data/raw/ of geef een pad op:")
        print(f"   python -m src.budgetting.ingest /pad/naar/je.csv")
        sys.exit(1)
        
    except ValueError as e:
        print(f"❌ CSV format error: {e}")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()