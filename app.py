import os
import pyodbc
from flask import Flask, jsonify
from dotenv import load_dotenv
from flask_cors import CORS

# Lädt die Umgebungsvariablen (unseren DATABASE_CONNECTION_STRING, den wir in den Codespace-Secrets hinterlegt haben)
load_dotenv()

# Initialisiert die Flask-App
app = Flask(__name__)

# Richtet CORS ein. Das ist wichtig, damit unser React-Frontend später
# auf die API zugreifen darf.
CORS(app)

# Hilfsfunktion, um eine sichere Datenbankverbindung herzustellen
def get_db_connection():
    """Stellt eine Verbindung zur Azure SQL-Datenbank her und gibt das Connection-Objekt zurück."""
    conn_str = os.getenv('DATABASE_CONNECTION_STRING')
    if not conn_str:
        # Dieser Fehler sollte dank der Codespace-Secrets nicht auftreten
        raise ValueError("WICHTIG: DATABASE_CONNECTION_STRING wurde nicht gefunden! Hast du sie in den GitHub Codespaces Secrets hinterlegt?")
    try:
        conn = pyodbc.connect(conn_str, autocommit=True)
        return conn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"FATAL: Datenbankverbindungsfehler! SQLSTATE: {sqlstate}")
        # Wirft den Fehler weiter, damit die App nicht startet, wenn die DB nicht erreichbar ist.
        raise

# API-Endpunkt #1: Ein einfacher Health-Check
@app.route('/api/health', methods=['GET'])
def health_check():
    """Überprüft, ob der Server läuft und die DB-Verbindung klappt."""
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({"status": "ok", "database_connection": "successful"})
    except Exception as e:
        return jsonify({"status": "error", "database_connection": "failed", "error_message": str(e)}), 500

# API-Endpunkt #2: Holt Daten aus deiner Datenbank
# BITTE ANPASSEN!
@app.route('/api/data', methods=['GET'])
def get_data():
    """Holt Beispieldaten aus einer Tabelle."""
    items = []
    # WICHTIG: Passe die SQL-Abfrage an deine Tabellen- und Spaltennamen an!
    # Beispiel: "SELECT UserID, Username, Email FROM Users"
    sql_query = "SELECT TOP 10 * FROM Person;" 

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        
        # Konvertiert die Datenbankzeilen in ein lesbares Format (Liste von Dictionaries)
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            items.append(dict(zip(columns, row)))
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Fehler beim Abrufen der Daten: {e}")
        return jsonify({"error": "Konnte Daten nicht abrufen", "details": str(e)}), 500
        
    return jsonify(items)

# Startet den Server, wenn das Skript direkt ausgeführt wird
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)