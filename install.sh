#!/bin/bash
clear
cat EUA.txt
sleep 1
printf '\033[1;92m'
read -p "[*] Enter to continue... " shs
printf "\033[1;92mUpdating...\033[0m\n"
pkg update && pkg upgrade -y
printf "\n\033[1;92mInstalling requirements...\033[0m\n"
pkg install python python-pillow tesseract -y
pip install -r requirements.txt
printf "\033[1;92mDone...\033[0m\n"
