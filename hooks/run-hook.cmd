@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "PLUGIN_ROOT=%SCRIPT_DIR%.."
call "%PLUGIN_ROOT%\hooks\session-start"
