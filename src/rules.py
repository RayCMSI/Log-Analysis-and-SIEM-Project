from datetime import datetime, timedelta, timezone
from src.db import get_conn

def alert(rule_id, severity, entity, summary, details):
    ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    with get_conn() as con:
        con.execute("""
            INSERT INTO alerts (ts, rule_id, severity, entity, summary, details)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (datetime.utcnow().isoformat(), rule_id, severeity, entity, summary, details),)

def failed_login_burst(threshold=5, window_minutes=10):
    """>threshold failed logins from same IP within window."""
    wstart = (datetime.utcnow() - timedelta(minutes=window_minutes)).isoformat()
    with get_conn() as con:
        rows = con.execute("""
            SELECT ip, COUNT(*) AS cnt
            FROM logs
            WHERE source='auth' AND action='login_failed' AND ts >= :wstart
            GROUP BY ip
            HAVING cnt > :threshold
        """, {"wstart": wstart, "threshold": threshold}).fetchall()

        for ip, cnt in rows:
            alert("failed_login_burst", "medium", ip,
                  f"{cnt} failed logins in {window_minutes}m",
                  f"ip={ip}")
                  
def off_hours_activity(start_hour = 8, end_hour = 18):
    """"Any Auth activity outside business hours"""
    with get_conn() as con:
        rows = con.execute("""
        SELECT ip, user, ts FROM logs
        WHERE source = 'auth'
        ORDER BY ts DESC LIMIT 500
        """).fetchall()
        for ip, user, ts in rows:
            hour = int(ts[11:13]) # Extract hour from ISO 8601 timestamp
            if not (start_hour <= hour < end_hour):
                alert("off_hours_activity", "low", f"{user}@{ip}", "Auth activity off_hours", f"ts={ts}, user={user}, ip={ip}")
