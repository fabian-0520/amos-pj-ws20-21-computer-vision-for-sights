@echo off
cmd /k "cd /d %~dp0\venv\Scripts & activate & cd /d  %~dp0\amos\gui & python main.py"