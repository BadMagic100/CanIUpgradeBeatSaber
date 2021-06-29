@echo off

if exist venv_for_upgrade_checker\ (
    start venv_for_upgrade_checker\Scripts\pythonw upgrade_check.py -s graphical
) else (
    echo You haven't installed the required dependencies. Run install.bat first.
    pause
)