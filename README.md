# Tools of the Trade 🛠️

> Your friendly neighborhood scraping & validation toolkit—data hunting shouldn’t feel like rocket science (but it can if you want it to!).

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Getting Started](#getting-started)
  - [SMTP Email Validator](#smtp-email-validator)
  - [Generate Search Queries](#generate-search-queries)
  - [Run Searches](#run-searches)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Overview

**Tools of the Trade** is a growing collection of simple-yet-powerful Python scripts to supercharge your data scraping and validation adventures. From crafting search queries to verifying email deliverability, we’ve got your back—and your data.

_Currently included:_

- **generate_search_queries**: Turn a CSV of terms (e.g., Local Authorities, game consoles, product SKUs, or any custom list) into hundreds of Bing & DuckDuckGo query strings.
- **run_searches**: Fire off those queries via Playwright, handle retries with back-off, checkpoint completed items, and dump results to JSON.
- **smtp_email_validator**: Syntax-check, fetch MX records, and SMTP-handshake validate email addresses without sending real emails.

More tools are brewing in the cauldron 🔮 – stay tuned!

---

## Features

- ✉️ **Email Validation**: Validate syntax, retrieve MX hosts, and perform an SMTP handshake to confirm mailbox existence.
- 🎯 **Targeted Query Generation**: Plug in a CSV and watch search patterns come to life for Bing or DuckDuckGo.
- 🤖 **Automated Scraping**: Leverages Playwright for rock-solid page loads and data extraction.
- ⏱️ **Smart Retry & Pause**: Customizable retries & random delays to keep servers happy.
- 🔄 **Checkpointing**: No more re-scraping the same items—resume where you left off.
- 🌐 **User-Agent Config**: Built-in fallback or integrate with ScrapeOps for rotating UAs.

---

## Installation

1. **Clone this repo**
   ```bash
   git clone https://github.com/Adanessa/tools-of-the-trade.git
   cd tools-of-the-trade
   ```
2. **Create & activate a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate    # macOS/Linux
   .\.venv\\Scripts\\activate  # Windows
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## Getting Started

### SMTP Email Validator

1. **Drop your files** (CSV or TXT) into `data/dirty_data/` (or reference them directly).
2. **Run the validator**:
   ```bash
   # Process every .csv/.txt under data/dirty_data/
   python -m smtp_validator_4000.smtp_validator -c email

   # Or target specific file(s) by name in data/dirty_data/
   python -m smtp_validator_4000.smtp_validator -f data_snippet.csv -c email
   python -m smtp_validator_4000.smtp_validator -f data_snippet.csv,example2.csv -c email

   # Or use full paths
   python -m smtp_validator_4000.smtp_validator -f path/to/custom_list.csv -c email
   ```
3. **Key options**:
   - `--file` (`-f`): Comma-separated names or paths to CSV/TXT files. Names without paths are looked up under `data/dirty_data/`.
   - `--column` (`-c`): Header name for the email column (defaults to the first column).
   - `--timeout` (`-t`): SMTP connect timeout in seconds (default: `10`).
   - `--output` (`-o`): JSON output path (default: `data/validation_results.json`).

Results include syntax validity, MX hosts, SMTP handshake success, and errors—dumped into your JSON file.

### Generate Search Queries

1. Prepare a CSV with your list of terms (e.g., a column named `LA (name)`, `ConsoleName`, `ProductSKUs`, etc.).
2. Run:
   ```bash
   python -m thebing_ducksearchinator_5000.generate_search_queries 
     --column "LA (name)"
     --bing-out data/queries/bing_search_queries.txt
     --duck-out data/queries/duckduckgo_search_queries.txt
   ```
3. Watch as your customized queries land in `data/queries/`.

> **Pro tip:** Tweak `SEARCH_PATTERNS` in `generate_search_queries.py` to alter query templates.

### Run Searches

```bash
python -m thebing_ducksearchinator_5000.run_searches 
  --pause-min 1.0 
  --pause-max 3.0 
  --retries 3
# Or add --engine bing (or duckduckgo) to focus on one.
# DuckDuck is being annoying atm and you will need to run it with --no-headless arg
```


Results appear in `data/scraped_data/`:

- `bing_results.json`
- `duckduckgo_results.json`
- `completed_queries.json`
- `search_log.txt`

---

## Configuration

Create a `.env` in the project root for rotating user agents:
```dotenv
SCRAPEOPS_API_KEY=your_scrapeops_api_key_here
```
Skip it for a solid default UA.

---

## Project Structure

```text
Tools-of-the-Trade/
├── data/
│   ├── dirty_data/         # Your raw CSV/TXT inputs (e.g., email lists)
│   ├── queries/            # Auto-generated search strings
│   └── scraped_data/       # JSON dumps & logs
├── helpers/
│   ├── paths.py            # Directory helpers
│   └── user_agents.py      # UA rotation logic
├── smtp_validator_4000/
│   └── smtp_validator.py
├── thebing_ducksearchinator_5000/
│   ├── generate_search_queries.py
│   └── run_searches.py
├── requirements.txt
├── .env.example            # Sample env file
├── LICENSE
└── README.md
```

---

## Contributing

Contributions, issues, and feature requests are welcome! To contribute:

1. Fork it 🍴
2. Create your branch (`git checkout -b feature/AwesomeTool`)
3. Commit your changes (`git commit -m 'Add awesome tool'`)
4. Push (`git push origin feature/AwesomeTool`)
5. Open a Pull Request—let’s make data magic happen!

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.

---

_Stay curious, stay scraping, stay validating! 🚀_
