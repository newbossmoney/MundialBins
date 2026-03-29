import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ==============================
# 🔐 CONFIGURACIÓN
# ==============================

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ ERROR: BOT_TOKEN no está configurado en Railway")

print("✅ TOKEN CARGADO:", BOT_TOKEN[:10], "...")  # muestra solo parte por seguridad

# ==============================
# 🧾 LOGS
# ==============================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ==============================
# 🤖 COMANDOS
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 Bot activo y funcionando correctamente\n\n"
        "Usa los comandos para interactuar."
    )

# ==============================
# 🚀 MAIN
# ==============================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # comandos
    app.add_handler(CommandHandler("start", start))

    print("🚀 Bot iniciado correctamente...")

    app.run_polling()

# ==============================
# ▶️ EJECUCIÓN
# ==============================

if __name__ == "__main__":
    main()
