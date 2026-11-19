"""Export factual tables from Kiranico's public MH3U pages into SQLite."""

import argparse
import hashlib
import json
import re
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
from threading import Event
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


HOST = "https://kiranico.com"
ROOT = "/en/mh3u"
VARIABLES = re.compile(r"window\.js_vars\s*=\s*")
WEAPONS = (
    "greatsword", "longsword", "sword", "dualblades", "hammer", "huntinghorn",
    "lance", "gunlance", "switchaxe", "lightbowgun", "heavybowgun", "bow",
)
ARMOR_PARTS = ("armor/head", "armor/chest", "armor/arms", "armor/waist", "armor/legs")
HTML_TABLES = ("item/veggie-elder", "item/fleet", "item/village-request")
SECTIONS = ("quest", "map", "monster", "armor/skill", "armor/jewel", *ARMOR_PARTS,
            "item", "item/combo", "item/veggie-elder", "item/fleet", "item/village-request")
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml",
}
ENTITY_KEYS = {
    "map": "map", "monster": "monster", "quest": "quest", "item": "item",
    "weapons": "weapon", "jewels": "decoration", "itemcombos": "combination",
    "skilltree": "skill", "armor": "armor", "armors": "armor",
}


def fetch(path, cache):
    file = cache / (hashlib.sha256(path.encode()).hexdigest() + ".html")
    if file.exists():
        return file.read_text(encoding="utf-8")
    sleep(0.25)
    request = Request(HOST + path, headers=HEADERS)
    with urlopen(request, timeout=18) as response:
        if urlsplit(response.url).hostname != "kiranico.com":
            raise ValueError(f"unexpected redirect to {response.url}")
        page = response.read().decode("utf-8")
    if "Kiranico" not in page or "MH3U" not in page:
        raise ValueError("unexpected page body")
    file.write_text(page, encoding="utf-8")
    return page


def links(page):
    result = {}
    for anchor in BeautifulSoup(page, "html.parser").select("a[href]"):
        url = urlsplit(anchor["href"])
        if url.netloc not in ("", "kiranico.com") or not url.path.startswith(ROOT + "/"):
            continue
        label = anchor.get_text(" ", strip=True)
        if label and url.path not in result:
            result[url.path] = label
    return result


def variables(page):
    match = VARIABLES.search(page)
    return json.JSONDecoder().raw_decode(page, match.end())[0] if match else {}


def facts(value):
    if isinstance(value, dict):
        return {key: facts(child) for key, child in value.items()
                if not key.endswith("description")}
    if isinstance(value, list):
        return [facts(child) for child in value]
    return value


def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def named_refs(value):
    if isinstance(value, dict):
        link = urlsplit(value.get("link") or "").path
        if "id" in value and value.get("local_name") and link.startswith(ROOT + "/"):
            section = link.removeprefix(ROOT + "/").split("/")
            kind = section[0]
            if kind == "armor":
                kind = "skill" if section[1] == "skill" else "armor"
            yield kind, link, value
        for child in value.values():
            yield from named_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from named_refs(child)


def write_page(db, path, page):
    payload = variables(page)
    for key, values in payload.items():
        kind = ENTITY_KEYS.get(key)
        if not kind:
            continue
        rows = values if isinstance(values, list) else [values]
        for row in rows:
            if not isinstance(row, dict) or "id" not in row:
                continue
            name = row.get("local_name") or (row.get("item") or {}).get("local_name")
            row_url = row.get("link") or HOST + path
            db.execute("INSERT OR REPLACE INTO entities VALUES (?, ?, ?, ?, ?)",
                       (kind, row["id"], name, row_url, encode(facts(row))))

    for kind, link, row in named_refs(payload):
        flat = {key: value for key, value in row.items() if not isinstance(value, (dict, list))}
        db.execute("INSERT OR IGNORE INTO references_by_id VALUES (?, ?, ?, ?, ?)",
                   (kind, row["id"], row["local_name"], HOST + link, encode(facts(flat))))

    if "map" in payload:
        game_map = payload["map"]
        for pos, item in enumerate(game_map.get("items") or [], 1):
            pivot = item["pivot"]
            db.execute("INSERT INTO gathering VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (game_map["id"], pos, game_map["local_name"], item["id"],
                        item["local_name"], (pivot.get("rank") or {}).get("local_name"),
                        (pivot.get("maparea") or {}).get("local_name"),
                        (pivot.get("mapgathertype") or {}).get("local_name"),
                        pivot.get("percentage"), HOST + path))
    if "quest" in payload:
        quest = payload["quest"]
        for pos, item in enumerate(quest.get("items") or [], 1):
            pivot = item["pivot"]
            db.execute("INSERT OR REPLACE INTO quest_rewards VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (quest["id"], pos, item["id"], item["local_name"], pivot.get("type"),
                        pivot.get("quantity"), pivot.get("percentage")))
    if path.removeprefix(ROOT + "/") in HTML_TABLES:
        for table_number, table in enumerate(BeautifulSoup(page, "html.parser").select("table"), 1):
            for row_number, row in enumerate(table.find_all("tr"), 1):
                cells = [{"text": cell.get_text(" ", strip=True),
                          "links": [a["href"] for a in cell.select("a[href]")]}
                         for cell in row.find_all(["th", "td"], recursive=False)]
                if cells:
                    db.execute("INSERT INTO public_table_rows VALUES (?, ?, ?, ?)",
                               (path, table_number, row_number, encode(cells)))
    return int(bool(payload))


