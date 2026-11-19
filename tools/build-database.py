"""Build the Android MH3U asset from local Dex, legacy, and Kiranico databases."""
import argparse
import json
import re
import sqlite3
import unicodedata
from collections import defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "app/src/main"
DATA_VERSION = 1
ELEMENTS = dict(FI="Fire", WA="Water", TH="Thunder", IC="Ice", DR="Dragon",
                PO="Poison", PA="Paralysis", SL="Sleep", BL="Blastblight", BA="Blastblight")
MAPS = (None, 1, 3, 4, 5, 6, 7, 8, 10, 9, 13, 12, 11, 14, 15,
        3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 10, 10, 13, 13)
RANKS = {1: "LR", 2: "HR", 3: "G"}
DRAWABLES = {p.stem for p in (ASSETS / "icon-res/drawable").iterdir() if p.is_file()}
COLORS = dict(white=0, purple=1, yellow=2, pink=3, green=4, blue=5,
              red=6, cyan=7, orange=8, magenta=9, grey=10, gray=10)


def match_name(value):
    plain = unicodedata.normalize("NFKD", (value or "").casefold())
    return re.sub(r"[^\w+]", "", plain)


def icon(kind, original, subtype):
    if kind == "Armor":
        return "icon_armor_" + subtype.lower()
    if kind == "Weapon":
        return "icon_" + subtype.lower().replace(" ", "_")
    if kind == "Decoration":
        return "icon_jewel"
    if kind == "Monster":
        old_name = (original or "").removeprefix("MH3U-").removesuffix("_Icon.png")
        candidates = ("monster_" + re.sub(r"\W+", "_", name.lower())
                      for name in (subtype, old_name))
        return next((name for name in candidates if name in DRAWABLES), "icon_quest_mark")
    name = "icon_" + (original or "").split("-")[0].split(".")[0].lower()
    return name if name in DRAWABLES else "icon_quest_mark"


def icon_color(original):
    return COLORS.get(Path(original or "").stem.rpartition("-")[2].lower(), 0)


def insert(db, table, **values):
    columns = ", ".join(values)
    params = ", ".join("?" for _ in values)
    db.execute(f"INSERT INTO {table} ({columns}) VALUES ({params})", tuple(values.values()))


def localized(column, english, japanese=None):
    return {**{column + suffix: english or "" for suffix in ("", "_de", "_fr", "_es", "_it")},
            column + "_ja": japanese or english or ""}


def preserve_dex(db):
    for (table,) in db.execute("SELECT name FROM dex.sqlite_schema WHERE type='table' ORDER BY name"):
        db.execute(f'CREATE TABLE "dex_{table}" AS SELECT * FROM dex."{table}"')


def map_dex_items(db):
    names = defaultdict(list)
    for item in db.execute("SELECT _id,name FROM items WHERE type IN ('', 'Decoration')"):
        names[match_name(item["name"])].append(item["_id"])
    result = {}
    for item in db.execute("SELECT n.*,i.* FROM dex.ID_Itm_Name n JOIN dex.DB_Itm i USING (Itm_ID)"):
        source_id = item["Itm_ID"]
        name = item["Itm_Name_0"]
        candidates = names[match_name(name)]
        if len(candidates) == 1:
            item_id, = candidates
        else:
            item_id = 100_000 + source_id
            insert(db, "items", _id=item_id, **localized("name", name or item["Itm_Name_3"], item["Itm_Name_3"]),
                   type="", sub_type="", rarity=item["Itm_Rare"] or 0,
                   carry_capacity=item["Itm_Max"] or 0, buy=item["Itm_Buy"], sell=item["Itm_Sell"],
                   **localized("description", ""), icon_name="icon_quest_mark", icon_color=0, account=0)
        result[source_id] = item_id
    return result


def map_dex_monsters(db):
    names = defaultdict(list)
    for row in db.execute("SELECT _id,name FROM monsters"):
        names[match_name(row["name"])].append(row["_id"])
    result = {}
    for row in db.execute("SELECT * FROM dex.ID_Mon_Name WHERE Mon_ID > 0"):
        candidates = names[match_name(row["Mon_Name_0"])]
        if len(candidates) == 1:
            result[row["Mon_ID"]], = candidates
            db.execute("UPDATE monsters SET name_ja=? WHERE _id=?",
                       (row["Mon_Name_3"] or "", candidates[0]))
    return result


