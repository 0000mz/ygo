#!/bin/bash

rm -rf dist > /dev/null
rm -rf build > /dev/null
rm main.spec > /dev/null

pip install -r requirements.txt
pyinstaller main.py
cp dist/main/main .

rm -rf dist > /dev/null
rm -rf build > /dev/null
rm main.spec > /dev/null