## Table of contents
1. [What is it?](#what-is-it)
2. [What can it do?](#what-can-it-do)
3. [What can it NOT do?](#what-can-it-not-do)
4. [This says a mod isn't available, what can I do?](#this-says-a-mod-isnt-available-what-can-i-do)
5. [That sounds great, how can I use it?](#that-sounds-great-how-do-i-use-it)
   1. [Installation and setup](#installation-and-setup)
       1. [Install Python](#install-python)
       2. [Download the script](#download-the-script)
       3. [Create a virtual environment](#create-a-virtual-environment-optional)
   2. [Usage](#usage)

## What is it?

A utility script to help players determine whether they can safely upgrade their modded
install of PC Beat Saber.

## What can it do?

This script can help you determine if it's safe to upgrade your PC installation of Beat
Saber by telling you which of your installed mods have a known upgrade available in your
target version. The goal is to help you ask the right questions - rather than "Should I 
upgrade," you will have the information to ask questions like the following:

* "Which of my installed mods are available in the new version?"
* "Which mods have I have installed manually, rather than from Mod Assistant, that I'll
  have to find upgrades for?"
* "Do I really care that (some mod) is missing in the new version, or can I live without it?"

## What can it NOT do?

This tool doesn't know everything. It cannot tell you anything about mods that are not
available on Mod Assistant, nor can it tell you if a mod's functionality has been replaced
by a new mod or the base game.

## This says a mod isn't available, what can I do?

If a mod you want to keep doesn't have an upgrade available, here are some things you can
try to help you decide if you should upgrade:
* **Check beatmods.com**: This is the source of truth for Mod Assistant. You can use this 
  to help find new mods that might replace the functionality you're looking for.
* **Check the `#pc-mods` channel on the BSMG Discord**: This can be a good source for mods,
  especially if they're new or otherwise not yet available in Mod Assistant.
* **Check the mod's GitHub page**: This may contain information about upcoming releases or
  have beta version available. At a minimum, you can usually tell if a mod is actively
  being developed by it
  
## That sounds great, how do I use it?

### Installation and setup

This section assumes that you've never used a Python program or GitHub before. If that's
not the case, you can probably skip to [Usage](#usage).

#### Install Python

You'll need to install a Python interpreter in order to run this script. It's developed and
tested in [Python 3.9.1](https://www.python.org/downloads/release/python-391/), which is the
newest release of Python at the time of writing. It's also tested in 3.7 and 3.8 if you happen
to already have one of those on hand.

Download the installer and make sure you check the box that will either say "Add Python to
environment variables" or "Add Python to PATH" on the first page of the installer. When it's
finished installing, open a command prompt and enter `python --version` to make sure it
worked correctly.

#### Download the script

Download the .zip file from the [latest release](https://github.com/The-Demp/CanIUpgradeBeatSaber/releases/latest)
and extract it in a location of your choosing.

#### Create a virtual environment (Optional)

Python has the concept of a "virtual environment" which is a small and isolated Python
interpreter that allows cleaner dependency management. If you don't create a virtual
environment, there's a possibility that there could be interference between different
Python programs. For many users, this is not a major concern and you can skip to
[Usage](#usage).

<a name="commandLine"></a>
To create a virtual environment, open a command prompt in the folder you unzipped the script
(the place where `upgrade_check.py` is). If you click the whitespace in the file path you
can copy and paste it in the command line, like this:  
`> cd "C:\Users\YourUsername\Documents\CanIUpgradeBeatSaber"`  
Some versions of Windows also have an "Open Command Window Here" if you right click in file
explorer.

Run the following commands to create your virtual environment. It will create a folder called
venv that contains your virtual environment.  
`> python -m venv venv`

To activate your venv:  
`> venv\Scripts\activate.bat`

To deactivate your venv, type `deactivate` while it's running.

#### Install dependencies

Open a command line to the location of the script. See [above](#commandLine) for details
on how to do this. If you're using a virtual environment, activate it.
Run `> pip install -r requirements.txt` to install the required libraries.

### Usage

Open a command line to the location of the script. See [above](#commandLine) for details
on how to do this. If you're using a virtual environment, activate it. First, you'll need
to install additional dependencies. Run `> pip install -r requirements.txt`. Then run the
following command, which will provide more information about the program:  
`> python upgrade_check.py --help`. This includes details on how to use each argument and
whether they are required.

On your first usage of the script, you'll need to provide your Beat Saber installation, like
this:  
`> python upgrade_check.py --install-path "D:\Program Files\Steam\steamapps\common\Beat Saber"`

Your path may be different, and you can find it in Mod Assistant if you're stuck. Note the
quotes around the path, since it contains spaces.

After the initial run, you no longer need to provide this flag, and can just run  
`> python upgrade_check.py`.
