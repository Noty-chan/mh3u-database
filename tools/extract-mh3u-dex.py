import argparse
import hashlib
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile


SQL_SHA256 = "de28dafd7558b823e9f60be94f714e0094ef7b0975ac2ae9fc5378e7c4b19296"


def main():
    parser = argparse.ArgumentParser(description="Extract the local database from MH3U/G Dex 0.7.2.1.")
    parser.add_argument("apk", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    if args.output.exists():
        parser.error(f"output already exists: {args.output}")

    with ZipFile(args.apk) as apk:
        sql = apk.read("assets/create.sql")
    if hashlib.sha256(sql).hexdigest() != SQL_SHA256:
        parser.error("assets/create.sql differs from the verified 0.7.2.1 dump")

    with TemporaryDirectory(dir=args.output.parent) as temp:
        database = Path(temp) / "dex.sqlite"
        connection = sqlite3.connect(database)
        try:
            connection.executescript("BEGIN;\n" + sql.decode("utf-8-sig") + "\nCOMMIT;")
            if connection.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
                raise RuntimeError("SQLite integrity check failed")
        finally:
            connection.close()

        with database.open("rb") as source, args.output.open("xb") as dest:
            while block := source.read(1024 * 1024):
                dest.write(block)
    print(args.output)


if __name__ == "__main__":
    main()
