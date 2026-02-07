# 🧪 Test CSV Files

## 📋 Overzicht

Ik heb 3 test CSV's voor je gemaakt om verschillende scenario's te testen:

### 1️⃣ `sample.csv` (jouw origineel)
**Gebruik:** Basis test
- 3 simpele transacties
- Mix van uitgaven en inkomen

### 2️⃣ `test_february.csv` (nieuw!) 
**Gebruik:** Realistische maand data
- 40 transacties
- Veel verschillende categorieën
- Mix van bekende winkels (Albert Heijn, Jumbo, Shell, etc.)
- Ook uncategorized items (Random Webshop, Cafe, etc.)
- Salaris + vaste lasten (huur, energie)

**Perfect voor:** Zien hoe goed je rules werken op echte data

### 3️⃣ `test_edgecases.csv` (nieuw!)
**Gebruik:** Test rule matching en duplicates
- 38 transacties
- **Edge cases:**
  - Verschillende schrijfwijzen: "AH", "ah to go", "ALBERT HEIJN ONLINE"
  - Duplicates: 2x Netflix, 2x Spotify, 2x Eneco (test of je ze allebei categoriseert)
  - Vreemde namen: "Mystery Shop", "Unknown Store", "Weird Transaction"
  - Hoofdletters variaties: "ODIDO" vs "odido"

**Perfect voor:** Testen of je rules flexibel genoeg zijn

---

## 🚀 Hoe te gebruiken

### Test 1: Basis flow
```bash
# Import eerste batch
python -m src.budgetting.ingest sample.csv

# Apply rules
python -m src.budgetting.apply_rules

# Check result
uvicorn src.budgetting.api:app --reload
# → Open http://localhost:8000
```

### Test 2: Grote dataset
```bash
# Import februari data
python -m src.budgetting.ingest test_february.csv

# Apply rules
python -m src.budgetting.apply_rules

# Check hoeveel nog in inbox zitten
```

### Test 3: Edge cases
```bash
# Import edge cases
python -m src.budgetting.ingest test_edgecases.csv

# Apply rules
python -m src.budgetting.apply_rules

# Kijk of duplicates (2x Netflix) beide gecategoriseerd zijn
```

---

## 💡 Test strategie

### Scenario A: Fresh start
```bash
# Reset database
rm budget.db

# Import test data
python -m src.budgetting.ingest test_february.csv

# Add rules + apply
python -m src.budgetting.apply_rules

# Start UI en categoriseer handmatig wat overblijft
```

### Scenario B: Incremental import
```bash
# Importeer meerdere CSV's achter elkaar
python -m src.budgetting.ingest sample.csv
python -m src.budgetting.ingest test_february.csv
python -m src.budgetting.ingest test_edgecases.csv

# Totaal: ~80 transacties
python -m src.budgetting.apply_rules
```

### Scenario C: Multiple profiles (later)
```bash
# Profile 1: jouw data
python -m src.budgetting.ingest test_february.csv --profile-id 1

# Profile 2: vriend/partner data
python -m src.budgetting.ingest test_edgecases.csv --profile-id 2

# Rules apart toepassen per profile
```

---

## 🎯 Wat te verwachten

### Na import `test_february.csv` + apply rules:

**Automatisch gecategoriseerd (~60-70%):**
- ✅ Albert Heijn → Boodschappen
- ✅ Shell → Benzine
- ✅ Odido → Mobiel abonnement / Internet
- ✅ Netflix → Abonnementen
- ✅ Salaris → Inkomen
- ✅ Eneco → Nutsvoorzieningen

**Blijft in inbox (~30-40%):**
- ❌ Random Webshop
- ❌ Cafe Het Paaltje
- ❌ Restaurant Venezia
- ❌ Booking.com
- ❌ Pathé
- ❌ Coolblue
- ❌ MediaMarkt

**Dit is perfect!** Want:
1. Je ziet dat rules werken
2. Je hebt nog werk te doen in de UI
3. Je kan nieuwe rules maken (bijv: "coolblue" → "Electronica")

---

## 🐛 Debug tips

### Check hoeveel in inbox:
```bash
python -m src.budgetting.show_inbox
```

### Check totaal aantal transacties:
```bash
sqlite3 budget.db "SELECT COUNT(*) FROM transactions WHERE profile_id=1"
```

### Check categories:
```bash
sqlite3 budget.db "SELECT category, COUNT(*) FROM transactions WHERE profile_id=1 GROUP BY category"
```

---

## 📊 Expected results

Na import van **alle 3 CSV's** + apply rules:

| Category | ~Aantal transacties |
|----------|---------------------|
| Boodschappen | 15-20 |
| Mobiel abonnement / Internet | 8-10 |
| Benzine | 4-6 |
| Abonnementen | 6-8 |
| Inkomen | 3-4 |
| Nutsvoorzieningen | 4-6 |
| Uncategorized | 20-30 |

**Inbox zou ~25-35% moeten zijn** - dat is normaal en verwacht!

---

## 🎉 Success criteria

Je app werkt goed als:
- ✅ CSV import zonder errors
- ✅ Rules matchen (case-insensitive)
- ✅ Duplicates worden beide gecategoriseerd
- ✅ UI toont uncategorized items
- ✅ Je kan handmatig categoriseren
- ✅ Je kan nieuwe rules maken
- ✅ "Apply rules" knop werkt

Succes met testen! 🚀