def import_quests(db, items, monsters):
    monster_links = set()
    query = """SELECT q.*,n.Qst_Name_0,n.Qst_Name_3,g.Qst_Goal_0,g.Qst_Goal_3
               FROM dex.DB_Qst q JOIN dex.ID_Qst_Name n USING (Qst_ID)
               JOIN dex.ID_Qst_Goal g USING (Qst_ID) ORDER BY q.Qst_ID"""
    for row in db.execute(query):
        level = row["Qst_Lv_ID"]
        if level < 21:
            hub, stars = "Village", level - 11
            rank = "LR" if stars < 6 else "HR"
        else:
            hub, stars = ("Guild", level - 20) if level < 29 else ("Event", level - 28)
            rank = "LR" if stars < 3 else "HR" if stars < 6 else "G"
        quest_id = row["Qst_ID"]
        insert(db, "quests", _id=quest_id, sort_order=quest_id,
               **localized("name", row["Qst_Name_0"] or row["Qst_Name_3"], row["Qst_Name_3"]),
               **localized("goal", row["Qst_Goal_0"] or row["Qst_Goal_3"], row["Qst_Goal_3"]),
               hub=hub, type=max(0, row["Qst_Urgent_ID"]), rank=rank,
               goal_type={1: 3, 2: 1, 3: 0, 4: 2, 7: 5}.get(row["Qst_Type_ID"], 0),
               **localized("sub_goal", ""), **localized("flavor", ""),
               hunter_type=0, stars=stars, location_id=MAPS[row["Loc_ID"]],
               time_limit=row["Time"], fee=row["Fee"], reward=row["Reward"], hrp=row["HRP"], metadata=0)
        for slot in range(1, 9):
            monster_id = monsters.get(row[f"Mon{slot}_ID"])
            if monster_id:
                monster_links.add((monster_id, quest_id))
    for row in db.execute("SELECT * FROM legacy.arena_quests"):
        quest_id = 10_000 + row["_id"]
        insert(db, "quests", _id=quest_id, sort_order=quest_id,
               **localized("name", row["name"]), **localized("goal", row["goal"]),
               **localized("sub_goal", ""), **localized("flavor", ""),
               hub="Arena", type=0, rank="", goal_type=1, hunter_type=0, stars=0,
               location_id=row["location_id"], time_limit=0, fee=0, reward=row["reward"], metadata=0)
        insert(db, "mh3u_arena_times", quest_id=quest_id, participants=row["num_participants"],
               time_s=row["time_s"], time_a=row["time_a"], time_b=row["time_b"])
    monster_links.update((monster, 10_000 + arena)
                         for monster, arena in db.execute("SELECT monster_id,arena_id FROM legacy.monster_to_arena"))
    db.executemany("INSERT INTO monster_to_quest (monster_id,quest_id,unstable,hyper) VALUES (?,?,0,0)",
                   sorted(monster_links))
    for row in db.execute("SELECT * FROM dex.DB_Itm_Qst ORDER BY ID"):
        insert(db, "quest_rewards", _id=row["ID"], quest_id=row["Qst_ID"],
               item_id=items[row["Itm_ID"]], reward_slot=row["Type"] if row["Region"] == "A" else row["Type"] + " (" + row["Region"] + ")",
               stack_size=row["Quant"],
               percentage=round(row["Percentage"] * 100))
        insert(db, "mh3u_quest_reward_regions", reward_id=row["ID"], region=row["Region"])
    db.execute("""INSERT INTO quest_rewards (quest_id,item_id,reward_slot,stack_size,percentage)
                  SELECT 10000+arena_id,item_id,'A',stack_size,percentage FROM legacy.arena_rewards""")


def import_item_sources(db, items, monsters):
    db.execute("""INSERT INTO gathering (item_id,location_id,area,site,rank)
                  SELECT item_id,location_id,area,site,rank FROM legacy.gathering
                  WHERE location_id IN (1,2)""")
    query = """SELECT g.*,a.Loc_Ara_0 FROM dex.DB_Itm_Loc g
               JOIN dex.ID_Loc_Ara a USING (Loc_Ara_ID) ORDER BY g.ID"""
    for row in db.execute(query):
        insert(db, "gathering", item_id=items[row["Itm_ID"]], location_id=MAPS[row["Loc_ID"]],
               area=row["Loc_Ara_0"], site={1: "Gather", 2: "Fish", 3: "Mine", 4: "Bug"}[row["Loc_GetType_ID"]],
               rank=RANKS[row["Rank_ID"]])
    query = """SELECT r.*,t.Mon_GetItmType_0 FROM dex.DB_Itm_Mon r
               JOIN dex.ID_Mon_GetItmType t USING (Mon_GetItmType_ID) ORDER BY r.ID"""
    represented = set()
    for row in db.execute(query):
        monster_id = monsters.get(row["Mon_ID"])
        if not monster_id or row["Rank_ID"] not in RANKS or row["Percentage"] is None or row["Itm_ID"] not in items:
            continue
        represented.add(monster_id)
        insert(db, "hunting_rewards", item_id=items[row["Itm_ID"]], condition=row["Mon_GetItmType_0"],
               monster_id=monster_id, rank=RANKS[row["Rank_ID"]], stack_size=row["Quant"] or 1,
               percentage=round(row["Percentage"] * 100))
    db.executemany("""INSERT INTO hunting_rewards (item_id,condition,monster_id,rank,stack_size,percentage)
                      VALUES (?,?,?,?,?,?)""",
                   (tuple(row) for row in db.execute("""SELECT item_id,condition,monster_id,rank,stack_size,percentage
                                                        FROM legacy.hunting_rewards ORDER BY _id""")
                    if row["monster_id"] not in represented))


