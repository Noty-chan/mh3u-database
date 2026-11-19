# MH3U Database

An offline Android reference for Monster Hunter 3 Ultimate, based on the MIT-licensed [MHGU Database](https://github.com/gatheringhallstudios/MHGenDatabase) by Gathering Hall Studios.

Settings → Theme offers System default, Light, and Dark. This app uses its own Android package and database file so it can be installed alongside the upstream app.

## Build

Requirements are Python 3.10 or later, JDK 17, and Android SDK (35 for the app and 27/30 for the existing library modules). Gradle runs through the included wrapper.

From the repository root, use PowerShell or adapt the paths for your shell:

```powershell
New-Item -ItemType Directory -Force local-data
python tools/extract-mh3u-dex.py local-data/MH3U-G-Dex.apk local-data/dex.sqlite
python tools/build-database.py --dex local-data/dex.sqlite --legacy local-data/mh3u.sqlite --kira local-data/mh3u-kiranico.sqlite
.\gradlew.bat :app:assembleDebug
```

- **Dex** — `dex.monhun` [version 0.7.2.1](https://apkpure.net/mh3u-g-dex/dex.monhun/download). The extractor verifies the embedded SQL checksum.
- **Legacy** — `mh3u.sqlite` from the [Android reference source at a500845](https://github.com/dbooga/MonsterHunter3UDatabase/tree/a500845/MonsterHunter3UDatabase/assets). Use the binary SQLite file.
- **Kiranico** — install `beautifulsoup4`, then run the included exporter as shown below.

```powershell
python -m pip install beautifulsoup4
python tools/export-kiranico-mh3u.py --cache local-data/kiranico-cache --output local-data/mh3u-kiranico.sqlite
```

For map art, copy the `maps_mh3_*.png` files from the legacy app’s `assets/icons_location` into `local-data/maps/drawable-nodpi` before building.

The build script writes `app/src/main/assets/databases/mh3u.db.zip`. The APK is in `app/build/outputs/apk/debug/app-debug.apk`. Local inputs and the generated asset are ignored by Git.

## Database mapping

`tools/schema.sql` defines the schema the Android app expects. `tools/import-legacy.sql` loads equipment, skills, templates for catalog items and maps, and hitzones. The Python migration uses Dex for regular quests, quest rewards, gathering, hunting drops, and talisman combinations. It keeps the original Dex tables under a `dex_` prefix for comparisons. Arena quests and hitzones come from the legacy reference, and verified Kiranico name/type matches supply weapon upgrade links and secondary stats.

The migration verifies the resulting SQLite file, foreign keys, and expected table counts before replacing the local archive. Keep Android database version `DATABASE_VERSION` and migration `DATA_VERSION` in sync. Preserve record IDs when updating an installed MH3U catalog so wishlists and saved sets still point to the same records.

Catalog fields without a source value remain empty or use the UI's unknown marker. Gathering percentages and rewards for the ten Challenge Quest entries are still unavailable. Raw Dex ailment values retain their source scale. Armor families use names, rarity, gender, and hunter type. Pieces that cannot be grouped unambiguously have their own entries. The language for the merged catalog is English, with Japanese names where available.

[Data provenance and upstream terms](https://sites.google.com/site/pingsdex/pingsmh3gdex)
