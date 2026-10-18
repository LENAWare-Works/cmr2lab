@echo off
setlocal
cd /d "%~dp0"

REM ============================================================
REM  Lena <-> DeepCode bridge.  Double-click this file.
REM  First run asks for DeepCode's command, then remembers it.
REM ============================================================

if exist "dc-command.txt" ( set /p DC_CMD=<dc-command.txt ) else (
  echo.
  echo What command starts DeepCode?  Example:  deepcode
  set /p DC_CMD="> "
  if "%DC_CMD%"=="" ( echo No command given. & pause & exit /b 1 )
  >dc-command.txt echo %DC_CMD%
)

where python >nul 2>&1 && ( set PY=python ) || (
  where py >nul 2>&1 && ( set PY=py ) || (
    echo.
    echo Python is not installed. Get it from python.org and tick "Add to PATH".
    pause & exit /b 1
  )
)

echo.
echo Bridge running. DeepCode command: %DC_CMD%
echo Leave this window open. Close it to stop.
echo.

%PY% lena-bridge.py
echo.
echo Bridge stopped.
pause
