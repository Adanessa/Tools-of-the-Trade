from pathlib import Path
from typing import Dict

def get_project_root() -> Path:
    return Path(__file__).resolve().parents[1]

def get_data_dirs() -> Dict[str, Path]:
    """
    Return a dict of key directories used by the project, creating them if needed:
      - dirty:   unprocessed input data
      - queries: where we write out query files
      - scraped: where we dump scraped JSON
      - raw:     any raw binary data (CSVs, images, etc.)
    """
    root = get_project_root()
    dirs = {
        "dirty_data":   root / "data" / "dirty_data",
        "queries": root / "data" / "queries",
        "scraped": root / "data" / "scraped_data",
        "raw":     root / "data" / "raw_data",
    }
    for p in dirs.values():
        p.mkdir(parents=True, exist_ok=True)
    return dirs
