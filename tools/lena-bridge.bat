@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ===============================================
echo   Lena  ^<->  DeepCode bridge
echo ===============================================
echo.

REM ---- 1. which command runs DeepCode? ask once, then remember ----
set "DC_CMD="
if exist "bridge-cmd.txt" (
  set /p DC_CMD=<"bridge-cmd.txt"
  if "!DC_CMD!"=="" set "DC_CMD="
)

if not defined DC_CMD (
  echo Point me at DeepCode. Paste the full path to it, or just its name
  echo if it is on PATH.  Examples:
  echo    deepcode
  echo    %USERPROFILE%\.local\bin\deepcode.exe
  echo    C:\Users\you\AppData\Roaming\npm\deepcode.cmd
  echo.
  echo Not sure? open another window and run:   where deepcode
  echo and if that finds nothing:              uv tool list
  echo.
  set /p DC_CMD="command> "
  if "!DC_CMD!"=="" goto :fail
  >"bridge-cmd.txt" echo !DC_CMD!
)

set "DC_ARGS=exec {prompt} --json"

REM ---- 2. topics: private, made once, kept in bridge-topics.txt ----
if exist "bridge-topics.txt" (
  for /f "usebackq tokens=1,2 delims==" %%A in ("bridge-topics.txt") do set "%%A=%%B"
) else (
  echo Generating your private topics...
  for /f "tokens=1,2 delims==" %%A in ('python lena-bridge.py --newtopic') do set "%%A=%%B"
  >bridge-topics.txt echo BRIDGE_IN=%BRIDGE_IN%
  >>bridge-topics.txt echo BRIDGE_OUT=%BRIDGE_OUT%
)

echo.
echo   command : !DC_CMD! !DC_ARGS!
echo   in      : !BRIDGE_IN!
echo   out     : !BRIDGE_OUT!
echo.
echo   Testing DeepCode before going live...
echo.
python lena-bridge.py --test "Reply with exactly: bridge test ok"
echo.
echo ---------------------------------------------------------------
echo   Answer above? Good. Press a key to start the bridge.
echo   "command not found" or an error? Press ctrl-c, delete
echo   bridge-cmd.txt, and run this again with the right path.
echo ---------------------------------------------------------------
pause

python lena-bridge.py
echo.
echo Bridge stopped.
pause
goto :eof

:fail
echo.
echo No command given. Nothing started.
pause
