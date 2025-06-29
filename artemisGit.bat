@echo off
setlocal enabledelayedexpansion

REM ========================================
REM Git Repository Downloader - Interactive Version
REM Allows you to enter repository URLs manually
REM ========================================

echo.
echo [*] Git Repository Downloader - Interactive
echo ==========================================

REM Check if Git is installed
echo [?] Checking system requirements...
git --version >nul 2>&1
if errorlevel 1 (
    echo [X] Git is not installed or not available in PATH
    echo Please install Git: https://git-scm.com/
    echo.
    pause
    exit /b 1
)
echo [+] Git found

REM Use current directory (relative paths)
set "DOWNLOAD_DIR=.\"
echo [i] Download directory: %DOWNLOAD_DIR%

echo.
echo Please enter the repository information (press Enter for defaults):
echo.

REM Get Repository 1
echo Repository 1:
set /p "REPO1_NAME=Enter name (folder) [default: exercise]: "
if "%REPO1_NAME%"=="" set "REPO1_NAME=exercise"
set /p "REPO1_URL=Enter URL [default: artemis exercise]: "
if "%REPO1_URL%"=="" set "REPO1_URL=https://nutzer@artemis.it.hs-heilbronn.de/git/WNCKTC1TESTAUFGABEJAVA/wncktc1testaufgabejava-exercise.git"

echo.
REM Get Repository 2
echo Repository 2:
set /p "REPO2_NAME=Enter name (folder) [default: solution]: "
if "%REPO2_NAME%"=="" set "REPO2_NAME=solution"
set /p "REPO2_URL=Enter URL [default: artemis solution]: "
if "%REPO2_URL%"=="" set "REPO2_URL=https://nutzer@artemis.it.hs-heilbronn.de/git/WNCKTC1TESTAUFGABEJAVA/wncktc1testaufgabejava-solution.git"

echo.
REM Get Repository 3
echo Repository 3:
set /p "REPO3_NAME=Enter name (folder) [default: tests]: "
if "%REPO3_NAME%"=="" set "REPO3_NAME=tests"
set /p "REPO3_URL=Enter URL [default: artemis tests]: "
if "%REPO3_URL%"=="" set "REPO3_URL=https://nutzer@artemis.it.hs-heilbronn.de/git/WNCKTC1TESTAUFGABEJAVA/wncktc1testaufgabejava-tests.git"

echo.
echo [*] Configuration Summary:
echo   1. %REPO1_NAME% - %REPO1_URL%
echo   2. %REPO2_NAME% - %REPO2_URL%
echo   3. %REPO3_NAME% - %REPO3_URL%

echo.
set /p "CONFIRM=Continue with download? (Y/n): "
if /i not "%CONFIRM%"=="Y" if /i not "%CONFIRM%"=="" (
    echo Aborted.
    pause
    exit /b 0
)

echo.
echo [*] Starting download of repositories...

set "SUCCESS_COUNT=0"
set "TOTAL_COUNT=3"

REM Download repositories if URLs are provided
if not "%REPO1_URL%"=="" if not "%REPO1_NAME%"=="" (
    call :download_repo "%REPO1_URL%" "%REPO1_NAME%"
    if !errorlevel! == 0 set /a SUCCESS_COUNT+=1
)

if not "%REPO2_URL%"=="" if not "%REPO2_NAME%"=="" (
    call :download_repo "%REPO2_URL%" "%REPO2_NAME%"
    if !errorlevel! == 0 set /a SUCCESS_COUNT+=1
)

if not "%REPO3_URL%"=="" if not "%REPO3_NAME%"=="" (
    call :download_repo "%REPO3_URL%" "%REPO3_NAME%"
    if !errorlevel! == 0 set /a SUCCESS_COUNT+=1
)

echo.
echo [*] Download completed!
echo [+] Successful: !SUCCESS_COUNT!/!TOTAL_COUNT! repositories

if !SUCCESS_COUNT! gtr 0 (
    echo.
    echo Downloaded repositories:
    if exist "%REPO1_NAME%" echo   [+] %REPO1_NAME%
    if exist "%REPO2_NAME%" echo   [+] %REPO2_NAME%
    if exist "%REPO3_NAME%" echo   [+] %REPO3_NAME%
)

echo.
echo [*] Download process completed!
echo.
pause
exit /b 0

REM ========================================
REM Function to download a single repository
REM Parameters: %1 = URL, %2 = Name
REM ========================================
:download_repo
set "REPO_URL=%~1"
set "REPO_NAME=%~2"
set "TARGET_PATH=%DOWNLOAD_DIR%%REPO_NAME%"

echo.
echo [~] Downloading repository: %REPO_NAME%
echo URL: %REPO_URL%
echo Target directory: %TARGET_PATH%

REM Check if directory already exists
if exist "%TARGET_PATH%" (
    echo [-] Directory %TARGET_PATH% already exists - deleting automatically...
    
    REM Try to remove readonly attributes and delete
    attrib -r "%TARGET_PATH%\*.*" /s /d >nul 2>&1
    rmdir /s /q "%TARGET_PATH%" >nul 2>&1
    
    REM Check if deletion was successful
    if exist "%TARGET_PATH%" (
        echo [!] Warning: Could not delete directory completely, trying PowerShell...
        powershell -Command "Remove-Item -Path '%TARGET_PATH%' -Recurse -Force" >nul 2>&1
        
        if exist "%TARGET_PATH%" (
            echo [X] Directory could not be deleted: %TARGET_PATH%
            exit /b 1
        )
    )
    echo [+] Old directory successfully deleted
)

REM Clone the repository
echo [~] Cloning repository...
git clone "%REPO_URL%" "%TARGET_PATH%"

if errorlevel 1 (
    echo [X] Error cloning %REPO_NAME%
    exit /b 1
) else (
    echo [+] Repository successfully cloned: %REPO_NAME%
    exit /b 0
)

REM End of function
goto :eof
