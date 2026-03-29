import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    puntos INTEGER DEFAULT 0,
    faltas INTEGER DEFAULT 0,
    aciertos INTEGER DEFAULT 0,
    predicciones INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS jornadas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT,
    cierre INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS partidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jornada_id INTEGER,
    numero INTEGER,
    equipo1 TEXT,
    equipo2 TEXT,
    hora INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS predicciones (
    user_id INTEGER,
    jornada_id INTEGER,
    data TEXT,
    UNIQUE(user_id, jornada_id)
)
""")

conn.commit()
