# Plán implementace generátoru pozvánek v Pythonu

Tento dokument popisuje detailní postup pro vytvoření aplikace na generování PDF pozvánek ze strukturovaných dat pomocí Pythonu.

### 1. Cíl

Vytvořit skript, který automaticky načte seznam adresátů z `adresari.csv`, pro každého adresáta vyplní jeho údaje do připravené `sablona.html` a výsledek uloží jako samostatný PDF soubor do určené složky.

### 2. Použité technologie a knihovny

- **Python 3:** Hlavní programovací jazyk.
- **`pandas`:** Výkonná knihovna pro načítání a efektivní práci s daty z CSV souboru.
- **`Jinja2`:** Moderní šablonovací engine, který nám umožní vkládat data do HTML šablony pomocí zástupných symbolů (např. `{{ JMENO }}`).
- **`WeasyPrint`:** Knihovna pro převod HTML a CSS do PDF. Vyniká vysokou kvalitou a věrností zobrazení moderních CSS stylů.

### 3. Struktura projektu

Projekt bude mít následující adresářovou strukturu:

```
.
├── docs/
│   └── about-python.md
├── vytvorene_pozvanky/
├── adresari.csv
├── generator.py
├── requirements.txt
└── sablona.html
```

- `docs/`: Složka pro dokumentaci.
- `vytvorene_pozvanky/`: Do této složky bude skript ukládat vygenerované PDF soubory. Skript ji automaticky vytvoří.
- `adresari.csv`: Vstupní data s adresáty.
- `generator.py`: Hlavní spustitelný skript v Pythonu.
- `requirements.txt`: Seznam Python knihoven, které jsou pro projekt potřeba.
- `sablona.html`: HTML šablona pro vzhled pozvánky.

### 4. Detailní postup implementace

#### Krok 1: Nastavení virtuálního prostředí a instalace závislostí

Abychom udrželi pořádek v závislostech, vytvoříme virtuální prostředí.

1.  **Vytvoření `requirements.txt`:** Vytvořím soubor se seznamem potřebných knihoven.
2.  **Vytvoření virtuálního prostředí:** Pomocí příkazu `python3 -m venv .venv`.
3.  **Aktivace prostředí:** Spuštěním `source .venv/bin/activate` (pro Linux/macOS) nebo `.venv\Scripts\activate` (pro Windows).
4.  **Instalace knihoven:** Pomocí příkazu `pip install -r requirements.txt`.
    *   **Poznámka:** `WeasyPrint` může na některých systémech vyžadovat doinstalování systémových závislostí (GTK3). V případě potřeby dodám instrukce. Například na Debian/Ubuntu se instalují pomocí: `sudo apt-get install libpango-1.0-0 libpangoft2-1.0-0`.

#### Krok 2: Příprava datových souborů (`adresari.csv` a `sablona.html`)

Vytvořím dva hlavní soubory: jeden s daty a druhý se šablonou, přesně podle návrhu z předchozí konverzace.

#### Krok 3: Vytvoření hlavního skriptu (`generator.py`)

Skript bude obsahovat následující logiku:
1.  **Importy:** Načtení potřebných funkcí z knihoven `pandas`, `jinja2`, `weasyprint` a `os`.
2.  **Definice cest:** Nastavení názvů souborů a složek pro snadnou orientaci.
3.  **Vytvoření výstupní složky:** Skript zkontroluje, zda existuje složka `vytvorene_pozvanky`, a pokud ne, vytvoří ji.
4.  **Načtení dat:** Pomocí `pandas` se načte soubor `adresari.csv` do datové struktury DataFrame.
5.  **Načtení šablony:** Inicializuje se `Jinja2` a načte se obsah souboru `sablona.html`.
6.  **Generovací smyčka:** Skript projde řádek po řádku data z CSV.
    a. Pro každý řádek (adresáta) se jeho data (jméno, pozice atd.) vloží do načtené HTML šablony.
    b. Výsledný HTML kód pro daného adresáta se pomocí `WeasyPrint` převede na PDF.
    c. PDF se uloží do složky `vytvorene_pozvanky` pod unikátním názvem (např. `pozvanka_host_001.pdf`).
7.  **Informační výpisy:** Skript bude do konzole vypisovat průběh generování.

#### Krok 4: Spuštění

Po dokončení všech příprav bude stačit v terminálu s aktivovaným virtuálním prostředím spustit jediný příkaz:
`python3 generator.py`

Výsledkem bude složka `vytvorene_pozvanky` naplněná hotovými PDF soubory.
