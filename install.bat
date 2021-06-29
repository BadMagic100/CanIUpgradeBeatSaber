@echo off

if exist venv_for_upgrade_checker\ (
    echo You already installed this! To reinstall the script, get the latest release from GitHub. ^
To reinstall dependencies, delete the venv_for_upgrade_checker folder first.

) else (
    echo Installing to venv_for_upgrade_checker\...
    python -m venv venv_for_upgrade_checker
    venv_for_upgrade_checker\Scripts\python -m pip install --upgrade pip
    venv_for_upgrade_checker\Scripts\python -m pip install -r requirements.txt
    echo Successfully installed dependencies
)
pause