# Использовать официальный образ Python
FROM python:3.13-slim-bookworm

# Обновить пакеты и установить обновления безопасности
RUN apt-get update && apt-get upgrade -y && apt-get clean

# Установить рабочую директорию
WORKDIR /app

# Скопировать файл зависимостей
COPY requirements.txt requirements.txt

# Установить зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Скопировать исходный код приложения
COPY . .

# Указать команду для запуска приложения
# Предполагается, что ваш основной файл - main.py и он запускает waitress на порту 8080
# и слушает на всех интерфейсах (0.0.0.0)
CMD ["waitress-serve", "--host=0.0.0.0", "--port=8080", "main:app"]