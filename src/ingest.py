from pathlib import Path
from src.db import get_conn, init_db
from src.parsers.apache import parse_line as parse_apache
from src.parsers.auth import parse_line as parse_auth

def ingest_file(path: Path, kind: str):
    parser = {"apache": parse_apache, "auth": parse_auth}[kind]

    with get_conn() as con, path.open("r", errors="ignore") as f:
        rows = []
        for line in f:
            rec = parser(line)
            if rec:
                rec.setdefault("source", kind)
                rows.append(rec)

        con.executemany(
            """
            INSERT INTO logs (source, ts, ip, user, action, result, raw)
            VALUES (:source, :ts, :ip, :user, :action, :result, :raw)
            """,
            rows,
        )

        return len(rows)

if __name__ == "__main__":
    init_db()
    base = Path(__file__).resolve().parents[1] / "sample_logs" / "synthetic"

    for p in base.glob("*.log"):
        kind = "apache" if "access" in p.name else "auth"
        n = ingest_file(p, kind)
        print(f"Ingested {n} from {p}")
