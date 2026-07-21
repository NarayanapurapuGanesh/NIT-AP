<#
.SYNOPSIS
    FacultyIQ Development Environment Lifecycle Manager
.DESCRIPTION
    Automates building, running, stopping, migrating, and health checking the FacultyIQ monorepo environment.
.EXAMPLE
    .\scripts\dev.ps1 start
    .\scripts\dev.ps1 build
    .\scripts\dev.ps1 health
#>

param (
    [Parameter(Position=0, Mandatory=$false)]
    [ValidateSet("start", "stop", "restart", "build", "clean", "migrate", "health")]
    [string]$Action = "start"
)

$ErrorActionPreference = "Stop"
$DockerComposeFile = "docker/docker-compose.yml"

function Show-Header {
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "                FacultyIQ Dev Lifecycle Manager           " -ForegroundColor Cyan
    Write-Host "==========================================================" -ForegroundColor Cyan
}

Show-Header

switch ($Action) {
    "start" {
        Write-Host "[+] Starting infrastructure containers..." -ForegroundColor Green
        docker-compose -f $DockerComposeFile up -d
        Write-Host "[+] Infrastructure containers operational." -ForegroundColor Green
    }

    "stop" {
        Write-Host "[-] Stopping infrastructure containers..." -ForegroundColor Yellow
        docker-compose -f $DockerComposeFile down
        Write-Host "[-] Containers stopped." -ForegroundColor Yellow
    }

    "restart" {
        Write-Host "[*] Restarting infrastructure containers..." -ForegroundColor Yellow
        docker-compose -f $DockerComposeFile restart
    }

    "build" {
        Write-Host "[+] Building ASP.NET Core 9 Backend Solution..." -ForegroundColor Green
        dotnet build backend/FacultyIQ.sln --configuration Release
        
        Write-Host "[+] Building Next.js Frontend..." -ForegroundColor Green
        Push-Location frontend
        npm run build
        Pop-Location
        Write-Host "[+] Monorepo build completed successfully." -ForegroundColor Green
    }

    "clean" {
        Write-Host "[!] Cleaning build artifacts..." -ForegroundColor Yellow
        Get-ChildItem -Path backend -Include bin,obj -Recurse | Remove-Item -Recurse -Force
        if (Test-Path "frontend/.next") { Remove-Item "frontend/.next" -Recurse -Force }
        Write-Host "[!] Clean completed." -ForegroundColor Green
    }

    "migrate" {
        Write-Host "[+] Applying Entity Framework Core Database Migrations..." -ForegroundColor Green
        dotnet ef database update --project backend/src/FacultyIQ.Persistence --startup-project backend/src/FacultyIQ.Api
        Write-Host "[+] Database migration completed." -ForegroundColor Green
    }

    "health" {
        Write-Host "[*] Checking container health statuses..." -ForegroundColor Cyan
        docker-compose -f $DockerComposeFile ps
    }
}
