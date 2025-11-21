import re 
from datetime import datetime, timezone

PATTERN = re.compile(r'(?P<ip>\S+) - (?P<user>\S+) \[(?P<time>.*?)\] "(?P<action>.*?)" (?P<result>\d{3}) \S+')

def parse_line(line:str, year: int | None = None):
    m = PATTERN.search(line)

    if not m:
        return None
    
    now = datetime.now(timezone.utc)
    ts = now.replace(microsecond=0).isoformat()

    return {
        "source": "auth",
        "ts": ts,
        "ip": m["ip"],
        "user": m["user"],
        "action": "login_failed",
        "result": "failed",
        "raw": line.rstrip("\n"),
    }
    
