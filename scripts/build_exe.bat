@echo off
REM Build dist\SpaceFractionsAgent.exe (run from anywhere on Windows).
setlocal
cd /d "%~dp0\.."
if not exist .venv\Scripts\python.exe (
  py -3.12 -m venv .venv || goto :error
)
.venv\Scripts\python -m pip install -q -r requirements-dev.txt || goto :error
.venv\Scripts\python -m pytest -q || goto :error
.venv\Scripts\python -m PyInstaller --noconfirm --clean SpaceFractionsAgent.spec || goto :error
echo.
echo Built dist\SpaceFractionsAgent.exe
exit /b 0
:error
echo BUILD FAILED
exit /b 1
