# helpers/user_agents.py
import os
import logging
import requests
from typing import Optional

__all__ = ["get_user_agent"]

FALLBACK_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

def get_user_agent(api_key: Optional[str] = None) -> str:
    key = api_key or os.getenv("SCRAPEOPS_API_KEY")
    if not key:
        logging.debug("SCRAPEOPS_API_KEY not set; using fallback UA.")
        return FALLBACK_AGENT

    try:
        resp = requests.get(
            "https://headers.scrapeops.io/v1/user-agents",
            params={"api_key": key, "num_results": 5},
            timeout=5
        )
        resp.raise_for_status()
        data = resp.json().get("result") or []
        if data:
            return data[0]
        logging.warning("ScrapeOps returned empty result; using fallback UA.")
    except requests.RequestException as e:
        logging.warning(f"Failed to fetch UA from ScrapeOps: {e}")
    return FALLBACK_AGENT
