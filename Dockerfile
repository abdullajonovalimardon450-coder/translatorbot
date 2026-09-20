FROM python:3.11-slim
WORKDIR /app
COPY requirements-1.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY bot-1.py bot.py
CMD ["python", "bot.py"]
