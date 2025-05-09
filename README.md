# Tools of the Trade 🛠️

> Your friendly neighborhood scraping toolkit – because hunting data shouldn’t feel like rocket science (but it can if you want it to!).

## Table of Contents

* [Overview](#overview)
* [Features](#features)
* [Installation](#installation)
* [Getting Started](#getting-started)

  * [Generate Search Queries](#generate-search-queries)
  * [Run Searches](#run-searches)
* [Configuration](#configuration)
* [Project Structure](#project-structure)
* [Contributing](#contributing)
* [License](#license)

## Overview

**Tools of the Trade** is a growing collection of simple-yet-powerful Python scripts designed to supercharge your web scraping adventures. Whether you need to generate a mountain of search queries or blast them at search engines and collect results, we’ve got your back (and your queries).

*Currently included:*

* **generate\_search\_queries**: Turn a CSV of names (e.g., Local Authorities) into hundreds of Bing & DuckDuckGo search strings effortlessly.
* **run\_searches**: Fire off those queries via Playwright, handle retries with back-off, checkpoint completed queries, and save results to JSON.

More tools are brewing in the cauldron 🔮 – stay tuned!

---

## Features

* 🎯 **Targeted Query Generation**: Plug in a CSV and watch search patterns come to life.
* 🤖 **Automated Scraping**: Uses Playwright for reliable page loads and link extraction.
* ⏱️ **Smart Retry & Pause**: Customizable retries and random pauses to keep search engines happy.
* 🔄 **Checkpointing**: No more re-scraping the same queries – we remember what you’ve done.
* 🌐 **User-Agent Config**: Falls back to a solid default or integrates with ScrapeOps for rotating agents.

---

## Installation

1. **Clone this repo**

   ```bash
   git clone https://github.com/yourusername/tools-of-the-trade.git
   cd tools-of-the-trade
   ```
2. **Create a virtual environment & activate it**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate    # on macOS/Linux
   .\.venv\\Scripts\\activate  # on Windows
   ```
3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

---

## Getting Started

### Generate Search Queries

1. Prepare your CSV (it should have a column like `LA (name)`).
2. Run:

   ```bash
   python -m thebing_ducksearchinator_5000.generate_search_queries \
     -i data/dirty_data/test_data.csv \
     --column "LA (name)" \
     --bing-out data/queries/bing_search_queries.txt \
     --duck-out data/queries/duckduckgo_search_queries.txt
   ```
3. Watch as **hundreds** of queries get written to `data/queries/`.

> **Pro tip:** Adjust `SEARCH_PATTERNS` in `generate_search_queries.py` to tweak query templates.

### Run Searches

Once you’ve got your query files:

```bash
python -m thebing_ducksearchinator_5000.run_searches \
  --pause-min 1.0 \
  --pause-max 3.0 \
  --retries 3
# Or add --engine bing (or duckduckgo) to target just one.
```

Results will land in `data/scraped_data/` as JSON files:

* `bing_results.json`
* `duckduckgo_results.json`
* `completed_queries.json` (your checkpoint file!)
* `search_log.txt`

---

## Configuration

Create a `.env` file at the project root if you want fancy rotating user agents:

```dotenv
SCRAPEOPS_API_KEY=your_scrapeops_api_key_here
```

If you skip this, a reliable fallback agent will be used.

---

## Project Structure

```text
Tools-of-the-Trade/
├── data/
│   ├── dirty_data/         # Your input CSVs
│   ├── queries/            # Auto-generated search strings
│   └── scraped_data/       # JSON dumps & logs
├── helpers/
│   ├── paths.py            # Directory helpers
│   └── user_agents.py      # UA rotation logic
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

Contributions, issues, and feature requests are welcome! Feel free to:

1. Fork it (🍴)
2. Create your feature branch (`git checkout -b feature/AwesomeTool`)
3. Commit your changes (`git commit -m 'Add awesome scraping tool'`)
4. Push to the branch (`git push origin feature/AwesomeTool`)
5. Open a Pull Request – let’s make scraping great together!

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

---

*Stay curious, stay scraping! 💻☕*
