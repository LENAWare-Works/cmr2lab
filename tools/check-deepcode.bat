@echo off
setlocal
title DeepCode finder
echo ================================================================
echo   Looking for DeepCode on this machine.
echo   Nothing here changes anything - it only looks.
echo   Screenshot the whole window when it stops.
echo ================================================================
echo.

echo --- 1. is it on PATH -------------------------------------------
where deepcode 2>nul || echo    not on PATH
echo.
where deepcode.cmd 2>nul || echo    no deepcode.cmd on PATH
echo.
where deepcode.exe 2>nul || echo    no deepcode.exe on PATH
echo.

echo --- 2. uv tool list --------------------------------------------
where uv 2>nul || echo    uv itself not found on PATH
echo.
uv tool list 2>&1 || echo    uv tool list failed
echo.

echo --- 3. .local\bin ----------------------------------------------
if exist "%USERPROFILE%\.local\bin" (
  dir /b "%USERPROFILE%\.local\bin\deepcode*" 2>nul || echo    folder exists, no deepcode in it
) else (
  echo    no %USERPROFILE%\.local\bin folder
)
echo.

echo --- 4. npm global ----------------------------------------------
if exist "%APPDATA%\npm" (
  dir /b "%APPDATA%\npm\deepcode*" 2>nul || echo    folder exists, no deepcode in it
) else (
  echo    no %APPDATA%\npm folder
)
echo.

echo --- 5. Program Files -------------------------------------------
if exist "%LOCALAPPDATA%\Programs" (
  dir /b /s "%LOCALAPPDATA%\Programs\*deepcode*" 2>nul || echo    nothing named deepcode under Local\Programs
) else (
  echo    no Local\Programs folder
)
echo.

echo --- 6. python ------------------------------------------------
where python 2>nul || echo    python not on PATH  ^(the bridge needs it^)
python --version 2>&1 || echo.
echo.

echo --- 7. vscode extensions --------------------------------------
if exist "%USERPROFILE%\.vscode\extensions" (
  dir /b "%USERPROFILE%\.vscode\extensions\*deepcode*" 2>nul || echo    no deepcode extension folder
) else (
  echo    no .vscode\extensions folder
)
echo.

echo ================================================================
echo   Done. Screenshot all of this.
echo ================================================================
pause
