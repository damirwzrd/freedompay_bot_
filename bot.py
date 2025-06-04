import logging
from uuid import uuid4
from telegram import Update, LabeledPrice
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
)
from flask import Flask
import threading
import asyncio

# 🔐 Замените своими токенами
TOKEN = "7860845577:AAEGZ_nPLGSRDXOwadzdgJGe20kKT_ZtCIY"
PROVIDER_TOKEN = "6618536796:TEST:545158"

# Логгирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask-приложение для Render
flask_app = Flask(__name__)

@flask_app.route("/")
def index():
    return "OK"

def run_flask():
    flask_app.run(host="0.0.0.0", port=8000)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Введите /pay чтобы протестировать оплату через FreedomPay.")

# Команда /pay
async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payload = f"freedompay-test-{uuid4()}"  # Уникальный payload
    prices = [LabeledPrice("Тестовый товар", 1000 * 100)]  # 1000 сомов
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title="FreedomPay Тестовая покупка",
        description="Это тестовая оплата через FreedomPay",
        payload=payload,
        provider_token=PROVIDER_TOKEN,
        currency="KGS",
        prices=prices,
        need_name=True,
        is_flexible=False,
    )

# Обработка pre-checkout
async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    if not query.invoice_payload.startswith("freedompay-test-"):
        await query.answer(ok=False, error_message="Ошибка проверки payload.")
    else:
        await query.answer(ok=True)
        logger.info("PreCheckout подтвержден.")

# Обработка успешной оплаты
async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("✅ Оплата прошла успешно!")
    await update.message.reply_text("✅ Спасибо! Оплата прошла успешно!")

async def main():
    # Запускаем Flask-сервер в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Создаём и запускаем Telegram-бота
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("pay", pay))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
