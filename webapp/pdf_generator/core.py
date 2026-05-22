from __future__ import annotations

import io
import os
import re
import shutil
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlparse

import pandas as pd
from jinja2 import StrictUndefined
from jinja2.sandbox import SandboxedEnvironment
from weasyprint import HTML, default_url_fetcher

MAX_ROWS = 200
MAX_ZIP_BYTES = 20 * 1024 * 1024
MAX_HTML_BYTES = 20 * 1024 * 1024
MAX_DATA_BYTES = 20 * 1024 * 1024
MAX_UNPACKED_BYTES = 50 * 1024 * 1024
PDF_TIMEOUT_SECONDS = 30

ALLOWED_DELIMITERS = {
    "auto": None,
    "|": "|",
    ",": ",",
    ";": ";",
    "tab": "\t",
}


class CsvInputError(ValueError):
    """Raised when uploaded recipient data cannot be used."""


class TemplatePackageError(ValueError):
    """Raised when uploaded template package is invalid."""


class GenerationError(RuntimeError):
    """Raised when PDF generation fails for a recipient."""


def safe_extract_template_zip(zip_bytes: bytes, destination: Path) -> None:
    """Extract a ZIP archive while blocking traversal and oversized packages."""
    if len(zip_bytes) > MAX_ZIP_BYTES:
        raise TemplatePackageError("ZIP se šablonou je větší než 20 MB.")

    destination.mkdir(parents=True, exist_ok=True)
    total_size = 0

    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue

                total_size += info.file_size
                if total_size > MAX_UNPACKED_BYTES:
                    raise TemplatePackageError("ZIP se šablonou má po rozbalení více než 50 MB.")

                relative_path = _safe_archive_path(info.filename)
                target_path = (destination / relative_path).resolve()
                _ensure_child_path(target_path, destination)
                target_path.parent.mkdir(parents=True, exist_ok=True)

                with archive.open(info) as source, target_path.open("wb") as target:
                    shutil.copyfileobj(source, target)
    except zipfile.BadZipFile as exc:
        raise TemplatePackageError("Nahraná šablona není platný ZIP soubor.") from exc


def prepare_template_upload(file_name: str, file_bytes: bytes, destination: Path) -> list[str]:
    """Prepare an uploaded .html/.htm file or .zip package and return template names."""
    suffix = Path(file_name).suffix.lower()
    if suffix == ".zip":
        safe_extract_template_zip(file_bytes, destination)
        return list_html_templates(destination)

    if suffix in {".html", ".htm"}:
        if len(file_bytes) > MAX_HTML_BYTES:
            raise TemplatePackageError("HTML šablona je větší než 20 MB.")

        destination.mkdir(parents=True, exist_ok=True)
        template_name = f"uploaded_template{suffix}"
        template_path = (destination / template_name).resolve()
        _ensure_child_path(template_path, destination)
        template_path.write_bytes(file_bytes)
        return [template_name]

    raise TemplatePackageError("Šablona musí být soubor .html, .htm nebo .zip.")


def list_html_templates(template_root: Path) -> list[str]:
    """Return HTML templates inside a previously extracted template package."""
    html_files = sorted(
        path.relative_to(template_root).as_posix()
        for path in template_root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".html", ".htm"}
    )
    if not html_files:
        raise TemplatePackageError("ZIP se šablonou musí obsahovat alespoň jeden .html nebo .htm soubor.")
    return html_files


def load_recipients(csv_bytes: bytes, delimiter_key: str) -> tuple[list[dict[str, Any]], list[str]]:
    """Load CSV data and return Jinja context rows plus ordered column names."""
    if len(csv_bytes) > MAX_DATA_BYTES:
        raise CsvInputError("Datový soubor je větší než 20 MB.")
    if delimiter_key not in ALLOWED_DELIMITERS:
        raise CsvInputError("Nepodporovaný oddělovač CSV.")

    text = _decode_text(csv_bytes)
    if not text.strip():
        raise CsvInputError("CSV soubor je prázdný.")

    delimiter = ALLOWED_DELIMITERS[delimiter_key]
    try:
        if delimiter is None:
            df = pd.read_csv(io.StringIO(text), sep=None, engine="python", dtype=str, keep_default_na=False)
        else:
            df = pd.read_csv(io.StringIO(text), sep=delimiter, engine="python", dtype=str, keep_default_na=False)
    except Exception as exc:
        raise CsvInputError(f"CSV se nepodařilo načíst: {exc}") from exc

    return _dataframe_to_records(df, "CSV")


def get_excel_sheet_names(excel_bytes: bytes) -> list[str]:
    """Return worksheet names from an uploaded Excel workbook."""
    if len(excel_bytes) > MAX_DATA_BYTES:
        raise CsvInputError("Datový soubor je větší než 20 MB.")
    try:
        workbook = pd.ExcelFile(io.BytesIO(excel_bytes), engine="openpyxl")
    except Exception as exc:
        raise CsvInputError(f"Excel se nepodařilo načíst: {exc}") from exc

    if not workbook.sheet_names:
        raise CsvInputError("Excel soubor neobsahuje žádný list.")
    return list(workbook.sheet_names)


