import time
import re
import logging
import pandas as pd

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from config import BOT_TOKEN, ADMIN_IDS
from database import cursor, conn
from sofascore import obtener_partidos_hoy, obtener_resultados_hoy

logging.basicConfig(level=logging.INFO)

last_usage = {}

def anti_spam(user_id):
    ahora = time.time()
    if user_id in last_usage and ahora - last_usage[user_id] < 3:
        return True
    last_usage[user_id] = ahora
    return False


def is_admin(user_id):
    return user_id in ADMIN_IDS


def validar_prediccion(texto, total):
    lineas = texto.split("\n")
    if len(lineas) != total:
        return False

    patron = r"#\d+\s\d+-\d+"
    return all(re.match(patron, l.strip()) for l in lineas)


def menu():
    return ReplyKeyboardMarkup([
        ["📊 Ranking", "🎯 Mi Puntaje"],
        ["📅 Jornada", "💀 Inactivos"]
    ], resize_keyboard=True)


# 🚀 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bienvenido ⚽", reply_markup=menu())


# 📅 JORNADA
async def jornada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Solo admin")
        return

    partidos = obtener_partidos_hoy()

    if not partidos:
        await update.message.reply_text("❌ No hay partidos")
        return

    primer = min(p["hora"] for p in partidos)
    cierre = primer - 1800

    cursor.execute("INSERT INTO jornadas (fecha, cierre) VALUES (?, ?)", ("hoy", cierre))
    jid = cursor.lastrowid

    texto = "📅 Jornada:\n\n"

    for p in partidos:
        cursor.execute("""
        INSERT INTO partidos (jornada_id, numero, equipo1, equipo2, hora)
        VALUES (?, ?, ?, ?, ?)
        """, (jid, p["numero"], p["equipo1"], p["equipo2"], p["hora"]))

        hora = time.strftime('%H:%M', time.localtime(p["hora"]))
        texto += f"#{p['numero']} {p['equipo1']} vs {p['equipo2']} ({hora})\n"

    conn.commit()
    await update.message.reply_text(texto)


# ⚽ PREDICCION
async def prediccion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if anti_spam(user.id):
        return

    texto = update.message.text.replace("/prediccion", "").strip()

    cursor.execute("SELECT id, cierre FROM jornadas ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()

    if not row:
        await update.message.reply_text("❌ No hay jornada")
        return

    jid, cierre = row

    if time.time() > cierre:
        await update.message.reply_text("⛔ Cerrado")
        return

    cursor.execute("SELECT COUNT(*) FROM partidos WHERE jornada_id=?", (jid,))
    total = cursor.fetchone()[0]

    if not validar_prediccion(texto, total):
        await update.message.reply_text("❌ Formato inválido")
        return

    try:
        cursor.execute("INSERT INTO predicciones VALUES (?, ?, ?)", (user.id, jid, texto))
    except:
        await update.message.reply_text("⚠️ Ya enviaste")
        return

    cursor.execute("""
    INSERT OR IGNORE INTO users (user_id, username)
    VALUES (?, ?)
    """, (user.id, user.username))

    conn.commit()
    await update.message.reply_text("✅ Guardado")


# 🧮 RESULTADOS AUTO
async def resultado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    resultados_api = obtener_resultados_hoy()

    cursor.execute("SELECT id FROM jornadas ORDER BY id DESC LIMIT 1")
    jid = cursor.fetchone()[0]

    cursor.execute("SELECT numero, equipo1, equipo2 FROM partidos WHERE jornada_id=?", (jid,))
    partidos = cursor.fetchall()

    mapa = {}
    for num, e1, e2 in partidos:
        if (e1, e2) in resultados_api:
            mapa[f"#{num}"] = resultados_api[(e1, e2)]

    cursor.execute("SELECT user_id, data FROM predicciones WHERE jornada_id=?", (jid,))
    preds = cursor.fetchall()

    for uid, pred in preds:
        puntos = 0

        for linea in pred.split("\n"):
            n, res = linea.split(" ")
            if n not in mapa:
                continue

            pr1, pr2 = map(int, res.split("-"))
            r1, r2 = map(int, mapa[n].split("-"))

            if pr1 == r1 and pr2 == r2:
                puntos += 3
            elif (pr1 > pr2 and r1 > r2) or (pr1 < pr2 and r1 < r2) or (pr1 == pr2 and r1 == r2):
                puntos += 1

        cursor.execute("""
        UPDATE users 
        SET puntos = puntos + ?, predicciones = predicciones + 1 
        WHERE user_id=?
        """, (puntos, uid))

    conn.commit()
    await update.message.reply_text("✅ Resultados procesados")


# 🏆 RANKING
async def ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("SELECT username, puntos FROM users ORDER BY puntos DESC LIMIT 10")
    data = cursor.fetchall()

    texto = "🏆 Ranking:\n\n"
    for i, (u, p) in enumerate(data, 1):
        texto += f"{i}. @{u} - {p} pts\n"

    await update.message.reply_text(texto)


# 💀 INACTIVOS
async def inactivos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("SELECT username, faltas FROM users WHERE faltas >= 2 ORDER BY faltas DESC")
    data = cursor.fetchall()

    texto = "💀 Inactivos:\n\n"
    for i, (u, f) in enumerate(data, 1):
        texto += f"{i}. @{u} - {f}\n"

    await update.message.reply_text(texto)


# 📊 STATS
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    cursor.execute("SELECT puntos, predicciones FROM users WHERE user_id=?", (uid,))
    row = cursor.fetchone()

    if not row:
        return

    puntos, preds = row
    await update.message.reply_text(f"Puntos: {puntos}\nParticipaciones: {preds}")


# 🧾 EXPORT
async def exportar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    cursor.execute("SELECT username, puntos FROM users ORDER BY puntos DESC")
    data = cursor.fetchall()

    df = pd.DataFrame(data, columns=["Usuario", "Puntos"])
    df.to_excel("ranking.xlsx", index=False)

    await update.message.reply_document(open("ranking.xlsx", "rb"))


# 🚀 RUN
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("jornada", jornada))
app.add_handler(CommandHandler("prediccion", prediccion))
app.add_handler(CommandHandler("resultado", resultado))
app.add_handler(CommandHandler("ranking", ranking))
app.add_handler(CommandHandler("inactivos", inactivos))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("exportar", exportar))

app.run_polling()
