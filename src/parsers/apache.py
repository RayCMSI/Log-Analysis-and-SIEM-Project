import re
from datetime import datetime, timezone

PATTERN = re.compile(r'(?P<ip>\S+) \S+ \S+ \[(?P<time>.*?)\] "(?P<method>\S+) (?P<path>\S+) \S+" (?P<status>\d{3}) \S+')

def parse_line(line: str):
    m = PATTERN.search(line)

    if not m:
        return None
    ts = datetime.strptime(m["time"], "%d/%b/%Y:%H:%M:%S %z").astimezone(timezone.utc).isoformat()
    return {
        "source": "apache",
        "ts": ts,
        "ip": m["ip"],
        "user": None,
        "action": f'{m["method"]} {m["path"]}',
        "result": m["status"],
        "raw": line.strip("\n"),
    }