@echo off
setlocal
set "SC_PY=%~dp0..\.venv\Scripts\python.exe"
if not exist "%SC_PY%" goto setup
"%SC_PY%" -c "import anthropic" >nul 2>&1
if errorlevel 1 goto setup
goto run
:setup
if defined SOLARCHAT_IN_SETUP goto broken
echo Solarchat is not set up on this computer yet. Running setup...
set "SOLARCHAT_NO_PAUSE=1"
call "%~dp0..\setup.cmd"
if errorlevel 1 exit /b 1
if not exist "%SC_PY%" exit /b 1
goto run
:broken
echo Solarchat still cannot start after setup: the packages in .venv do not load. Delete the .venv folder and run setup.cmd again.
exit /b 1
:run
set "PYTHONPATH=%~dp0.."
"%SC_PY%" -m solarchat.cli %*
exit /b %ERRORLEVEL%
