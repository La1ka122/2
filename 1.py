import telebot
from mega import Mega
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)
mega = Mega()
m = mega.login()

DOWNLOAD_DIR = "downloads"
MAX_SIZE_MB = 500
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Отправь ссылку на файл с mega.nz (до 500 МБ)"
    )

@bot.message_handler(func=lambda m: m.text and "mega.nz" in m.text)
def handle_mega(message):
    chat_id = message.chat.id
    url = message.text.strip()

    status = bot.send_message(chat_id, "🔍 Проверяю файл...")

    try:
        # Получаем инфу о файле
        info = m.get_public_url_info(url)
        file_size = info["size"]
        file_name = info["name"]

        if file_size > MAX_SIZE_BYTES:
            bot.edit_message_text(
                f"❌ Файл слишком большой\n"
                f"Размер: {file_size / 1024 / 1024:.2f} МБ\n"
                f"Лимит: {MAX_SIZE_MB} МБ",
                chat_id,
                status.message_id
            )
            return

        bot.edit_message_text(
            f"⬇ Скачиваю `{file_name}`...",
            chat_id,
            status.message_id,
            parse_mode="Markdown"
        )

        file_path = m.download_url(url, DOWNLOAD_DIR)

        with open(file_path, "rb") as f:
            bot.send_document(chat_id, f)

        os.remove(file_path)

        bot.edit_message_text(
            f"✅ Файл `{file_name}` отправлен и удалён",
            chat_id,
            status.message_id,
            parse_mode="Markdown"
        )

    except Exception as e:
        bot.edit_message_text(
            f"❌ Ошибка:\n`{e}`",
            chat_id,
            status.message_id,
            parse_mode="Markdown"
        )
