# Використовуємо конкретний тег slim з Python 3.11
FROM python:3.11-slim-bullseye

WORKDIR /app

# Копіюємо залежності та встановлюємо
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо код бота та таблицю
COPY . .

# Запуск бота
CMD ["python", "bot.py"]
