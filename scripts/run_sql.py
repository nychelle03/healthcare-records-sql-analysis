"""Run a saved SQL practice file against the fictional healthcare SQLite database."""
import sqlite3
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
db = root / "data" / "healthcare_records.db"
if len(sys.argv) < 2:
    sys.exit("Choose an open .sql file and run the VS Code task.")
sql_file = Path(sys.argv[1])
if not db.is_file():
    sys.exit(f"Database not found: {db}")
if not sql_file.is_file():
    sys.exit(f"SQL file not found: {sql_file}")
conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
conn.row_factory = sqlite3.Row
buffer = ""
try:
    for line in sql_file.read_text(encoding="utf-8").splitlines(keepends=True):
        buffer += line
        if not sqlite3.complete_statement(buffer):
            continue
        statement = buffer.strip()
        buffer = ""
        if not statement or all(part.strip().startswith("--") for part in statement.splitlines()):
            continue
        print("\nSQL:", statement)
        try:
            cur = conn.execute(statement)
            if cur.description:
                headers = [col[0] for col in cur.description]
                rows = cur.fetchmany(100)
                print(" | ".join(headers))
                print("-" * min(100, max(12, sum(map(len, headers)) + 3 * len(headers))))
                for row in rows:
                    print(" | ".join(str(value) if value is not None else "NULL" for value in row))
                if len(rows) == 100:
                    print("(Showing at most 100 rows)")
                else:
                    print(f"({len(rows)} rows)")
            else:
                print("Statement executed.")
        except sqlite3.Error as exc:
            print(f"SQL error: {exc}", file=sys.stderr)
    if buffer.strip() and not buffer.strip().startswith("--"):
        print("Incomplete SQL statement: check for a missing semicolon (;)", file=sys.stderr)
finally:
    conn.close()
