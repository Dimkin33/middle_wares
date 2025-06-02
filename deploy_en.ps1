# ==============================================
# TENNIS SCOREBOARD DEPLOYMENT SCRIPT
# ==============================================
# PowerShell script for Tennis Scoreboard deployment

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

# Variables
$COMPOSE_FILE = "compose.yml"
$ENV_FILE = ".env"
$APP_NAME = "tennis-scoreboard"
$BACKUP_DIR = "./backups"

# Show help
function Show-Help {
    Write-Host "=== TENNIS SCOREBOARD DEPLOYMENT ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Main commands:" -ForegroundColor Green
    Write-Host "  .\deploy_en.ps1 build     - Build Docker images"
    Write-Host "  .\deploy_en.ps1 up        - Start all services"
    Write-Host "  .\deploy_en.ps1 down      - Stop all services"
    Write-Host "  .\deploy_en.ps1 restart   - Restart all services"
    Write-Host "  .\deploy_en.ps1 deploy    - Full deployment (build + up)"
    Write-Host ""
    Write-Host "Monitoring:" -ForegroundColor Green
    Write-Host "  .\deploy_en.ps1 status    - Show container status"
    Write-Host "  .\deploy_en.ps1 logs      - Show all logs"
    Write-Host "  .\deploy_en.ps1 health    - Health check"
    Write-Host ""
    Write-Host "Maintenance:" -ForegroundColor Green
    Write-Host "  .\deploy_en.ps1 backup    - Backup database"
    Write-Host "  .\deploy_en.ps1 clean     - Clean Docker resources"
    Write-Host ""
}

# Build images
function Build-Images {
    Write-Host "Building Docker images..." -ForegroundColor Yellow
    docker-compose -f $COMPOSE_FILE build
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Build completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Build failed!" -ForegroundColor Red
        exit 1
    }
}

# Start services
function Start-Services {
    Write-Host "Starting services..." -ForegroundColor Yellow
    docker-compose -f $COMPOSE_FILE up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Services started!" -ForegroundColor Green
        Show-Status
    } else {
        Write-Host "Failed to start services!" -ForegroundColor Red
        exit 1
    }
}

# Stop services
function Stop-Services {
    Write-Host "Stopping services..." -ForegroundColor Yellow
    docker-compose -f $COMPOSE_FILE down
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Services stopped!" -ForegroundColor Green
    } else {
        Write-Host "Failed to stop services!" -ForegroundColor Red
        exit 1
    }
}

# Restart services
function Restart-Services {
    Write-Host "Restarting services..." -ForegroundColor Yellow
    Stop-Services
    Start-Services
}

# Full deployment
function Deploy-Full {
    Write-Host "Full deployment..." -ForegroundColor Cyan
    Build-Images
    Start-Services
    Start-Sleep -Seconds 5
    Test-Health
}

# Show status
function Show-Status {
    Write-Host "Container status:" -ForegroundColor Cyan
    docker-compose -f $COMPOSE_FILE ps
}

# Show logs
function Show-Logs {
    Write-Host "Service logs:" -ForegroundColor Cyan
    docker-compose -f $COMPOSE_FILE logs --tail=50
}

# Health check
function Test-Health {
    Write-Host "Health check..." -ForegroundColor Cyan
    
    # Check nginx
    Write-Host "Checking nginx (port 80):"
    try {
        $response = Invoke-WebRequest -Uri "http://localhost" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "Nginx: OK" -ForegroundColor Green
        } else {
            Write-Host "Nginx: Failed" -ForegroundColor Red
        }
    } catch {
        Write-Host "Nginx: Connection error" -ForegroundColor Red
    }
    
    # Check app
    Write-Host "Checking app (port 8080):"
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "App: OK" -ForegroundColor Green
        } else {
            Write-Host "App: Failed" -ForegroundColor Red
        }
    } catch {
        Write-Host "App: Connection error" -ForegroundColor Red
    }
    
    # Check database
    Write-Host "Checking database:"
    $dbContainer = docker-compose -f $COMPOSE_FILE ps -q db
    if ($dbContainer) {
        Write-Host "Database: OK" -ForegroundColor Green
    } else {
        Write-Host "Database: Container not found" -ForegroundColor Red
    }
}

# Backup database
function Backup-Database {
    Write-Host "Creating database backup..." -ForegroundColor Yellow
    
    if (!(Test-Path $BACKUP_DIR)) {
        New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
    }
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "$BACKUP_DIR/tennis_db_backup_$timestamp.sql"
    
    docker-compose -f $COMPOSE_FILE exec -T db pg_dump -U postgres postgres > $backupFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Backup created: $backupFile" -ForegroundColor Green
    } else {
        Write-Host "Backup failed!" -ForegroundColor Red
        exit 1
    }
}

# Clean resources
function Clean-Resources {
    Write-Host "Cleaning Docker resources..." -ForegroundColor Yellow
    
    docker-compose -f $COMPOSE_FILE down --volumes --remove-orphans
    docker system prune -f
    docker volume prune -f
    
    Write-Host "Cleanup completed!" -ForegroundColor Green
}

# Main logic
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "build" { Build-Images }
    "up" { Start-Services }
    "down" { Stop-Services }
    "restart" { Restart-Services }
    "deploy" { Deploy-Full }
    "status" { Show-Status }
    "logs" { Show-Logs }
    "health" { Test-Health }
    "backup" { Backup-Database }
    "clean" { Clean-Resources }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Help
        exit 1
    }
}
