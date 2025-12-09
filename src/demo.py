from db import get_conn

def activity_for_user(username: str):
    with get_conn() as con:
        rows = con.execute("""
            SELECT ts, ip, action, result
            FROM logs
            WHERE user = ?
            ORDER BY ts DESC;
        """, (username,))
        for r in rows:
            print(r)

if __name__ == "__main__":
    activity_for_user("ray")
