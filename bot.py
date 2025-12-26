import telebot
import subprocess
import os
import json
import uuid

BOT_TOKEN = os.environ.get("BOT_TOKEN")
MAX_SIZE_MB = 500
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024
DOWNLOAD_DIR = "/tmp/downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

bot = telebot.TeleBot(BOT_TOKEN)

def get_mega_info(url: str):
    """
    Получаем информацию о файле через megatools
    """
    result = subprocess.run(
        ["megatools", "ls", url, "--json"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(result.stderr)

    data = json.loads(result.stdout)
    file_info = data[0]

    return file_info["name"], int(file_info["size"])

def download_mega(url: str, path: str):
    subprocess.check_call([
        "megatools",
        "dl",
        "--path", path,
        url
    ])

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
        filename, size = get_mega_info(url)

        if size > MAX_SIZE_BYTES:
            bot.edit_message_text(
                f"❌ Файл слишком большой\n"
                f"Размер: {size / 1024 / 1024:.2f} МБ\n"
                f"Лимит: {MAX_SIZE_MB} МБ",
                chat_id,
                status.message_id
            )
            return

        tmp_name = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(DOWNLOAD_DIR, tmp_name)

        bot.edit_message_text(
            f"⬇ Скачиваю `{filename}`...",
            chat_id,
            status.message_id,
            parse_mode="Markdown"
        )

        download_mega(url, file_path)

        with open(file_path, "rb") as f:
            bot.send_document(chat_id, f)

        os.remove(file_path)

        bot.edit_message_text(
            f"✅ Файл `{filename}` отправлен и удалён",
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

bot.polling(none_stop=True)
