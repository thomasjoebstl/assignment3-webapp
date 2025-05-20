from flask import Flask, request, jsonify
import psycopg2
import os
import time

app = Flask(__name__)

# Umgebungsvariablen (aus docker-compose.yml)
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "mydb")
DB_USER = os.getenv("DB_USER", "user")
DB_PASS = os.getenv("DB_PASS", "password")

# Verbindung zur Datenbank mit Wiederholungsversuchen
conn = None
for i in range(10):
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        print("✅ Erfolgreich mit der Datenbank verbunden.")
        break
    except psycopg2.OperationalError:
        print(f"❌ Versuch {i+1}/10: Verbindung zur Datenbank fehlgeschlagen, warte 2 Sekunden...")
        time.sleep(2)

if conn is None:
    raise Exception("❌ Verbindung zur Datenbank konnte nicht hergestellt werden.")

# Routen
@app.route("/")
def hello():
    return "✅ WebApp läuft!"

@app.route("/add", methods=["POST"])
def add_data():
    try:
        data = request.json["data"]
        with conn.cursor() as cur:
            cur.execute("INSERT INTO testtable (data) VALUES (%s)", (data,))
            conn.commit()
        return "✅ Gespeichert"
    except Exception as e:
        return f"❌ Fehler beim Speichern: {str(e)}", 500

@app.route("/all", methods=["GET"])
def get_data():
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM testtable")
            result = cur.fetchall()
        return jsonify(result)
    except Exception as e:
        return f"❌ Fehler beim Abrufen der Daten: {str(e)}", 500

# Server starten
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

