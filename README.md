# Facebook Ingestor

![Python](https://img.shields.io/badge/python-3.13-blue)
![License](https://img.shields.io/github/license/FrancescoASessa/facebook-ingestor)
![Last Commit](https://img.shields.io/github/last-commit/FrancescoASessa/facebook-ingestor)
[![Code Quality](https://github.com/FrancescoASessa/facebook-ingestor/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/FrancescoASessa/facebook-ingestor/actions/workflows/ci.yml)

Facebook Ingestor is an asynchronous, CLI-driven data ingestion tool designed to extract structured business information from Facebook pages using headless browser automation.

The project is built with scalability, observability, and production-readiness in mind, and is suitable for batch jobs, scheduled executions, and containerized environments.

## Features

- Asynchronous scraping with configurable parallelism
- Headless browser automation via `nodriver`
- Mobile emulation and network optimization
- Robust cookie handling
- Structured JSON output per page
- Centralized logging and observability
- Optional hardware resource monitoring
- Final execution report (saved vs failed pages)
- Enterprise-grade CLI powered by `Click`

## Project Structure

```text
facebook-ingestor/
│
├── app/
│   ├── __init__.py
│   ├── main.py              # Click-based CLI entrypoint
│   ├── orchestrator.py      # Parallel execution and workers
│   ├── browser_setup.py     # Browser configuration and emulation
│   ├── scraper.py           # Page scraping and persistence
│   ├── cookies.py           # Cookie handling logic
│   ├── utils.py             # Shared utilities
│   ├── observability.py     # Logging and resource monitoring
│   └── reporting.py         # Final scrape report aggregation
│   └── performance.py       # Timing utilities
│
├── data/                    # Output directory (JSON files)
├── urls.txt                 # Input URLs (one per line)
├── README.md
└── requirements.txt
```

## Usage
The application is executed via a Click-based command-line interface.
```bash
python -m app.main -f urls.txt -b 5
```

## Command-Line Options

The CLI exposes a set of options designed for batch execution and operational flexibility.

| Option | Description | Default |
|------|------------|---------|
| `-f, --urls-file` | Path to a text file containing one URL per line | **required** |
| `-b, --browsers` | Number of parallel browser workers | `10` |
| `--log-resources / --no-log-resources` | Enable or disable hardware resource logging | enabled |
| `-h, --help` | Show CLI help | — |

### Example

```bash
python -m app.main \
  --urls-file urls.txt \
  --browsers 8 \
  --no-log-resources
```

## Input Format
The input file must contain one Facebook page URL per line.
Example urls.txt:

```text
https://www.facebook.com/266105353548024
https://www.facebook.com/887053858059957
https://www.facebook.com/1646876462219866
```

URLs are automatically normalized to target the /about section of each page.

## Output
Each successfully scraped page generates a JSON file in the data/ directory.

### Output File Naming
- Filenames are derived deterministically from the Facebook page URL
- Unsafe filesystem characters are removed
- Collisions are avoided by design

Example:
```bash
data/266105353548024_about.json
```


# Disclaimer
This tool is intended for legitimate data ingestion and analysis use cases.
Users are responsible for ensuring compliance with Facebook’s Terms of Service and applicable laws.