def import_charms(db):
    names = {match_name(row["name"]): row["_id"] for row in db.execute("SELECT _id,name FROM skill_trees")}
    trees = {row["SklTree_ID"]: names.get(match_name(row["SklTree_Name_0"]))
             for row in db.execute("SELECT SklTree_ID,SklTree_Name_0 FROM dex.ID_SklTree_Name")}
    charms = set()
    for row in db.execute("SELECT * FROM dex.DB_Tls"):
        first, second = trees.get(row["SklTree1_ID"]), trees.get(row["SklTree2_ID"])
        if first and (second or row["SklTree2_ID"] in (-1, None)):
            charms.add((row["Slot"], first, row["SklTree1_Num"], second, row["SklTree2_Num"]))
    db.executemany("""INSERT INTO charms (num_slots,skill_tree_1_id,skill_tree_1_amount,skill_tree_2_id,skill_tree_2_amount)
                      VALUES (?,?,?,?,?)""", sorted(charms, key=lambda row: tuple(x or 0 for x in row)))


def weapon_elements(encoded):
    return [(ELEMENTS.get(code, ""), int(value)) for code, value in re.findall(r"([A-Z]{2})(\d+)", encoded or "")]


def import_armor_families(db):
    slots = ("head", "body", "arms", "waist", "legs")
    groups = defaultdict(list)
    for row in db.execute("SELECT a.*,i.name,i.rarity FROM armor a JOIN items i USING (_id) ORDER BY a._id"):
        # Most MH3U pieces use “family piece [tier]”. Singletons retain the whole name.
        match = re.fullmatch(r"(.+?) [^ ]+( [A-Z])?", row["name"])
        family = (match[1] + (match[2] or "")) if match else row["name"]
        groups[family, row["rarity"], row["gender"], row["hunter_type"]].append(row)
    for (name, rarity, _, hunter), members in groups.items():
        members_by_slot = {row["slot"].lower(): row for row in members}
        if len(members_by_slot) != len(members):
            subsets = [(row["name"], {row["slot"].lower(): row}) for row in members]
        elif len(members) == 1:
            subsets = [(members[0]["name"], members_by_slot)]
        else:
            subsets = [(name, members_by_slot)]
        for title, pieces in subsets:
            family_id = min(row["_id"] for row in pieces.values())
            ids = {slot + "_id": pieces[slot]["_id"] if slot in pieces else 0 for slot in slots}
            insert(db, "armor_families", _id=family_id, **localized("name", title),
                   rarity=rarity, **ids, hunter_type=hunter)
            db.executemany("UPDATE armor SET family=? WHERE _id=?",
                           ((family_id, row["_id"]) for row in pieces.values()))


def bow_coatings(value):
    bits = {"Power": 10, "C.Range": 6, "Poison": 5, "Para": 4, "Sleep": 3,
            "Exhaust": 2, "Slime": 1, "Paint": 0}
    return sum(1 << bits[name] for name, qty in re.findall(r"([^|]+) (\d+)", value or "")
               if name in bits and int(qty) > 0)


