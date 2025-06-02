# Используем Python 3.13 slim
FROM python:3.13-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы конфигурации проекта
COPY pyproject.toml ./
COPY README.md ./

# Копируем исходный код
COPY src/ ./src/

# Устанавливаем зависимости из pyproject.toml
RUN pip install --no-cache-dir .

# Копируем оставшиеся файлы приложения
COPY . .

# Устанавливаем переменные окружения
ENV PYTHONPATH="/app"
ENV FLASK_ENV=production

# Открываем порт
EXPOSE 8080

# Запускаем приложение
CMD ["python", "main.py"]