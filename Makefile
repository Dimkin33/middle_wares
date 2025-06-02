# ==============================================
# TENNIS SCOREBOARD MAKEFILE
# ==============================================
# Makefile для быстрого деплоя и управления
# Docker-контейнерами приложения Tennis Scoreboard

# Переменные
# ----------
COMPOSE_FILE = compose.yml
ENV_FILE = .env
APP_NAME = tennis-scoreboard
BACKUP_DIR = ./backups
LOG_DIR = ./logs

# Цвета для вывода
CYAN = \033[36m
GREEN = \033[32m
YELLOW = \033[33m
RED = \033[31m
NC = \033[0m # No Color

.PHONY: help build up down restart logs status clean backup restore health test

# Показать справку
help:
	@echo "$(CYAN)=== TENNIS SCOREBOARD DEPLOYMENT ===$(NC)"
	@echo ""
	@echo "$(GREEN)Основные команды:$(NC)"
	@echo "  make build     - Собрать все Docker образы"
	@echo "  make up        - Запустить все сервисы"
	@echo "  make down      - Остановить все сервисы"
	@echo "  make restart   - Перезапустить все сервисы"
	@echo "  make deploy    - Полный деплой (build + up)"
	@echo ""
	@echo "$(GREEN)Мониторинг и диагностика:$(NC)"
	@echo "  make status    - Показать статус контейнеров"
	@echo "  make logs      - Показать логи всех сервисов"
	@echo "  make logs-app  - Показать логи приложения"
	@echo "  make logs-db   - Показать логи базы данных"
	@echo "  make logs-nginx- Показать логи nginx"
	@echo "  make health    - Проверить здоровье сервисов"
	@echo ""
	@echo "$(GREEN)Управление данными:$(NC)"
	@echo "  make backup    - Создать резервную копию БД"
	@echo "  make restore   - Восстановить БД из резервной копии"
	@echo "  make clean     - Очистить неиспользуемые Docker ресурсы"
	@echo "  make clean-all - Полная очистка (включая volumes)"
	@echo ""
	@echo "$(GREEN)Разработка и тестирование:$(NC)"
	@echo "  make test      - Запустить тесты"
	@echo "  make lint      - Проверить код линтером"
	@echo "  make format    - Форматировать код"
	@echo "  make shell-app - Подключиться к контейнеру приложения"
	@echo "  make shell-db  - Подключиться к контейнеру БД"

# Собрать все Docker образы
build:
	@echo "$(CYAN)🔨 Сборка Docker образов...$(NC)"
	docker-compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) build --no-cache
	@echo "$(GREEN)✅ Сборка завершена$(NC)"

# Запустить все сервисы
up:
	@echo "$(CYAN)🚀 Запуск сервисов...$(NC)"
	docker-compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) up -d
	@sleep 5
	@make status
	@echo "$(GREEN)✅ Сервисы запущены$(NC)"
	@echo "$(YELLOW)🌐 Приложение доступно по адресу: http://localhost$(NC)"

# Остановить все сервисы
down:
	@echo "$(CYAN)🛑 Остановка сервисов...$(NC)"
	docker-compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) down
	@echo "$(GREEN)✅ Сервисы остановлены$(NC)"

# Перезапустить все сервисы
restart:
	@echo "$(CYAN)🔄 Перезапуск сервисов...$(NC)"
	@make down
	@sleep 2
	@make up

# Полный деплой
deploy:
	@echo "$(CYAN)🚀 ПОЛНЫЙ ДЕПЛОЙ ПРИЛОЖЕНИЯ$(NC)"
	@make build
	@make up
	@make health
	@echo "$(GREEN)✅ ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО$(NC)"

# Показать статус контейнеров
status:
	@echo "$(CYAN)📊 Статус контейнеров:$(NC)"
	docker-compose -f $(COMPOSE_FILE) ps

# Показать логи всех сервисов
logs:
	@echo "$(CYAN)📜 Логи всех сервисов:$(NC)"
	docker-compose -f $(COMPOSE_FILE) logs --tail=50 -f

# Показать логи приложения
logs-app:
	@echo "$(CYAN)📜 Логи приложения:$(NC)"
	docker-compose -f $(COMPOSE_FILE) logs --tail=50 -f app

# Показать логи базы данных
logs-db:
	@echo "$(CYAN)📜 Логи базы данных:$(NC)"
	docker-compose -f $(COMPOSE_FILE) logs --tail=50 -f db

# Показать логи nginx
logs-nginx:
	@echo "$(CYAN)📜 Логи nginx:$(NC)"
	docker-compose -f $(COMPOSE_FILE) logs --tail=50 -f nginx

# Проверить здоровье сервисов
health:
	@echo "$(CYAN)🏥 Проверка здоровья сервисов...$(NC)"
	@echo "$(YELLOW)Проверка nginx (порт 80):$(NC)"
	@curl -s -f http://localhost >/dev/null && echo "$(GREEN)✅ Nginx: OK$(NC)" || echo "$(RED)❌ Nginx: FAIL$(NC)"
	@echo "$(YELLOW)Проверка приложения (порт 8080):$(NC)"
	@curl -s -f http://localhost:8080 >/dev/null && echo "$(GREEN)✅ App: OK$(NC)" || echo "$(RED)❌ App: FAIL$(NC)"
	@echo "$(YELLOW)Проверка базы данных:$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec -T db pg_isready -U postgres >/dev/null && echo "$(GREEN)✅ Database: OK$(NC)" || echo "$(RED)❌ Database: FAIL$(NC)"

# Создать резервную копию БД
backup:
	@echo "$(CYAN)💾 Создание резервной копии БД...$(NC)"
	@mkdir -p $(BACKUP_DIR)
	@BACKUP_FILE="$(BACKUP_DIR)/tennis_db_backup_$$(date +%Y%m%d_%H%M%S).sql"; \
	docker-compose -f $(COMPOSE_FILE) exec -T db pg_dump -U postgres postgres > $$BACKUP_FILE && \
	echo "$(GREEN)✅ Резервная копия создана: $$BACKUP_FILE$(NC)" || \
	echo "$(RED)❌ Ошибка создания резервной копии$(NC)"

# Восстановить БД из резервной копии
restore:
	@echo "$(YELLOW)📋 Доступные резервные копии:$(NC)"
	@ls -la $(BACKUP_DIR)/*.sql 2>/dev/null || echo "$(RED)❌ Резервные копии не найдены$(NC)"
	@echo "$(CYAN)Для восстановления выполните:$(NC)"
	@echo "docker-compose exec -T db psql -U postgres postgres < $(BACKUP_DIR)/filename.sql"

# Очистить неиспользуемые Docker ресурсы
clean:
	@echo "$(CYAN)🧹 Очистка Docker ресурсов...$(NC)"
	docker system prune -f
	docker image prune -f
	@echo "$(GREEN)✅ Очистка завершена$(NC)"

# Полная очистка включая volumes
clean-all:
	@echo "$(RED)⚠️  ВНИМАНИЕ: Это удалит ВСЕ данные приложения!$(NC)"
	@echo "$(YELLOW)Продолжить? [y/N]$(NC)"
	@read -p "" confirm && [ "$$confirm" = "y" ] || exit 1
	@make down
	docker-compose -f $(COMPOSE_FILE) down -v --remove-orphans
	docker system prune -af --volumes
	@echo "$(GREEN)✅ Полная очистка завершена$(NC)"

# Запустить тесты
test:
	@echo "$(CYAN)🧪 Запуск тестов...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec app python -m pytest tests/ -v
	@echo "$(GREEN)✅ Тесты завершены$(NC)"

# Проверить код линтером
lint:
	@echo "$(CYAN)🔍 Проверка кода линтером...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec app python -m flake8 src/
	@echo "$(GREEN)✅ Проверка линтером завершена$(NC)"

# Форматировать код
format:
	@echo "$(CYAN)✨ Форматирование кода...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec app python -m black src/
	@echo "$(GREEN)✅ Форматирование завершено$(NC)"

# Подключиться к контейнеру приложения
shell-app:
	@echo "$(CYAN)🐚 Подключение к контейнеру приложения...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec app /bin/bash

# Подключиться к контейнеру БД
shell-db:
	@echo "$(CYAN)🐚 Подключение к контейнеру БД...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec db psql -U postgres postgres

# Создать директории для логов и бэкапов
init-dirs:
	@mkdir -p $(BACKUP_DIR)
	@mkdir -p $(LOG_DIR)
	@echo "$(GREEN)✅ Директории созданы$(NC)"

# Показать конфигурацию
config:
	@echo "$(CYAN)⚙️  Конфигурация Docker Compose:$(NC)"
	docker-compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) config

# Быстрая проверка (статус + health)
check:
	@make status
	@echo ""
	@make health

# По умолчанию показывать справку
.DEFAULT_GOAL := help
