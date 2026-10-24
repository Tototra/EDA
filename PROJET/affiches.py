import json
import os
import re
from pathlib import Path
import requests

CACHE = Path(__file__).parent / "affiches.json"
SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
IMAGE_URL = "https://image.tmdb.org/t/p/w185"


def clean_title(title):
    year = re.search(r"\((\d{4})\)\s*$", title).group(1)
    name = re.sub(r"\s*\(.*?\)", "", title).strip()
    m = re.match(r"(.*), (The|A|An|Il|La|Le|Les)$", name)
    if m:
        name = m.group(2) + " " + m.group(1)
    return name, year


def search(title, key):
    name, year = clean_title(title)
    params = {"query": name, "year": year}
    headers = {}
    if len(key) > 40:
        headers["Authorization"] = "Bearer " + key
    else:
        params["api_key"] = key
    r = requests.get(SEARCH_URL, params=params, headers=headers, timeout=10)
    if not r.ok:
        return None
    results = [x for x in r.json().get("results", []) if x.get("poster_path")]
    return IMAGE_URL + results[0]["poster_path"] if results else ""


def posters(titles):
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    key = os.environ.get("TMDB_API_KEY")
    updated = False
    for t in titles:
        if key and t not in cache:
            url = search(t, key)
            if url is not None:
                cache[t] = url
                updated = True
    if updated:
        CACHE.write_text(json.dumps(cache))
    return {t: cache.get(t, "") for t in titles}
