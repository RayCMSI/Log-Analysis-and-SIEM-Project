from flask import Flask, render_template
from src.db import get_conn

app = Flask(__name__, template_folder="../web/templates", static_folder="../web/static")

@app.route("/")

def home():
    with get_conn() as con:
        alerts = con.execute("SELECT ts, rule_id, severity, entity, summary, FROM alerts ORDER BY ts DESC LIMIT 50").fetchall()
        top_ips = con.execute("""
            SELECT ip, COUNT(*) as cnt FROM logs
            WHERE ip IS NOT NULL AND ip != ''
            GROUP BY ip ORDER BY cnt DESC LIMIT 10
        """).fetchall()
    return render_template("home.html", alerts=alerts, top_ips=top_ips)

if __name__ == "__main__":
    app.run(debug=True)