def import_weapons(db):
    rows = db.execute("SELECT w.*,i.name FROM legacy.weapons w JOIN items i USING (_id)").fetchall()
    lookup = defaultdict(list)
    for weapon in rows:
        lookup[(weapon["wtype"], match_name(weapon["name"]))].append(weapon["_id"])
    source = {}
    targets = {}
    for (raw,) in db.execute("SELECT data_json FROM kira.entities WHERE kind='weapon'"):
        row = json.loads(raw)
        source[row["id"]] = row
        weapon_type = row["weapontype"]["local_name"]
        if weapon_type == "Sword":
            weapon_type = "Sword and Shield"
        matches = lookup[weapon_type, match_name(row["local_name"])]
        if len(matches) == 1:
            targets[row["id"]] = matches[0]
    by_target = {value: source[key] for key, value in targets.items()}
    parents = {value: targets.get(source[key]["weapon_parent_id"], 0) for key, value in targets.items()}
    for weapon in rows:
        weapon_id = weapon["_id"]
        parent = parents.get(weapon_id, 0)
        depth, current = 0, parent
        seen = {weapon_id}
        while current:
            if current in seen:
                raise ValueError(f"cyclic weapon tree at {weapon_id}")
            seen.add(current)
            depth += 1
            current = parents.get(current, 0)
        web = by_target.get(weapon_id, {})
        special = web.get("weaponspecialattacks")
        element = weapon_elements(weapon["elemental_attack"])
        awaken = weapon_elements(weapon["awakened_elemental_attack"])
        if special:
            element, awaken = [], []
            for power in special:
                data = power["pivot"]
                name = power["local_name"].replace("Blast", "Blastblight") if power["local_name"] == "Blast" else power["local_name"]
                (awaken if data.get("awaken_required") else element).append((name, data.get("attack") or 0))
        element1, element2 = (element + [("", 0), ("", 0)])[:2]
        awakening = (awaken + [("", 0)])[0]
        sharpness = weapon["sharpness"]
        if sharpness:
            bars = [".".join((bar.split(".") + ["0"] * 7)[:7]) for bar in sharpness.split()]
            sharpness = " ".join([bars[0], bars[-1], bars[-1]])
        insert(db, "weapons", _id=weapon_id, parent_id=parent, wtype=weapon["wtype"],
               creation_cost=weapon["creation_cost"], upgrade_cost=weapon["upgrade_cost"],
               attack=web.get("attack") or weapon["attack"], max_attack=0,
               element=element1[0], element_attack=element1[1], element_2=element2[0], element_2_attack=element2[1],
               awaken=awakening[0], awaken_attack=awakening[1], defense=weapon["defense"],
               sharpness=sharpness, affinity=str(web.get("affinity") or weapon["affinity"]),
               horn_notes=weapon["horn_notes"], shelling_type=weapon["shelling_type"], phial=weapon["phial"],
               charges=(weapon["charges"] or "").rstrip("|").replace(" L", " "), coatings=bow_coatings(weapon["coatings"]), recoil=weapon["recoil"], reload_speed=weapon["reload_speed"],
               rapid_fire=weapon["rapid_fire"], deviation=weapon["deviation"], ammo=weapon["ammo"],
               num_slots=weapon["num_slots"], tree_depth=depth, final=web.get("final", weapon["final"]) or 0)
    print(f"Weapon crosswalk: {len(by_target)}/{len(rows)}")


def verify(db):
    if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        raise ValueError("SQLite integrity check failed")
    if db.execute("PRAGMA foreign_key_check").fetchone():
        errors = [tuple(row) for row in db.execute("PRAGMA foreign_key_check")]
        raise ValueError(f"SQLite foreign key check failed: {len(errors)} rows, first: {errors[:5]}")
    expected = {"quests": 386, "weapons": 1421, "armor": 1641, "quest_rewards": 6201,
                "dex_DB_Tls": 261448, "dex_DB_Mon_Ail": 294}
    for table, count in expected.items():
        actual = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        if count != actual:
            raise ValueError(f"{table}: expected {count} rows, got {actual}")


def build(args):
    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".mh3u-build-", dir=output.parent) as temporary:
        file = Path(temporary) / "mh3u.db"
        db = sqlite3.connect(file, uri=True)
        db.row_factory = sqlite3.Row
        db.create_function("icon", 3, icon)
        db.create_function("icon_color", 1, icon_color)
        try:
            for name in ("legacy", "dex", "kira"):
                path = getattr(args, name).resolve()
                db.execute(f"ATTACH DATABASE ? AS {name}", (path.as_uri() + "?mode=ro",))
            schema = (HERE / "schema.sql").read_text(encoding="utf-8")
            legacy = (HERE / "import-legacy.sql").read_text(encoding="utf-8-sig")
            db.executescript("BEGIN;\n" + schema + "\n" + legacy)
            preserve_dex(db)
            items = map_dex_items(db)
            monsters = map_dex_monsters(db)
            import_armor_families(db)
            import_weapons(db)
            import_quests(db, items, monsters)
            import_item_sources(db, items, monsters)
            import_charms(db)
            verify(db)
            db.execute(f"PRAGMA user_version={DATA_VERSION}")
            db.commit()
        finally:
            db.close()
        archive = Path(temporary) / "asset.zip"
        with ZipFile(archive, "w", compression=ZIP_DEFLATED) as zip_file:
            zip_file.write(file, arcname=file.name)
        archive.replace(output)
    print(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dex", type=Path, required=True)
    parser.add_argument("--legacy", type=Path, required=True)
    parser.add_argument("--kira", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ASSETS / "assets/databases/mh3u.db.zip")
    build(parser.parse_args())


if __name__ == "__main__":
    main()
