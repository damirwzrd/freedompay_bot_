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

# 🔐 Замените своими токенами
TOKEN = "7860845577:AAEGZ_nPLGSRDXOwadzdgJGe20kKT_ZtCIY"
PROVIDER_TOKEN = "6618536796:TEST:545158"

# Логгирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Главная функция
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pay", pay))
    app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
    app.run_polling()

if __name__ == "__main__":
    main()
