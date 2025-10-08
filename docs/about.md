Dobrý den. Vytvoření generátoru pozvánek je skvělý nápad.

Vámi navržený postup s použitím šablony ve Wordu (.docx) je sice možný, ale pro automatizované zpracování má několik technických úskalí:
1.  **Složitost:** Programové manipulování s `.docx` soubory je komplikované a náchylné k chybám, zvláště při zachování složitého formátování.
2.  **Závislost:** Vyžaduje, aby na systému, kde kód poběží, byly nainstalovány specifické knihovny nebo dokonce samotný MS Word/LibreOffice pro spolehlivý převod do PDF.
3.  **Kvalita převodu:** Převod z DOCX do PDF nemusí být vždy 100% věrný a může se lišit v závislosti na použitém softwaru.

### Lepší řešení: HTML šablona a převod na PDF

Navrhuji modernější a flexibilnější řešení, které je v softwarovém vývoji pro tento účel standardem: **Vytvoření šablony v HTML/CSS a následný programový převod na PDF.**

**Proč je to lepší?**
*   **Plná kontrola nad vzhledem:** HTML a CSS vám dávají absolutní kontrolu nad designem, písmem, obrázky a rozložením prvků.
*   **Vysoká kvalita PDF:** Knihovny pro převod HTML do PDF používají renderovací jádra prohlížečů (jako je Chrome) a vytvářejí tak PDF, které vypadá přesně tak, jak má.
*   **Oddělení dat od vzhledu:** Šablona (HTML) je oddělená od dat (CSV) a logiky (skript). Změna designu nevyžaduje změnu v kódu.
*   **Nezávislost:** Běží na jakémkoliv systému (Windows, Linux, macOS) bez nutnosti instalace kancelářských balíků.

---

### Návrh postupu

Zde je krok-za-krokem plán, jak bychom postupovali:

**Krok 1: Příprava datového souboru**

Vytvoříme jednoduchý CSV soubor s názvem `adresari.csv`. Bude obsahovat sloupce s daty o adresátech.

*Příklad (`adresari.csv`):*
```csv
Jmeno,Titul,Pozice,Email,Telefon
Jan Novák,Ing.,Ředitel společnosti,jan.novak@firma.cz,123456789
Petra Svobodová,,Marketingový specialista,petra.svobodova@firma.cz,987654321
```

**Krok 2: Vytvoření HTML šablony**

Vytvoříme soubor `sablona.html`, který bude obsahovat vzhled pozvánky. Pro data, která se budou doplňovat, použijeme zástupné značky (např. `{{JMENO}}`).

*Příklad (`sablona.html`):*
```html
<!DOCTYPE html>
<html>
<head>
    <title>Pozvánka</title>
    <style>
        body { font-family: sans-serif; }
        .pozvanka { border: 1px solid #ccc; padding: 20px; margin: 20px; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <div class="pozvanka">
        <h1>Pozvánka na výroční setkání</h1>
        <p>Vážený/á <strong>{{TITUL}} {{JMENO}}</strong>,</p>
        <p>srdečně Vás zveme na výroční setkání naší společnosti.</p>
        <p>Vaše pozice: {{POZICE}}</p>
        <hr>
        <p>Těšíme se na Vás!</p>
    </div>
</body>
</html>
```

**Krok 3: Výběr technologie a vytvoření skriptu**

Vytvoříme skript (např. v Pythonu nebo C#/.NET, jelikož jste ve složce `dotnet`), který provede celou operaci.

**Logika skriptu:**
1.  Načte data ze souboru `adresari.csv`.
2.  Načte obsah šablony `sablona.html`.
3.  Pro každý řádek v CSV souboru (pro každého adresáta):
    a. Vytvoří kopii HTML šablony.
    b. Nahradí zástupné značky (`{{JMENO}}`, `{{POZICE}}` atd.) skutečnými daty daného adresáta.
    c. Pomocí specializované knihovny vygeneruje z tohoto upraveného HTML soubor PDF.
    d. Uloží PDF pod unikátním názvem (např. `pozvanka_Jan_Novak.pdf`).

**Příklad technologií:**
*   **Python:** Velmi populární pro tento úkol. Použili bychom knihovny jako `pandas` pro čtení CSV, `Jinja2` pro práci se šablonami a `WeasyPrint` pro excelentní převod HTML/CSS do PDF.
*   **.NET/C#:** Vhodná volba vzhledem k vaší pracovní složce. Použili bychom knihovny jako `CsvHelper` pro CSV, `Scriban` pro šablonování a `QuestPDF` nebo `IronPdf` pro generování PDF.

Tento přístup je robustnější, snadněji se udržuje a poskytuje lepší kontrolu nad výsledným vzhledem.

**Jak si přejete pokračovat? Můžeme začít s přípravou souborů a výběrem konkrétní technologie (doporučuji Python pro jeho jednoduchost v tomto případě, ale .NET je také skvělá volba).**
