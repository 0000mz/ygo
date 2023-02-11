#!/bin/bash

rm ygo
rm -rf dist > /dev/null
rm -rf build > /dev/null
rm main.spec > /dev/null

pip install -r requirements.txt
pyinstaller -F main.py
cp dist/main ygo

rm -rf dist > /dev/null
rm -rf build > /dev/null
rm main.spec > /dev/null