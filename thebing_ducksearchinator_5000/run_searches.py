import argparse
import asyncio
import json
import logging
import random
from pathlib import Path
from typing import Any, Dict, List, Set

from dotenv import load_dotenv
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Error

from helpers.paths import get_data_dirs
from helpers.user_agents import get_user_agent

load_dotenv()

ASCII_TITLE = r"""
 __                     _      _____             _              ____   ___   ___   ___  
/ _\ ___  __ _ _ __ ___| |__   \_   \_ __   __ _| |_ ___  _ __ | ___| / _ \ / _ \ / _ \ 
\ \ / _ \/ _` | '__/ __| '_ \   / /\/ '_ \ / _` | __/ _ \| '__||___ \| | | | | | | | | |
_\ \  __/ (_| | | | (__| | | /\/ /_ | | | | (_| | || (_) | |    ___) | |_| | |_| | |_| |
\__/\___|\__,_|_|  \___|_| |_\____/ |_| |_|\__,_|\__\___/|_|___|____/ \___/ \___/ \___/ 
                                                          |_____|                         
"""

DIRS = get_data_dirs()
LOG_FILE = DIRS["scraped"] / "search_log.txt"
CHECKPOINT = DIRS["scraped"] / "completed_queries.json"

# Engines config
SEARCH_ENGINES: Dict[str, Dict[str, Any]] = {
    "bing": {
        "name": "Bing",
        "query_file": DIRS["queries"] / "bing_search_queries.txt",
        "result_file": DIRS["scraped"] / "bing_results.json",
        "url_template": "https://www.bing.com/search?q={query}",
        "selector": "li.b_algo a",
    },
    "duckduckgo": {
        "name": "DuckDuckGo",
        "query_file": DIRS["queries"] / "duckduckgo_search_queries.txt",
        "result_file": DIRS["scraped"] / "duckduckgo_results.json",
        "url_template": "https://duckduckgo.com/?q={query}",
        "selector": "a[data-testid='result-title-a']",
    },
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE)
    ]
)

def load_completed() -> Set[str]:
    """
    Return a set of queries to avoid duplicates.
    """
    if CHECKPOINT.exists():
        try:
            return set(json.loads(CHECKPOINT.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            logging.warning("Checkpoint file corrupted; starting fresh.")
    return set()

def save_completed(completed: Set[str]) -> None:
    """
    Overwrite the checkpoint file with the full completed set.
    """
    CHECKPOINT.write_text(json.dumps(sorted(completed), indent=2), encoding="utf-8")

def collect_queue(selected: List[str], completed: Set[str]) -> List[tuple]:
    queue = []
    for key, cfg in SEARCH_ENGINES.items():
        if selected and key not in selected:
            continue
        if not cfg["query_file"].exists():
            logging.warning(f"Missing query file: {cfg['query_file']}")
            continue
        for line in cfg["query_file"].read_text(encoding="utf-8").splitlines():
            q = line.strip()
            if q and q not in completed:
                queue.append((key, q))
    random.shuffle(queue)
    logging.info(f"Queued up {len(queue)} queries")
    return queue

async def fetch_results(
    context: BrowserContext,
    cfg: Dict[str, Any],
    query: str
) -> List[str]:
    page: Page = await context.new_page()
    await page.goto(cfg["url_template"].format(query=query), wait_until="load")
    if cfg["name"] == "DuckDuckGo":
        try:
            await page.wait_for_selector(cfg["selector"], timeout=10_000)
        except Error:
            logging.debug(f"No selector match for DuckDuckGo on '{query}'")
    links = await page.eval_on_selector_all(cfg["selector"], "els => els.map(e => e.href)")
    await page.close()
    return links

async def run_all(selected: List[str], headless: bool, retries: int, pause: tuple):
    """
    Main entrypoint: spin up one browser, then for each queued (engine, query):
      - make new context (isolates UA/fingerprint)
      - try up to `retries` times with back-off
      - save JSON, update checkpoint, sleep between queries
    """
    print(ASCII_TITLE)
    completed = load_completed()
    queue = collect_queue(selected, completed)

    async with async_playwright() as pw:
        browser: Browser = await pw.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"]
        )

        for engine_key, query in queue:
            cfg = SEARCH_ENGINES[engine_key]
            # fresh context for each query
            context = await browser.new_context(
                user_agent=get_user_agent(),
                viewport={"width": 1280, "height": 720}
            )

            for attempt in range(1, retries+1):
                try:
                    logging.info(f"[{cfg['name']}] Attempt {attempt}/{retries}: {query}")
                    links = await fetch_results(context, cfg, query)
                    # load existing or start fresh
                    if cfg["result_file"].exists():
                        data = json.loads(cfg["result_file"].read_text(encoding="utf-8"))
                    else:
                        data = []
                    data.append({"query": query, "results": links})
                    cfg["result_file"].write_text(json.dumps(data, indent=2), encoding="utf-8")
                    logging.info(f"[{cfg['name']}] Got {len(links)} links for '{query}'")
                    break
                except Exception as e:
                    logging.error(f"[{cfg['name']}] Error on '{query}': {e}")
                    if attempt < retries:
                        await asyncio.sleep(random.uniform(*pause))
                    else:
                        logging.warning(f"[{cfg['name']}] Giving up on '{query}'")
                finally:
                    await context.close()

            # mark done
            completed.add(query)
            save_completed(completed)
            await asyncio.sleep(random.uniform(*pause))

        await browser.close()

def parse_args():
    p = argparse.ArgumentParser(description="Run search queries on Bing & DuckDuckGo")
    p.add_argument("--engine", choices=list(SEARCH_ENGINES.keys()),
                   help="Only run this engine (defaults to both)")
    p.add_argument("--no-headless", action="store_true",
                   help="Show browser window")
    p.add_argument("--retries", type=int, default=3,
                   help="How many times to retry a failed query")
    p.add_argument("--pause-min", type=float, default=1.0,
                   help="Min seconds to wait between queries")
    p.add_argument("--pause-max", type=float, default=3.0,
                   help="Max seconds to wait between queries")
    return p.parse_args()

def main():
    args = parse_args()
    engines = [args.engine] if args.engine else []
    asyncio.run(run_all(
        selected=engines,
        headless=not args.no_headless,
        retries=args.retries,
        pause=(args.pause_min, args.pause_max)
    ))

if __name__ == "__main__":
    main()
