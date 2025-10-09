import os
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from typing import List, Dict, Any

# --- Konfigurace ---
CSV_FILE: str = "input/data/manual-entry.csv"
TEMPLATE_FILE: str = "input/template/pozvanka.html"
OUTPUT_DIR: str = "vytvorene_pozvanky"


def create_output_directory(path: str) -> None:
    """Zkontroluje existenci a případně vytvoří výstupní adresář."""
    if not os.path.exists(path):
        print(f"Vytvářím adresář: {path}")
        os.makedirs(path)

def load_recipients(file_path: str) -> List[Dict[str, Any]]:
    """Načte adresáty z CSV souboru s oddělovačem '|' a vrátí je jako seznam slovníků."""
    try:
        df = pd.read_csv(file_path, sep="|", engine="python")
        # Nahradíme prázdné hodnoty (NaN) prázdným řetězcem pro bezpečné použití v šabloně
        df.fillna("", inplace=True)
        return df.to_dict(orient="records")
    except FileNotFoundError:
        print(f"Chyba: Soubor '{file_path}' nebyl nalezen.")
        return []

def generate_pdf_invitation(data: Dict[str, Any], template: Any, output_dir: str) -> None:
    """Vygeneruje a uloží jednu PDF pozvánku."""
    # Vytvoření HTML obsahu ze šablony
    rendered_html: str = template.render(data)

    # Vytvoření bezpečného názvu souboru (nahradí mezery podtržítky)
    recipient_name: str = data.get("fullName", "neznamy").replace(" ", "_")
    output_filename: str = f"pozvanka_{recipient_name}.pdf"
    output_path: str = os.path.join(output_dir, output_filename)

    # Generování PDF
    HTML(string=rendered_html).write_pdf(output_path)
    print(f"- Vygenerována pozvánka pro: {data.get('Jmeno')}")

def main() -> None:
    """Hlavní funkce pro orchestraci generování pozvánek."""
    print("Spouštím generátor pozvánek...")
    create_output_directory(OUTPUT_DIR)

    # Načtení adresátů
    recipients: List[Dict[str, Any]] = load_recipients(CSV_FILE)
    if not recipients:
        print("Žádní adresáti k zpracování. Končím.")
        return

    # Nastavení a načtení Jinja2 šablony
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template(TEMPLATE_FILE)

    print(f"Nalezeno {len(recipients)} adresátů. Začínám generování PDF...")

    # Generování PDF pro každého adresáta
    for recipient in recipients:
        generate_pdf_invitation(recipient, template, OUTPUT_DIR)

    print(f"\nHotovo! Všechny pozvánky byly uloženy do adresáře '{OUTPUT_DIR}'.")


if __name__ == "__main__":
    main()
