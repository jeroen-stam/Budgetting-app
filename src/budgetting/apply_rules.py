from pathlib import Path
from .db import (
    get_db_path,
    connect,
    init_db,
    add_default_rule,  # ← dit is de juiste functie naam
    apply_rules,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Deze rules worden toegepast op ALLE profielen (profile_id = NULL in database)
DEFAULT_RULES = [
    ("odido", "Mobiel abonnement / Internet"),
    ("ziggo", "Mobiel abonnement / Internet"),
    ("kpn", "Mobiel abonnement / Internet"),
    ("t-mobile", "Mobiel abonnement / Internet"),
    
    ("albert heijn", "Boodschappen"),
    ("ah ", "Boodschappen"),  # vaak zie je "AH 1234" in beschrijvingen
    ("jumbo", "Boodschappen"),
    ("lidl", "Boodschappen"),
    ("aldi", "Boodschappen"),
    ("plus", "Boodschappen"),
    
    ("shell", "Benzine"),
    ("esso", "Benzine"),
    ("bp ", "Benzine"),
    
    ("netflix", "Abonnementen"),
    ("spotify", "Abonnementen"),
    ("disney", "Abonnementen"),
    
    ("salaris", "Inkomen"),
    ("loon", "Inkomen"),
    
    ("huur", "Wonen"),
    ("hypotheek", "Wonen"),
    ("nuon", "Nutsvoorzieningen"),
    ("eneco", "Nutsvoorzieningen"),
    ("vattenfall", "Nutsvoorzieningen"),
    ("essent", "Nutsvoorzieningen"),
    ("waternet", "Nutsvoorzieningen"),
]

def main():
    """
    Voegt default rules toe aan de database.
    Deze functie is 'idempotent' = je kan hem meerdere keren draaien,
    hij voegt alleen regels toe die er nog niet zijn (INSERT OR IGNORE).
    """
    conn = connect(get_db_path(PROJECT_ROOT))
    init_db(conn)

    print("Adding default rules...")
    for keyword, category in DEFAULT_RULES:
        add_default_rule(conn, keyword, category)
        print(f"  ✓ {keyword} → {category}")

    print("\nApplying rules to profile 1...")
    apply_rules(conn, profile_id=1)
    
    conn.close()
    print("\n✅ Done! Default rules ensured & applied.")

if __name__ == "__main__":
    main()