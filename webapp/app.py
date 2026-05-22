from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from pdf_generator import (
    CsvInputError,
    GenerationError,
    TemplatePackageError,
    generate_pdf_zip,
    get_excel_sheet_names,
    load_excel_recipients,
    load_recipients,
    prepare_template_upload,
)


DELIMITER_OPTIONS = {
    "Automaticky rozpoznat": "auto",
    "Svislítko |": "|",
    "Čárka ,": ",",
    "Středník ;": ";",
    "Tabulátor": "tab",
}


def main() -> None:
    st.set_page_config(page_title="Generátor PDF pozvánek", page_icon=":page_facing_up:", layout="centered")
    st.title("Generátor PDF pozvánek")
    _render_help()

    template_file = st.file_uploader("HTML šablona nebo ZIP se šablonou", type=["html", "htm", "zip"])
    data_file = st.file_uploader("CSV nebo Excel soubor s daty", type=["csv", "txt", "xlsx", "xlsm"])

    data_bytes: bytes | None = None
    delimiter_label = "Svislítko |"
    sheet_name: str | None = None

    if data_file:
        data_bytes = data_file.getvalue()
        if _is_excel_file(data_file.name):
            try:
                sheet_names = get_excel_sheet_names(data_bytes)
            except CsvInputError as exc:
                st.error(str(exc))
                return

            if len(sheet_names) == 1:
                sheet_name = sheet_names[0]
                st.caption(f"Použitý list Excelu: {sheet_name}")
            else:
                sheet_name = st.selectbox("List v Excelu", sheet_names)
        else:
            delimiter_label = st.selectbox("Oddělovač v CSV", list(DELIMITER_OPTIONS), index=1)

    if not template_file or not data_file or data_bytes is None:
        st.info("Nahrajte HTML šablonu nebo ZIP se šablonou a k tomu CSV nebo Excel soubor s daty.")
        return

    try:
        if _is_excel_file(data_file.name):
            recipients, columns = load_excel_recipients(data_bytes, sheet_name)
        else:
            recipients, columns = load_recipients(data_bytes, DELIMITER_OPTIONS[delimiter_label])
    except CsvInputError as exc:
        st.error(str(exc))
        return

    st.caption(f"Načteno {len(recipients)} řádků a {len(columns)} sloupců.")
    st.code(", ".join(columns), language="text")

    with tempfile.TemporaryDirectory(prefix="pdf-template-") as temp_dir:
        template_root = Path(temp_dir)
        try:
            html_templates = prepare_template_upload(template_file.name, template_file.getvalue(), template_root)
        except TemplatePackageError as exc:
            st.error(str(exc))
            return

        if len(html_templates) == 1:
            selected_template = html_templates[0]
            st.caption(f"Použitá šablona: {selected_template}")
        else:
            selected_template = st.selectbox("HTML šablona", html_templates)

        if st.button("Vygenerovat PDF", type="primary"):
            with st.spinner("Generuji PDF..."):
                try:
                    zip_bytes = generate_pdf_zip(recipients, template_root, selected_template)
                except (CsvInputError, TemplatePackageError, GenerationError) as exc:
                    st.error(str(exc))
                    return

            st.success("PDF soubory jsou připravené.")
            st.download_button(
                "Stáhnout vygenerovane_pozvanky.zip",
                data=zip_bytes,
                file_name="vygenerovane_pozvanky.zip",
                mime="application/zip",
            )


def _render_help() -> None:
    st.subheader("Jak to funguje")
    st.markdown(
        """
        Nahrajete HTML šablonu a CSV nebo Excel soubor s daty. Aplikace pro každý datový řádek
        doplní hodnoty do šablony, vytvoří samostatné PDF a nakonec vše zabalí do jednoho ZIP souboru ke stažení.
        Data se zpracovávají jen během generování a neukládají se do projektu.
        """
    )

    st.subheader("Podrobnější návod")
    st.markdown(
        """
        1. V HTML šabloně používejte názvy sloupců z CSV jako Jinja proměnné, například
           `{{ fullName }}` nebo `{{ eventDate }}`.
        2. CSV nebo Excel musí mít hlavičku. Pokud používáte současná CSV data, typický oddělovač je `|`.
        3. Pokud šablona obsahuje jen HTML, inline CSS a obrázky vložené jako `data:`, nahrajte
           přímo `.html` nebo `.htm` soubor.
        4. Pokud HTML používá relativní obrázky nebo fonty, nahrajte ZIP obsahující HTML i všechny
           potřebné soubory.
        5. U Excelu se jako zdroj dat používá vybraný list sešitu. Podporované jsou `.xlsx` a `.xlsm`.
        6. Výsledkem je ZIP, ve kterém je jedno PDF pro každý datový řádek.
        """
    )


def _is_excel_file(file_name: str) -> bool:
    return Path(file_name).suffix.lower() in {".xlsx", ".xlsm"}


if __name__ == "__main__":
    main()
