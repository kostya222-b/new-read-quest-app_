FROM python:3.10-bullseye

# Устанавливаем системные зависимости
RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
    python3-pip \
    libffi-dev && \
    apt-get clean && \
    apt-get autoremove && \
    rm -rf /var/lib/apt/lists/*

# Создаем и назначаем рабочую директорию
WORKDIR /app

# Копируем только requirements.txt для установки зависимостей
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Создаем пользователя для безопасности
RUN useradd -m appuser && \
    chown -R appuser:appuser /app

# Переключаемся на пользователя appuser
USER appuser

# Открываем порт 8000
EXPOSE 8000

# Запускаем FastAPI с Uvicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "src.quest_ans:app"]