def run(db, cache, item_details, armor_details):
    db.executescript("""
        CREATE TABLE pages (path TEXT PRIMARY KEY, result TEXT NOT NULL, structured INTEGER);
        CREATE TABLE catalog_links (
            index_path TEXT NOT NULL, path TEXT NOT NULL, name TEXT NOT NULL,
            PRIMARY KEY (index_path, path)
        );
        CREATE TABLE entities (
            kind TEXT NOT NULL, source_id INTEGER NOT NULL, name TEXT, source_url TEXT NOT NULL,
            data_json TEXT NOT NULL, PRIMARY KEY(kind, source_id)
        );
        CREATE TABLE references_by_id (
            kind TEXT NOT NULL, source_id INTEGER NOT NULL, name TEXT NOT NULL,
            source_url TEXT NOT NULL, data_json TEXT NOT NULL, PRIMARY KEY(kind, source_id)
        );
        CREATE TABLE gathering (
            map_id INTEGER NOT NULL, position INTEGER NOT NULL, map TEXT NOT NULL,
            item_id INTEGER NOT NULL, item TEXT NOT NULL, rank TEXT, area TEXT, method TEXT,
            chance REAL, source_url TEXT NOT NULL, PRIMARY KEY (map_id, position)
        );
        CREATE TABLE quest_rewards (
            quest_id INTEGER NOT NULL, position INTEGER NOT NULL, item_id INTEGER NOT NULL,
            item TEXT NOT NULL, pool TEXT, quantity INTEGER, chance REAL,
            PRIMARY KEY (quest_id, position)
        );
        CREATE TABLE public_table_rows (
            path TEXT NOT NULL, table_number INTEGER NOT NULL, row_number INTEGER NOT NULL,
            cells_json TEXT NOT NULL, PRIMARY KEY(path, table_number, row_number)
        );
        CREATE INDEX gathering_by_item ON gathering(item_id);
        CREATE INDEX rewards_by_item ON quest_rewards(item_id);
    """)
    roots = [f"{ROOT}/{section}" for section in SECTIONS]
    weapon_paths = [f"{ROOT}/weapon/{weapon}" for weapon in WEAPONS]
    rate_limited = Event()

    def download(path):
        if rate_limited.is_set():
            return path, None, "rate limited"
        try:
            return path, fetch(path, cache), None
        except HTTPError as exc:
            if exc.code == 429:
                rate_limited.set()
            return path, None, f"HTTP {exc.code}"
        except (OSError, URLError, ValueError) as exc:
            return path, None, str(exc)

    catalogs = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        for path, page, error in pool.map(download, roots + weapon_paths):
            if error:
                db.execute("INSERT INTO pages VALUES (?, ?, NULL)", (path, error))
                continue
            structured = write_page(db, path, page)
            db.execute("INSERT INTO pages VALUES (?, 'ok', ?)", (path, structured))
            if path in roots:
                catalogs[path] = links(page)
                db.executemany("INSERT INTO catalog_links VALUES (?, ?, ?)",
                               ((path, link, name) for link, name in catalogs[path].items()))

        paths = set()
        for path, options in catalogs.items():
            section = path.removeprefix(ROOT + "/")
            if section not in ("quest", "monster", "map", "armor/skill", "item", *ARMOR_PARTS):
                continue
            if section in ARMOR_PARTS and not armor_details:
                continue
            for link in options:
                if not link.startswith(path + "/") or link in roots:
                    continue
                expected_segments = 4 if section == "quest" else 2
                if len(link.removeprefix(path).split("/")) != expected_segments:
                    continue
                if section == "item" and not item_details and not link.endswith("/iron-ore"):
                    continue
                paths.add(link)

        print(f"{len(paths)} detail pages queued", flush=True)
        completed = 0
        for path, page, error in pool.map(download, sorted(paths)):
            if error == "HTTP 429":
                raise RuntimeError("Kiranico returned HTTP 429. Retry later using the same cache.")
            if error:
                db.execute("INSERT INTO pages VALUES (?, ?, NULL)", (path, error))
            else:
                structured = write_page(db, path, page)
                db.execute("INSERT INTO pages VALUES (?, 'ok', ?)", (path, structured))
            completed += 1
            if completed % 50 == 0:
                print(f"{completed}/{len(paths)} detail pages processed", flush=True)

    for row in db.execute("SELECT kind, COUNT(*) FROM entities GROUP BY kind ORDER BY kind"):
        print(*row)
    for table in ("gathering", "quest_rewards"):
        print(table, *db.execute(f"SELECT COUNT(*), COUNT(chance) FROM {table}").fetchone())
    if db.execute("PRAGMA integrity_check").fetchone() != ("ok",):
        raise ValueError("SQLite integrity check failed")


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--cache", type=Path, required=True)
    cli.add_argument("--output", type=Path, required=True)
    cli.add_argument("--item-details", action="store_true", help="also request every item detail page")
    cli.add_argument("--armor-details", action="store_true", help="also request every armor detail page")
    args = cli.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb"):
        pass
    try:
        with closing(sqlite3.connect(args.output)) as db, db:
            run(db, args.cache, args.item_details, args.armor_details)
    except Exception:
        args.output.unlink(missing_ok=True)
        raise


if __name__ == "__main__":
    main()
