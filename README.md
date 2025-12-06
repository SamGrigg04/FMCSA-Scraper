# THIS README IS AI GENERATED
# Safer Web Scraper

A Python-based GUI tool for scraping FMCSA data, processing it, and uploading it to Google Sheets.

---

## Features

* Graphical interface for configuring scraper parameters
* Multi-threaded scraping with progress reporting
* Saves configuration changes persistently to `config.json`
* Integrates with Google Sheets using service account credentials
* Works both as a Python program and as a standalone executable

---

## Project Structure

```
Safer Web Scraper/
├─ config/
│  ├─ config.json          # Main configuration
│  └─ secrets.json         # Google Sheets service account info
├─ scrapers/
│  └─ scraperX.py          # Individual scraper modules
├─ utils/
│  ├─ config_utils.py      # Config & secrets handling
│  ├─ spreadsheet_utils.py # Google Sheets integration
│  └─ ...                  # Other utilities
├─ interface.py            # GUI
├─ main.py                 # Entry point for Python runs
├─ FMCSA_Scraper.spec      # PyInstaller build spec
└─ README.md
```

---

## Setup & Requirements

1. **Python 3.9+**
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Place your Google Sheets service account JSON in the project root and reference it in `config/secrets.json`.

---

## Running the App

### Using Python

```bash
python interface.py
```

### Using the Standalone EXE

1. Build the EXE with PyInstaller:

```bash
python -m PyInstaller FMCSA_Scraper.spec
```

2. Run `FMCSA_Scraper.exe`.
3. On first run, `config.json` will be created next to the EXE if it doesn’t exist.

---

## Configuration

* Configurable options are stored in `config/config.json`
* Secrets (like Google Sheets credentials) are stored in `config/secrets.json`
* Any file paths in the secrets file are automatically resolved in the EXE

---

## Notes

* Only file paths need special handling in the frozen EXE; plain strings like API tokens work as-is
* Progress reporting in the GUI is multi-threaded and updates in real-time
* You'll need to replace example_config.json and example_secrets.json with the real thing. config.json should generate upon running the program, but secrets.json has to be populated with the actual values

Do you want me to do that?
