FROM python:3.11-slim

# Устанавливаем зависимости
RUN apt-get update && \
    apt-get install -y curl gnupg ca-certificates && \
    curl -fsSL https://mega.nz/linux/repo/xUbuntu_22.04/Release.key | gpg --dearmor > /usr/share/keyrings/mega.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/mega.gpg] https://mega.nz/linux/repo/xUbuntu_22.04/ /" \
        > /etc/apt/sources.list.d/mega.list && \
    apt-get update && \
    apt-get install -y megacmd wget && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .

CMD ["python", "bot.py"]
