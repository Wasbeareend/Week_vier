from flask import Flask
import sqlite3

app = Flask(__name__)

DB_NAME = "portfolio_opdracht_8_nieuw.db"

@app.route("/")
def home():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT wat_te_doen, status, device, eind_datum
        FROM assignments
        ORDER BY assignment_id
    """)

    opdrachten = cursor.fetchall()
    conn.close()

    html = "<h1>Mijn portfolio opdrachten</h1>"

    for opdracht in opdrachten:
        wat_te_doen, status, device, eind_datum = opdracht
        html += f"<p><b>{wat_te_doen}</b> | {status} | {device} | {eind_datum}</p>"

    return html