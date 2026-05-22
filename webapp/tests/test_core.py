from __future__ import annotations

import io
import tempfile
import unittest
import zipfile
from pathlib import Path

from pdf_generator.core import (
    CsvInputError,
    TemplatePackageError,
    generate_pdf_zip,
    get_excel_sheet_names,
    list_html_templates,
    load_excel_recipients,
    load_recipients,
    prepare_template_upload,
    safe_extract_template_zip,
)


def _zip_bytes(files: dict[str, str | bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return buffer.getvalue()


def _excel_bytes() -> bytes:
    import pandas as pd

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame(
            [
                {"fullName": "Jane Doe", "spouse": ""},
                {"fullName": "John Doe", "spouse": "and spouse"},
            ]
        ).to_excel(writer, index=False, sheet_name="Data")
    return buffer.getvalue()


class CoreTests(unittest.TestCase):
    def test_load_recipients_pipe_csv(self) -> None:
        rows, columns = load_recipients(b"fullName|spouse\nJane Doe|\nJohn Doe|and spouse\n", "|")

        self.assertEqual(columns, ["fullName", "spouse"])
        self.assertEqual(
            rows,
            [
                {"fullName": "Jane Doe", "spouse": ""},
                {"fullName": "John Doe", "spouse": "and spouse"},
            ],
        )

    def test_load_recipients_rejects_empty_csv(self) -> None:
        with self.assertRaises(CsvInputError):
            load_recipients(b"", "|")

    def test_load_excel_recipients(self) -> None:
        rows, columns = load_excel_recipients(_excel_bytes(), "Data")

        self.assertEqual(columns, ["fullName", "spouse"])
        self.assertEqual(rows[0]["fullName"], "Jane Doe")
        self.assertEqual(rows[1]["spouse"], "and spouse")

    def test_get_excel_sheet_names(self) -> None:
        self.assertEqual(get_excel_sheet_names(_excel_bytes()), ["Data"])

    def test_safe_extract_rejects_path_traversal(self) -> None:
        archive = _zip_bytes({"../escape.html": "<html></html>"})

        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(TemplatePackageError):
                safe_extract_template_zip(archive, Path(temp_dir))

    def test_list_html_templates(self) -> None:
        archive = _zip_bytes({"templates/main.html": "<html></html>", "asset.txt": "x"})

        with tempfile.TemporaryDirectory() as temp_dir:
            template_root = Path(temp_dir)
            safe_extract_template_zip(archive, template_root)

            self.assertEqual(list_html_templates(template_root), ["templates/main.html"])

    def test_prepare_direct_html_upload_generates_pdf_zip(self) -> None:
        html = b"""
        <!doctype html>
        <html>
        <body>
          <p>{{ fullName }}</p>
        </body>
        </html>
        """
        rows, _columns = load_recipients(b"fullName\nJane Doe\n", ",")

        with tempfile.TemporaryDirectory() as temp_dir:
            template_root = Path(temp_dir)
            templates = prepare_template_upload("template.html", html, template_root)
            output_zip = generate_pdf_zip(rows, template_root, templates[0])

        self.assertEqual(templates, ["uploaded_template.html"])
        self.assertTrue(output_zip.startswith(b"PK"))


if __name__ == "__main__":
    unittest.main()