def load_excel_recipients(excel_bytes: bytes, sheet_name: str | None = None) -> tuple[list[dict[str, Any]], list[str]]:
    """Load Excel data and return Jinja context rows plus ordered column names."""
    if len(excel_bytes) > MAX_DATA_BYTES:
        raise CsvInputError("Datový soubor je větší než 20 MB.")
    try:
        df = pd.read_excel(
            io.BytesIO(excel_bytes),
            sheet_name=sheet_name or 0,
            engine="openpyxl",
            dtype=str,
            keep_default_na=False,
        )
    except Exception as exc:
        raise CsvInputError(f"Excel se nepodařilo načíst: {exc}") from exc

    return _dataframe_to_records(df, "Excel")


def _dataframe_to_records(df: pd.DataFrame, source_label: str) -> tuple[list[dict[str, Any]], list[str]]:
    df.columns = [str(column).strip() for column in df.columns]

    if df.empty:
        raise CsvInputError(f"{source_label} musí obsahovat alespoň jeden datový řádek.")
    if len(df) > MAX_ROWS:
        raise CsvInputError(f"{source_label} obsahuje {len(df)} řádků; maximum je {MAX_ROWS}.")
    if any(not column for column in df.columns):
        raise CsvInputError(f"{source_label} obsahuje prázdný název sloupce.")
    if len(set(df.columns)) != len(df.columns):
        raise CsvInputError(f"{source_label} obsahuje duplicitní názvy sloupců.")

    df.fillna("", inplace=True)

    return df.to_dict(orient="records"), list(df.columns)


def generate_pdf_zip(recipients: list[dict[str, Any]], template_root: Path, template_relative_path: str) -> bytes:
    """Render one PDF per recipient and return them as an in-memory ZIP."""
    template_path = (template_root / template_relative_path).resolve()
    _ensure_child_path(template_path, template_root)
    if not template_path.is_file():
        raise TemplatePackageError("Vybraná HTML šablona neexistuje.")

    env = SandboxedEnvironment(undefined=StrictUndefined, autoescape=False)
    template_source = template_path.read_text(encoding="utf-8")
    template = env.from_string(template_source)

    output_buffer = io.BytesIO()
    with zipfile.ZipFile(output_buffer, "w", compression=zipfile.ZIP_DEFLATED) as output_zip:
        used_names: set[str] = set()
        for index, recipient in enumerate(recipients, start=1):
            try:
                rendered_html = template.render(recipient)
                pdf_bytes = HTML(
                    string=rendered_html,
                    base_url=template_path.parent.as_uri(),
                    url_fetcher=_restricted_url_fetcher(template_root),
                ).write_pdf(timeout=PDF_TIMEOUT_SECONDS)
            except Exception as exc:
                label = _recipient_label(recipient, index)
                raise GenerationError(f"Generování PDF selhalo pro řádek {index} ({label}): {exc}") from exc

            filename = _unique_filename(_pdf_filename(recipient, index), used_names)
            output_zip.writestr(filename, pdf_bytes)

    return output_buffer.getvalue()


def _decode_text(data: bytes) -> str:
    for encoding in ("utf-8-sig", "cp1250", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise CsvInputError("Kódování CSV není podporované.")


def _safe_archive_path(raw_name: str) -> Path:
    normalized_name = raw_name.replace("\\", "/")
    archive_path = PurePosixPath(normalized_name)
    if archive_path.is_absolute() or any(part in {"", ".", ".."} for part in archive_path.parts):
        raise TemplatePackageError(f"ZIP se šablonou obsahuje nebezpečnou cestu: {raw_name}")
    return Path(*archive_path.parts)


def _ensure_child_path(path: Path, parent: Path) -> None:
    resolved_parent = parent.resolve()
    try:
        path.resolve().relative_to(resolved_parent)
    except ValueError as exc:
        raise TemplatePackageError("Šablona se pokusila načíst soubor mimo nahraný balíček.") from exc


def _restricted_url_fetcher(template_root: Path):
    allowed_root = template_root.resolve()

    def fetcher(url: str) -> dict[str, Any]:
        parsed = urlparse(url)
        if parsed.scheme == "data":
            return default_url_fetcher(url)
        if parsed.scheme == "file":
            requested_path = Path(unquote(parsed.path)).resolve()
            _ensure_child_path(requested_path, allowed_root)
            return default_url_fetcher(url)
        raise TemplatePackageError(f"Externí odkaz na zdroj byl zablokován: {url}")

    return fetcher


def _pdf_filename(recipient: dict[str, Any], index: int) -> str:
    name = (
        recipient.get("fullName")
        or recipient.get("name")
        or recipient.get("Name")
        or recipient.get("jmeno")
        or recipient.get("Jmeno")
        or f"row_{index}"
    )
    safe_name = _slug_filename(str(name).strip()) or f"row_{index}"
    return f"{index:03d}_{safe_name}.pdf"


def _recipient_label(recipient: dict[str, Any], index: int) -> str:
    for key in ("fullName", "name", "Name", "jmeno", "Jmeno"):
        value = str(recipient.get(key, "")).strip()
        if value:
            return value
    return f"row {index}"


def _slug_filename(value: str) -> str:
    value = re.sub(r"\s+", "_", value)
    value = re.sub(r"[^\w.\-]+", "_", value, flags=re.UNICODE)
    return value.strip("._-")[:120]


def _unique_filename(filename: str, used_names: set[str]) -> str:
    candidate = filename
    stem, suffix = os.path.splitext(filename)
    counter = 2
    while candidate in used_names:
        candidate = f"{stem}_{counter}{suffix}"
        counter += 1
    used_names.add(candidate)
    return candidate
