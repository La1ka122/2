FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y wget ca-certificates && \
    wget https://mega.nz/linux/repo/Debian_11/amd64/megacmd_1.6.3-1_amd64.deb && \
    apt-get install -y ./megacmd_1.6.3-1_amd64.deb && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .

CMD ["python", "bot.py"]
