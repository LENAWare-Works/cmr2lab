@echo off
setlocal
cd /d "%~dp0"

REM ============================================================
REM  Lena <-> DeepCode headless bridge.  Double-click this file.
REM  Needs Python (python.org, tick "Add to PATH").
REM ============================================================

REM --- where is deepcode? uv puts it here, not on PATH ---
if not defined DC_CMD (
  for %%P in ("%USERPROFILE%\.local\bin\deepcode.exe" "%USERPROFILE%\.local\bin\deepcode.cmd" "%USERPROFILE%\.local\bin\deepcode") do (
    if exist %%P set "DC_CMD=%%~P"
  )
)
if not defined DC_CMD set "DC_CMD=deepcode"

REM --- the bridge replaces {prompt} with what Lena said ---
if not defined DC_ARGS set "DC_ARGS=exec {prompt} --json"

REM --- private topics, remembered after the first run ---
if exist "bridge-topics.txt" (
  for /f "usebackq tokens=1,2 delims==" %%A in ("bridge-topics.txt") do set "%%A=%%B"
) else (
  echo.
  echo Generating your private topics...
  for /f "tokens=1,2 delims==" %%A in ('python lena-bridge.py --newtopic') do set "%%A=%%B"
  >bridge-topics.txt echo BRIDGE_IN=%BRIDGE_IN%
  >>bridge-topics.txt echo BRIDGE_OUT=%BRIDGE_OUT%
)

echo.
echo  command : %DC_CMD% %DC_ARGS%
echo  in      : %BRIDGE_IN%
echo  out     : %BRIDGE_OUT%
echo.
echo  Testing DeepCode once before going live...
echo.
python lena-bridge.py --test "Reply with exactly: bridge test ok"
echo.
echo  If that printed an answer, the bridge works. Press a key to run it.
echo  If it said "command not found", run:  uv tool list
pause

python lena-bridge.py
echo.
echo Bridge stopped.
pause
