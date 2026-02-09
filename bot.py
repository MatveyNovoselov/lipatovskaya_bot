import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# --- НАСТРОЙКИ ---
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')  # Токен берется из файла .env

# !!! ВНИМАНИЕ: ВСТАВЬТЕ СЮДА РЕАЛЬНЫЕ ID ДВУХ ПОЛЬЗОВАТЕЛЕЙ !!!
# Замените числа 123456789 и 987654321 на те ID, которые вы нашли.
# Пример: USER_IDS = [592837461, 384716295]
USER_IDS = [5300487037, 5767746721]

# Настройка логирования
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# --- КОМАНДЫ БОТА ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение для приемной Липатовского"""
    official_welcome = (
        "Уважаемый(ая) {user_name}!\n\n"
        "🎗️ Добро пожаловать в официальную приемную Липатовского.\n\n"
        "Этот бот предназначен для оперативной связи и обработки ваших обращений. "
        "Здесь вы можете задать вопрос, оставить жалобу, предложение или запрос, "
        "касающийся интересующей Вас темы.\n\n"
        "🔹 **Как это работает:**\n"
        "1. Напишите ваш вопрос или обращение в этот чат.\n"
        "2. Бот автоматически зарегистрирует его и передаст ответственному сотруднику.\n"
        "3. Ответ поступит вам в установленные регламентом сроки.\n\n"
        "С уважением,\nПриемная Липатовского\n⸻\n*Это автоматическое сообщение, не требующее ответа.*"
    )
    welcome_text = official_welcome.format(user_name=update.effective_user.first_name)
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    await update.message.reply_text("Просто напишите ваш вопрос в этот чат.")

# --- ОСНОВНАЯ ЛОГИКА: ПЕРЕСЫЛКА ВОПРОСОВ ---
async def handle_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Принимает вопрос от пользователя и пересылает его двум ответственным"""
    user = update.effective_user
    user_message = update.message.text

    # Формируем информационное сообщение для ответственных
    user_info = (
        f"📩 *Новое обращение в приемную*\n"
        f"От: {user.first_name} {user.last_name or ''} (@{user.username or 'нет'})\n"
        f"ID пользователя: {user.id}\n"
        f"---\n`{user_message}`"
    )

    success_count = 0  # Счетчик успешных отправок
    # Пытаемся отправить сообщение каждому из ответственных
    for user_id in USER_IDS:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=user_info,
                parse_mode='Markdown'
            )
            logger.info(f"Обращение переслано пользователю с ID: {user_id}")
            success_count += 1
        except Exception as e:
            logger.error(f"Не удалось отправить пользователю {user_id}: {e}")

    # Даем обратную связь отправителю
    if success_count > 0:
        await update.message.reply_text(f"✅ Ваше обращение принято и направлено ответственному сотруднику (уведомлений отправлено: {success_count}).")
    else:
        await update.message.reply_text("❌ В данный момент невозможно передать обращение. Пожалуйста, попробуйте позже или свяжитесь иным способом.")

# --- ЗАПУСК БОТА ---
def main():
    """Основная функция запуска бота"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    # Обработчик для ЛИЧНЫХ текстовых сообщений (не команд)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        handle_private_message
    ))

    logger.info("Бот 'Приемная Липатовского' запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()