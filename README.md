# Generátor PDF pozvánek

Jednoduchý Python nástroj pro hromadné generování personalizovaných PDF pozvánek. Program načte seznam adresátů z CSV souboru, doplní data do HTML šablony a pro každý řádek vytvoří samostatný PDF soubor.

## Co projekt obsahuje

```text
.
├── generator.py                         # hlavní skript pro generování PDF
├── requirements.txt                     # Python závislosti
├── howto.txt                            # původní stručný návod
├── input/
│   ├── data/
│   │   └── manual-entry.csv             # vstupní seznam adresátů
│   └── template/
│       ├── pozvanka.html                # HTML/Jinja2 šablona pozvánky
│       └── Nina-Čalopek_sanitized__files/ # obrázky a podpůrné soubory šablony
├── vytvorene_pozvanky/                  # vygenerované PDF pozvánky
└── vytvorene_pozvanky.zip               # archiv vygenerovaných pozvánek
```

## Požadavky

- Python 3.10 nebo novější
- Python balíčky uvedené v `requirements.txt`:
  - `pandas`
  - `Jinja2`
  - `WeasyPrint`

`WeasyPrint` může na některých systémech vyžadovat systémové knihovny pro práci s HTML, CSS, fonty a obrázky. Pokud instalace nebo generování PDF selže, zkontrolujte oficiální instalační návod WeasyPrint pro váš operační systém.

## Instalace

### Varianta s virtuálním prostředím

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Na Windows použijte aktivaci:

```powershell
.venv\Scripts\activate
```

### Varianta s Conda

```bash
conda create --name pozvanky python=3.10
conda activate pozvanky
conda install -c conda-forge pandas jinja2 weasyprint
```

## Příprava vstupních dat

Adresáti se zapisují do souboru:

```text
input/data/manual-entry.csv
```

Soubor používá oddělovač `|` a musí obsahovat hlavičku:

```csv
fullName|spouse
H.E. Mr. Example Name|
H.E. Mrs. Example Name|yes
```

Význam sloupců:

- `fullName` - celé jméno nebo oslovení adresáta přesně tak, jak má být uvedeno na pozvánce.
- `spouse` - pokud je vyplněno libovolnou hodnotou, skript v šabloně použije text `and spouse`; pokud je prázdné, nedoplní nic.

Skript automaticky ořízne mezery na začátku a konci hodnoty `fullName`.

## Generování pozvánek

Spusťte:

```bash
python3 generator.py
```

Skript provede tyto kroky:

1. Načte data z `input/data/manual-entry.csv`.
2. Vykreslí šablonu `input/template/pozvanka.html` pro každého adresáta.
3. Vytvoří výstupní adresář `vytvorene_pozvanky/`, pokud ještě neexistuje.
4. Uloží PDF soubory ve formátu:

```text
vytvorene_pozvanky/invitation_Jmeno_Adresata.pdf
```

Po dokončení skript vypíše počet zpracovaných adresátů a seznam vygenerovaných pozvánek.

## Úprava šablony

Hlavní šablona je:

```text
input/template/pozvanka.html
```

Šablona používá Jinja2 proměnné odpovídající názvům sloupců v CSV. Aktuálně se používají zejména:

```jinja2
{{ fullName }}
{{ spouse }}
```

Při úpravách šablony neměňte názvy proměnných, pokud zároveň neupravíte i CSV a logiku v `generator.py`.

Obrázky a podpůrné soubory šablony jsou v adresáři:

```text
input/template/Nina-Čalopek_sanitized__files/
```

## Kontrola výsledků

Po vygenerování vždy otevřete několik PDF souborů z `vytvorene_pozvanky/` a zkontrolujte:

- správné jméno adresáta,
- správné zobrazení textu `and spouse`,
- rozložení textu na stránce,
- načtení obrázků a grafiky,
- diakritiku a speciální znaky ve jménech.

Při změně šablony doporučujeme zkontrolovat krátká i dlouhá jména, aby nedošlo k přetékání textu.

## Časté problémy

### Skript hlásí, že CSV soubor nebyl nalezen

Ověřte, že soubor existuje přesně na této cestě:

```text
input/data/manual-entry.csv
```

Skript používá relativní cesty, proto ho spouštějte z kořenového adresáře repozitáře.

### PDF neobsahuje obrázky

Zkontrolujte, že soubory šablony zůstaly v adresáři `input/template/` a že se nezměnily relativní cesty v HTML.

### Instalace WeasyPrint selže

Použijte Conda instalaci z kanálu `conda-forge`, která obvykle vyřeší i systémové závislosti:

```bash
conda install -c conda-forge weasyprint
```

## Doporučený pracovní postup

1. Upravte `input/data/manual-entry.csv`.
2. Spusťte `python3 generator.py`.
3. Zkontrolujte vybrané PDF soubory ve `vytvorene_pozvanky/`.
4. Pokud je výsledek správný, archivujte nebo odešlete obsah výstupního adresáře.

## Poznámky k datům

Vstupní soubor obsahuje osobní údaje adresátů. Nesdílejte ho veřejně a při práci s repozitářem dávejte pozor, kam se kopírují CSV soubory, PDF výstupy a ZIP archivy.
