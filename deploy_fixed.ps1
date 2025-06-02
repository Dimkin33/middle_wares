# ==============================================
# TENNIS SCOREBOARD DEPLOYMENT SCRIPT (FIXED)
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
    Write-ColorOutput "Обслуживание:" "Green"
    Write-Host "  .\deploy.ps1 backup    - Создать резервную копию БД"
    Write-Host "  .\deploy.ps1 restore   - Восстановить из резервной копии"
    Write-Host "  .\deploy.ps1 clean     - Очистить Docker ресурсы"
    Write-Host "  .\deploy.ps1 shell     - Открыть shell в контейнере app"
    Write-Host "  .\deploy.ps1 test      - Запустить тесты"
    Write-Host ""
}

# Сборка образов
function Build-Images {
    Write-ColorOutput "🔨 Сборка Docker образов..." "Yellow"
    docker-compose -f $COMPOSE_FILE build
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ Сборка завершена успешно!" "Green"
    } else {
        Write-ColorOutput "❌ Ошибка при сборке!" "Red"
        exit 1
    }
}

# Запуск сервисов
function Start-Services {
    Write-ColorOutput "🚀 Запуск сервисов..." "Yellow"
    docker-compose -f $COMPOSE_FILE up -d
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ Сервисы запущены!" "Green"
        Show-Status
    } else {
        Write-ColorOutput "❌ Ошибка при запуске!" "Red"
        exit 1
    }
}

# Остановка сервисов
function Stop-Services {
    Write-ColorOutput "🛑 Остановка сервисов..." "Yellow"
    docker-compose -f $COMPOSE_FILE down
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ Сервисы остановлены!" "Green"
    } else {
        Write-ColorOutput "❌ Ошибка при остановке!" "Red"
        exit 1
    }
}

# Перезапуск сервисов
function Restart-Services {
    Write-ColorOutput "🔄 Перезапуск сервисов..." "Yellow"
    Stop-Services
    Start-Services
}

# Полный деплой
function Deploy-Full {
    Write-ColorOutput "🚀 Полный деплой приложения..." "Cyan"
    Build-Images
    Start-Services
    Start-Sleep -Seconds 5
    Test-Health
}

# Показать статус
function Show-Status {
    Write-ColorOutput "📊 Статус контейнеров:" "Cyan"
    docker-compose -f $COMPOSE_FILE ps
}

# Показать логи
function Show-Logs {
    param([string]$Service = "")
    
    if ($Service -eq "") {
        Write-ColorOutput "📜 Логи всех сервисов:" "Cyan"
        docker-compose -f $COMPOSE_FILE logs --tail=50
    } else {
        Write-ColorOutput "📜 Логи сервиса $Service:" "Cyan"
        docker-compose -f $COMPOSE_FILE logs --tail=50 $Service
    }
}

# Проверка здоровья
function Test-Health {
    Write-ColorOutput "🏥 Проверка здоровья сервисов..." "Cyan"
    
    # Проверка nginx
    Write-Host "Проверка nginx (порт 80):"
    try {
        $response = Invoke-WebRequest -Uri "http://localhost" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-ColorOutput "✅ Nginx: OK" "Green"
        } else {
            Write-ColorOutput "❌ Nginx: Недоступен" "Red"
        }
    } catch {
        Write-ColorOutput "❌ Nginx: Ошибка подключения" "Red"
    }
    
    # Проверка приложения
    Write-Host "Проверка приложения (порт 8080):"
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-ColorOutput "✅ App: OK" "Green"
        } else {
            Write-ColorOutput "❌ App: Недоступно" "Red"
        }
    } catch {
        Write-ColorOutput "❌ App: Ошибка подключения" "Red"
    }
    
    # Проверка базы данных
    Write-Host "Проверка базы данных:"
    $dbContainer = docker-compose -f $COMPOSE_FILE ps -q db
    if ($dbContainer) {
        $dbStatus = docker inspect --format='{{.State.Health.Status}}' $dbContainer 2>$null
        if ($dbStatus -eq "healthy" -or $LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Database: OK" "Green"
        } else {
            Write-ColorOutput "❌ Database: Проблемы" "Red"
        }
    } else {
        Write-ColorOutput "❌ Database: Контейнер не найден" "Red"
    }
}

# Резервное копирование
function Backup-Database {
    Write-ColorOutput "💾 Создание резервной копии базы данных..." "Yellow"
    
    if (!(Test-Path $BACKUP_DIR)) {
        New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
    }
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "$BACKUP_DIR/tennis_db_backup_$timestamp.sql"
    
    docker-compose -f $COMPOSE_FILE exec -T db pg_dump -U postgres postgres > $backupFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ Резервная копия создана: $backupFile" "Green"
    } else {
        Write-ColorOutput "❌ Ошибка создания резервной копии!" "Red"
        exit 1
    }
}

# Восстановление из резервной копии
function Restore-Database {
    Write-ColorOutput "🔄 Восстановление базы данных из резервной копии..." "Yellow"
    
    $backupFiles = Get-ChildItem -Path $BACKUP_DIR -Filter "*.sql" | Sort-Object LastWriteTime -Descending
    
    if ($backupFiles.Count -eq 0) {
        Write-ColorOutput "❌ Файлы резервных копий не найдены в $BACKUP_DIR" "Red"
        return
    }
    
    $latestBackup = $backupFiles[0].FullName
    Write-Host "Восстановление из: $latestBackup"
    
    docker-compose -f $COMPOSE_FILE exec -T db psql -U postgres -d postgres -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
    Get-Content $latestBackup | docker-compose -f $COMPOSE_FILE exec -T db psql -U postgres postgres
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ База данных восстановлена!" "Green"
    } else {
        Write-ColorOutput "❌ Ошибка восстановления!" "Red"
        exit 1
    }
}

# Очистка ресурсов
function Clean-Resources {
    Write-ColorOutput "🧹 Очистка Docker ресурсов..." "Yellow"
    
    docker-compose -f $COMPOSE_FILE down --volumes --remove-orphans
    docker system prune -f
    docker volume prune -f
    
    Write-ColorOutput "✅ Очистка завершена!" "Green"
}

# Открыть shell в контейнере
function Open-Shell {
    Write-ColorOutput "🐚 Открытие shell в контейнере приложения..." "Cyan"
    docker-compose -f $COMPOSE_FILE exec app /bin/bash
}

# Запустить тесты
function Run-Tests {
    Write-ColorOutput "🧪 Запуск тестов..." "Yellow"
    docker-compose -f $COMPOSE_FILE exec app python -m pytest -v
}

# Основная логика
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "build" { Build-Images }
    "up" { Start-Services }
    "down" { Stop-Services }
    "restart" { Restart-Services }
    "deploy" { Deploy-Full }
    "status" { Show-Status }
    "logs" { Show-Logs }
    "logs-app" { Show-Logs "app" }
    "logs-db" { Show-Logs "db" }
    "logs-nginx" { Show-Logs "nginx" }
    "health" { Test-Health }
    "backup" { Backup-Database }
    "restore" { Restore-Database }
    "clean" { Clean-Resources }
    "shell" { Open-Shell }
    "test" { Run-Tests }
    default {
        Write-ColorOutput "❌ Неизвестная команда: $Command" "Red"
        Write-Host ""
        Show-Help
        exit 1
    }
}
