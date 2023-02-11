#!/bin/bash

# Copy data dependency to the appdata directory.
mkdir $HOME/.ygo/ > /dev/null 2>&1
rm $HOME/.ygo/*.sql > /dev/null 2>&1
ln -sf "$(pwd)/yugioh_card_database.sql" $HOME/.ygo/yugioh_card_database.sql

printf "ygo Installer:\n\n"
# Cleanup past artifacts
rm ygo > /dev/null 2>&1
rm -rf dist > /dev/null 2>&1
rm main.spec > /dev/null 2>&1
rm -rf build > /dev/null 2>&1

# Install the binary
pip install -r requirements.txt
pyinstaller -F main.py
cp dist/main ygo

# Cleanup artifacts
rm -rf dist > /dev/null 2>&1
rm -rf build > /dev/null 2>&1
rm main.spec > /dev/null 2>&1

# Install globally
sudo rm /usr/local/bin/ygo > /dev/null 2>&1
sudo cp ygo /usr/local/bin/ygo

# Verify Installation
printf "\n\n"
which ygo /usr/local/bin/ygo > /dev/null 2>&1
if [ "$?" -eq 0 ]; then
  printf "Installation Successful!\n"
  printf "Run: ygo --help\n"
else
  printf "Installation failed...\n"
  exit 1
fi