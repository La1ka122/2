import telebot
import subprocess
import os
import uuid

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

CHUNK_SIZE = 500 * 1024 * 1024  # 500 MB
TMP_DIR = "/tmp/mega_parts"
os.makedirs(TMP_DIR, exist_ok=True)

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Отправь ссылку на mega.nz\n"
        "Файлы будут отправляться частями по 500 МБ"
    )

@bot.message_handler(func=lambda m: m.text and "mega.nz" in m.text)
def handle_mega(message):
    chat_id = message.chat.id
    url = message.text.strip()

    status = bot.send_message(chat_id, "🚀 Начинаю загрузку...")

    try:
        process = subprocess.Popen(
            ["mega-get", url, "--stdout"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        part = 1
        current_size = 0
        part_path = os.path.join(TMP_DIR, f"part_{part}.bin")
        f = open(part_path, "wb")

        while True:
            chunk = process.stdout.read(1024 * 1024)  # 1 MB
            if not chunk:
                break

            f.write(chunk)
            current_size += len(chunk)

            if current_size >= CHUNK_SIZE:
                f.close()
                send_part(chat_id, part_path, part)
                os.remove(part_path)

                part += 1
                current_size = 0
                part_path = os.path.join(TMP_DIR, f"part_{part}.bin")
                f = open(part_path, "wb")

        f.close()

        if os.path.exists(part_path) and os.path.getsize(part_path) > 0:
            send_part(chat_id, part_path, part)
            os.remove(part_path)

        bot.edit_message_text(
            "✅ Загрузка завершена",
            chat_id,
            status.message_id
        )

    except Exception as e:
        bot.edit_message_text(
            f"❌ Ошибка:\n{e}",
            chat_id,
            status.message_id
        )

def send_part(chat_id, path, part):
    with open(path, "rb") as f:
        bot.send_document(
            chat_id,
            f,
            caption=f"📦 Часть {part}"
        )

if __name__ == "__main__":
    bot.polling(
        none_stop=True,
        timeout=30,
        skip_pending=True
    )
