# Використовуємо конкретний тег slim з Python 3.11
FROM python:3.11-slim-bullseye

# Встановлюємо робочу директорію
WORKDIR /app

# Оновлюємо pip та встановлюємо залежності
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо скрипт та таблицю
COPY . .

# Встановлюємо змінну оточення для Fly.io (опціонально)
ENV PYTHONUNBUFFERED=1

# Запуск бота
CMD ["python", "bot.py"]
