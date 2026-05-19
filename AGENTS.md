# Repository Guidelines

## Project Structure & Module Organization

This repository generates invitation PDFs from a pipe-delimited CSV and an HTML template.

- `generator.py` is the main Python entry point. It loads recipient data, renders the Jinja2 template, and writes PDFs.
- `requirements.txt` lists runtime Python dependencies: `pandas`, `Jinja2`, and `WeasyPrint`.
- `input/data/manual-entry.csv` contains invitee rows. Expected headers are `fullName|spouse`.
- `input/template/pozvanka.html` is the active Jinja2/HTML template.
- `input/template/*_files/` contains template assets such as images and Office-export metadata.
- `vytvorene_pozvanky/` and `vytvorene_pozvanky.zip` are generated outputs.
- `docs/` and `howto.txt` contain project notes and setup instructions.

## Build, Test, and Development Commands

Create a local environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The project notes also support Conda:

```bash
conda create --name pozvanky python=3.10
conda activate pozvanky
conda install -c conda-forge pandas jinja2 weasyprint
```

Generate PDFs:

```bash
python3 generator.py
```

This reads `input/data/manual-entry.csv`, renders `input/template/pozvanka.html`, and writes one PDF per row into `vytvorene_pozvanky/`.

## Coding Style & Naming Conventions

Use Python 3.10-compatible code. Keep four-space indentation, type hints for function signatures, and short single-purpose functions as in `generator.py`. Constants for repository paths should stay near the top of the script in uppercase names, for example `CSV_FILE` and `OUTPUT_DIR`. Preserve existing CSV column names because the template expects them directly.

## Testing Guidelines

There is no automated test suite yet. For changes, run `python3 generator.py` and manually inspect at least one generated PDF for layout, images, names, and spouse text. When changing CSV parsing, verify both empty and non-empty `spouse` values. If tests are added later, place them under `tests/` and name files `test_*.py`.

## Commit & Pull Request Guidelines

Recent commit messages are short, imperative or descriptive, and often in Czech, for example `template fix - spodni blok` or `cleanup and howto`. Keep commits focused on one concern: generator logic, template changes, data updates, or regenerated outputs.

Pull requests should include a concise description, the command used to verify generation, and notes about any changed template assets or regenerated PDFs. Include screenshots or sample PDF comparisons when layout changes are visible.

## Agent-Specific Instructions

Do not delete or overwrite generated PDFs, input data, or template assets unless the task explicitly requires it. Treat recipient names and invitation data as sensitive working data; avoid pasting full lists into issues or PR text.
