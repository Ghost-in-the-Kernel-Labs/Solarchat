@echo off
setlocal
set "PYTHONPATH=%~dp0.."
"%~dp0..\.venv\Scripts\python.exe" -m solarchat.cli %*
exit /b %ERRORLEVEL%
