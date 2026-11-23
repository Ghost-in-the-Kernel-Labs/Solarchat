@echo off
rem Solarchat setup for a Windows computer (TODO 2.11). Safe to run again; needs no admin rights.
rem It finds Python 3.12, makes the .venv, installs the locked packages, puts bin on your PATH and asks for the key.
setlocal
cd /d "%~dp0"
set "SC_BIN=%~dp0bin"
set "PYEXE="

echo [1/5] Looking for Python 3.12...
call :findpython
if defined PYEXE goto havepython

echo Python 3.12 is needed and was not found on this computer.
where winget >nul 2>&1
if errorlevel 1 goto nopython
choice /c YN /n /m "Install Python 3.12 now with winget? [Y/N] "
if errorlevel 2 goto nopython
echo Installing Python 3.12 for this user with winget...
winget install --id Python.Python.3.12 -e --scope user --accept-package-agreements --accept-source-agreements
if errorlevel 1 goto nopython
call :findpython
if defined PYEXE goto havepython

:nopython
echo Install Python 3.12 from python.org, then run setup.cmd again.
goto fail

:havepython
echo Found Python 3.12: "%PYEXE%"

echo [2/5] Making the environment in .venv...
if exist ".venv\Scripts\python.exe" goto venvexists
"%PYEXE%" -m venv .venv
if errorlevel 1 goto venvfail
:venvexists
".venv\Scripts\python.exe" -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 12) else 1)"
if errorlevel 1 goto wrongvenv

echo [3/5] Installing the locked packages (checked by hash; quick when already installed)...
".venv\Scripts\python.exe" -m pip install --only-binary :all: --require-hashes -r requirements.lock
if errorlevel 1 goto pipfail

echo [4/5] Making the solarchat command available in new Command Prompt windows...
powershell -NoProfile -Command "$ErrorActionPreference='Stop'; $b=$env:SC_BIN.TrimEnd('\'); $u=[Environment]::GetEnvironmentVariable('Path','User'); if(-not $u){$u=''}; $has=$false; foreach($e in $u.Split(';')){ if($e.Trim().TrimEnd('\') -ieq $b){$has=$true} }; if(-not $has){ if($u){$n=$u.TrimEnd(';')+';'+$b}else{$n=$b}; [Environment]::SetEnvironmentVariable('Path',$n,'User'); Write-Host 'Added the bin folder to your user PATH.' } else { Write-Host 'The bin folder is already on your user PATH.' }"
if errorlevel 1 goto pathfail
echo New windows will know the solarchat command.

echo [5/5] Checking for the Anthropic key...
call "%~dp0bin\solarchat.cmd" --has-key
if not errorlevel 1 goto keyset
echo The Anthropic key is needed. Type or paste it at the prompt and press Enter.
call "%~dp0bin\solarchat.cmd" --key
if errorlevel 1 goto keyfail
goto keydone
:keyset
echo A key is already set.
:keydone

call "%~dp0bin\solarchat.cmd" --help >nul
if errorlevel 1 goto checkfail
echo.
echo Setup done. Open a new Command Prompt and type: solarchat --demo
if not defined SOLARCHAT_NO_PAUSE pause
endlocal & set "PATH=%SC_BIN%;%PATH%"
exit /b 0

:venvfail
echo Setup stopped: could not make the .venv folder with Python 3.12.
goto fail
:wrongvenv
echo Setup stopped: the .venv folder was made with another Python. Delete the .venv folder and run setup.cmd again.
goto fail
:pipfail
echo Setup stopped: installing the locked packages failed. Check the internet connection and run setup.cmd again.
goto fail
:pathfail
echo Setup stopped: could not add the bin folder to your PATH.
goto fail
:keyfail
echo Setup stopped: the key was not saved. Run it again with: solarchat --key
goto fail
:checkfail
echo Setup stopped: solarchat did not start. Run setup.cmd again, and show this window to the maintainer.
goto fail

:fail
if not defined SOLARCHAT_NO_PAUSE pause
exit /b 1

:findpython
rem Sets PYEXE to a Python 3.12 interpreter's full path, or leaves it empty.
set "PYEXE="
py -3.12 -c "import sys" >nul 2>&1
if errorlevel 1 goto findpath
for /f "delims=" %%P in ('py -3.12 -c "import sys; print(sys.executable)"') do set "PYEXE=%%P"
if defined PYEXE exit /b 0
:findpath
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
exit /b 0
