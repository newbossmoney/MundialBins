import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ==============================
# 🔍 DEBUG VARIABLES
# ==============================

print("🔍 VARIABLES DE ENTORNO DISPONIBLES:")
for key in os.environ:
    print(f"{key} = {os.environ[key]}")

BOT_TOKEN = os.getenv("BOT_TOKEN")

print("🔑 TOKEN DETECTADO:", BOT_TOKEN)

# ==============================
# 🚨 VALIDACIÓN FUERTE
# ==============================

if not BOT_TOKEN or BOT_TOKEN.strip() == "":
    raise ValueError("❌ ERROR: BOT_TOKEN no está configurado en Railway o está vacío")

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
        "Ya estamos listos para el siguiente nivel 🚀"
    )

# ==============================
# 🚀 MAIN
# ==============================

def main():
    print("🚀 Iniciando bot...")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # comandos
    app.add_handler(CommandHandler("start", start))

    print("✅ Bot corriendo correctamente...")

    app.run_polling()

# ==============================
# ▶️ EJECUCIÓN
# ==============================

if __name__ == "__main__":
    main()
