# ==============================================
# TENNIS SCOREBOARD DEPLOYMENT SCRIPT
# ==============================================
# PowerShell скрипт для быстрого деплоя
# Tennis Scoreboard приложения в Windows

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

# Основные переменные
$COMPOSE_FILE = "compose.yml"
$ENV_FILE = ".env"
$APP_NAME = "tennis-scoreboard"
$BACKUP_DIR = "./backups"
$LOG_DIR = "./logs"

# Функция для вывода цветного текста
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# Показать справку
function Show-Help {
    Write-ColorOutput "=== TENNIS SCOREBOARD DEPLOYMENT ===" "Cyan"
    Write-Host ""
    Write-ColorOutput "Основные команды:" "Green"
    Write-Host "  .\deploy.ps1 build     - Собрать все Docker образы"
    Write-Host "  .\deploy.ps1 up        - Запустить все сервисы"
    Write-Host "  .\deploy.ps1 down      - Остановить все сервисы"
    Write-Host "  .\deploy.ps1 restart   - Перезапустить все сервисы"
    Write-Host "  .\deploy.ps1 deploy    - Полный деплой (build + up)"
    Write-Host ""
    Write-ColorOutput "Мониторинг и диагностика:" "Green"
    Write-Host "  .\deploy.ps1 status    - Показать статус контейнеров"
    Write-Host "  .\deploy.ps1 logs      - Показать логи всех сервисов"
    Write-Host "  .\deploy.ps1 logs-app  - Показать логи приложения"
    Write-Host "  .\deploy.ps1 logs-db   - Показать логи базы данных"
    Write-Host "  .\deploy.ps1 logs-nginx- Показать логи nginx"
    Write-Host "  .\deploy.ps1 health    - Проверить здоровье сервисов"
    Write-Host ""
    Write-ColorOutput "Управление данными:" "Green"
    Write-Host "  .\deploy.ps1 backup    - Создать резервную копию БД"
    Write-Host "  .\deploy.ps1 restore   - Восстановить БД из резервной копии"
    Write-Host "  .\deploy.ps1 clean     - Очистить неиспользуемые Docker ресурсы"
    Write-Host "  .\deploy.ps1 clean-all - Полная очистка (включая volumes)"
    Write-Host ""
    Write-ColorOutput "Разработка и тестирование:" "Green"
    Write-Host "  .\deploy.ps1 test      - Запустить тесты"
    Write-Host "  .\deploy.ps1 shell-app - Подключиться к контейнеру приложения"
    Write-Host "  .\deploy.ps1 shell-db  - Подключиться к контейнеру БД"
}

