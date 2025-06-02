@echo off
REM ==============================================
REM TENNIS SCOREBOARD DEPLOYMENT BATCH SCRIPT
REM ==============================================
REM Batch скрипт для быстрого деплоя в Windows CMD

setlocal enabledelayedexpansion
set COMPOSE_FILE=compose.yml
set ENV_FILE=.env
set APP_NAME=tennis-scoreboard

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="build" goto build
if "%1"=="up" goto up
if "%1"=="down" goto down
if "%1"=="restart" goto restart
if "%1"=="deploy" goto deploy
if "%1"=="status" goto status
if "%1"=="logs" goto logs
if "%1"=="health" goto health
if "%1"=="backup" goto backup
if "%1"=="clean" goto clean
goto help

:help
echo.
echo === TENNIS SCOREBOARD DEPLOYMENT ===
echo.
echo Основные команды:
echo   deploy.bat build     - Собрать все Docker образы
echo   deploy.bat up        - Запустить все сервисы
echo   deploy.bat down      - Остановить все сервисы
echo   deploy.bat restart   - Перезапустить все сервисы
echo   deploy.bat deploy    - Полный деплой (build + up)
echo   deploy.bat status    - Показать статус контейнеров
echo   deploy.bat logs      - Показать логи всех сервисов
echo   deploy.bat health    - Проверить здоровье сервисов
echo   deploy.bat backup    - Создать резервную копию БД
echo   deploy.bat clean     - Очистить Docker ресурсы
echo.
goto end

:build
echo 🔨 Сборка Docker образов...
docker-compose -f %COMPOSE_FILE% --env-file %ENV_FILE% build --no-cache
if %errorlevel%==0 (
    echo ✅ Сборка завершена
) else (
    echo ❌ Ошибка сборки
)
goto end

:up
echo 🚀 Запуск сервисов...
docker-compose -f %COMPOSE_FILE% --env-file %ENV_FILE% up -d
timeout /t 5 /nobreak >nul
call :status
echo ✅ Сервисы запущены
echo 🌐 Приложение доступно по адресу: http://localhost
goto end

:down
echo 🛑 Остановка сервисов...
docker-compose -f %COMPOSE_FILE% --env-file %ENV_FILE% down
echo ✅ Сервисы остановлены
goto end

:restart
echo 🔄 Перезапуск сервисов...
call :down
timeout /t 2 /nobreak >nul
call :up
goto end

:deploy
echo 🚀 ПОЛНЫЙ ДЕПЛОЙ ПРИЛОЖЕНИЯ
call :build
call :up
call :health
echo ✅ ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО
goto end

:status
echo 📊 Статус контейнеров:
docker-compose -f %COMPOSE_FILE% ps
goto end

:logs
echo 📜 Логи всех сервисов:
docker-compose -f %COMPOSE_FILE% logs --tail=50
goto end

:health
echo 🏥 Проверка здоровья сервисов...
echo Проверка nginx (порт 80):
curl -s -f http://localhost >nul 2>&1
if %errorlevel%==0 (
    echo ✅ Nginx: OK
) else (
    echo ❌ Nginx: FAIL
)

echo Проверка приложения (порт 8080):
curl -s -f http://localhost:8080 >nul 2>&1
if %errorlevel%==0 (
    echo ✅ App: OK
) else (
    echo ❌ App: FAIL
)

echo Проверка базы данных:
docker-compose -f %COMPOSE_FILE% exec -T db pg_isready -U postgres >nul 2>&1
if %errorlevel%==0 (
    echo ✅ Database: OK
) else (
    echo ❌ Database: FAIL
)
goto end

:backup
echo 💾 Создание резервной копии БД...
if not exist backups mkdir backups
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set mydate=%%c%%b%%a
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set mytime=%%a%%b
set timestamp=%mydate%_%mytime%
docker-compose -f %COMPOSE_FILE% exec -T db pg_dump -U postgres postgres > backups\tennis_db_backup_%timestamp%.sql
if %errorlevel%==0 (
    echo ✅ Резервная копия создана: backups\tennis_db_backup_%timestamp%.sql
) else (
    echo ❌ Ошибка создания резервной копии
)
goto end

:clean
echo 🧹 Очистка Docker ресурсов...
docker system prune -f
docker image prune -f
echo ✅ Очистка завершена
goto end

:end
endlocal