# Выполнение команд
switch ($Command) {
    "build" {
        Write-ColorOutput "🔨 Сборка Docker образов..." "Cyan"
        docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE build --no-cache
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Сборка завершена" "Green"
        } else {
            Write-ColorOutput "❌ Ошибка сборки" "Red"
        }
        break
    }
    
    "up" {
        Write-ColorOutput "🚀 Запуск сервисов..." "Cyan"
        docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d
        Start-Sleep -Seconds 5
        & $MyInvocation.MyCommand.Path status
        Write-ColorOutput "✅ Сервисы запущены" "Green"
        Write-ColorOutput "🌐 Приложение доступно по адресу: http://localhost" "Yellow"
        break
    }
    
    "down" {
        Write-ColorOutput "🛑 Остановка сервисов..." "Cyan"
        docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE down
        Write-ColorOutput "✅ Сервисы остановлены" "Green"
        break
    }
    
    "restart" {
        Write-ColorOutput "🔄 Перезапуск сервисов..." "Cyan"
        & $MyInvocation.MyCommand.Path down
        Start-Sleep -Seconds 2
        & $MyInvocation.MyCommand.Path up
        break
    }
    
    "deploy" {
        Write-ColorOutput "🚀 ПОЛНЫЙ ДЕПЛОЙ ПРИЛОЖЕНИЯ" "Cyan"
        & $MyInvocation.MyCommand.Path build
        & $MyInvocation.MyCommand.Path up
        & $MyInvocation.MyCommand.Path health
        Write-ColorOutput "✅ ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО" "Green"
        break
    }
    
    "status" {
        Write-ColorOutput "📊 Статус контейнеров:" "Cyan"
        docker-compose -f $COMPOSE_FILE ps
        break
    }
    
    "logs" {
        Write-ColorOutput "📜 Логи всех сервисов:" "Cyan"
        docker-compose -f $COMPOSE_FILE logs --tail=50 -f
        break
    }
    
    "logs-app" {
        Write-ColorOutput "📜 Логи приложения:" "Cyan"
        docker-compose -f $COMPOSE_FILE logs --tail=50 -f app
        break
    }
    
    "logs-db" {
        Write-ColorOutput "📜 Логи базы данных:" "Cyan"
        docker-compose -f $COMPOSE_FILE logs --tail=50 -f db
        break
    }
    
    "logs-nginx" {
        Write-ColorOutput "📜 Логи nginx:" "Cyan"
        docker-compose -f $COMPOSE_FILE logs --tail=50 -f nginx
        break
    }
    
    "health" {
        Write-ColorOutput "🏥 Проверка здоровья сервисов..." "Cyan"
        
        Write-ColorOutput "Проверка nginx (порт 80):" "Yellow"
        try {
            $response = Invoke-WebRequest -Uri "http://localhost" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-ColorOutput "✅ Nginx: OK" "Green"
            } else {
                Write-ColorOutput "❌ Nginx: FAIL" "Red"
            }
        } catch {
            Write-ColorOutput "❌ Nginx: FAIL" "Red"
        }
        
        Write-ColorOutput "Проверка приложения (порт 8080):" "Yellow"
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8080" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-ColorOutput "✅ App: OK" "Green"
            } else {
                Write-ColorOutput "❌ App: FAIL" "Red"
            }
        } catch {
            Write-ColorOutput "❌ App: FAIL" "Red"
        }
        
        Write-ColorOutput "Проверка базы данных:" "Yellow"
        $dbStatus = docker-compose -f $COMPOSE_FILE exec -T db pg_isready -U postgres 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Database: OK" "Green"
        } else {
            Write-ColorOutput "❌ Database: FAIL" "Red"
        }
        break
    }
    
    "backup" {
        Write-ColorOutput "💾 Создание резервной копии БД..." "Cyan"
        if (!(Test-Path $BACKUP_DIR)) {
            New-Item -ItemType Directory -Path $BACKUP_DIR | Out-Null
        }
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupFile = "$BACKUP_DIR/tennis_db_backup_$timestamp.sql"
        docker-compose -f $COMPOSE_FILE exec -T db pg_dump -U postgres postgres > $backupFile
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Резервная копия создана: $backupFile" "Green"
        } else {
            Write-ColorOutput "❌ Ошибка создания резервной копии" "Red"
        }
        break
    }
    
    "restore" {
        Write-ColorOutput "📋 Доступные резервные копии:" "Yellow"
        if (Test-Path "$BACKUP_DIR/*.sql") {
            Get-ChildItem "$BACKUP_DIR/*.sql" | Format-Table Name, LastWriteTime
            Write-ColorOutput "Для восстановления выполните:" "Cyan"
            Write-Host "Get-Content '$BACKUP_DIR/filename.sql' | docker-compose exec -T db psql -U postgres postgres"
        } else {
            Write-ColorOutput "❌ Резервные копии не найдены" "Red"
        }
        break
    }
    
    "clean" {
        Write-ColorOutput "🧹 Очистка Docker ресурсов..." "Cyan"
        docker system prune -f
        docker image prune -f
        Write-ColorOutput "✅ Очистка завершена" "Green"
        break
    }
    
    "clean-all" {
        Write-ColorOutput "⚠️  ВНИМАНИЕ: Это удалит ВСЕ данные приложения!" "Red"
        $confirm = Read-Host "Продолжить? [y/N]"
        if ($confirm -eq "y" -or $confirm -eq "Y") {
            & $MyInvocation.MyCommand.Path down
            docker-compose -f $COMPOSE_FILE down -v --remove-orphans
            docker system prune -af --volumes
            Write-ColorOutput "✅ Полная очистка завершена" "Green"
        } else {
            Write-ColorOutput "❌ Операция отменена" "Yellow"
        }
        break
    }
    
    "test" {
        Write-ColorOutput "🧪 Запуск тестов..." "Cyan"
        docker-compose -f $COMPOSE_FILE exec app python -m pytest tests/ -v
        Write-ColorOutput "✅ Тесты завершены" "Green"
        break
    }
    
    "shell-app" {
        Write-ColorOutput "🐚 Подключение к контейнеру приложения..." "Cyan"
        docker-compose -f $COMPOSE_FILE exec app /bin/bash
        break
    }
    
    "shell-db" {
        Write-ColorOutput "🐚 Подключение к контейнеру БД..." "Cyan"
        docker-compose -f $COMPOSE_FILE exec db psql -U postgres postgres
        break
    }
    
    "config" {
        Write-ColorOutput "⚙️  Конфигурация Docker Compose:" "Cyan"
        docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE config
        break
    }
    
    "check" {
        & $MyInvocation.MyCommand.Path status
        Write-Host ""
        & $MyInvocation.MyCommand.Path health
        break
    }
    
    default {
        Show-Help
        break
    }
}
