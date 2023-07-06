#!/bin/sh

cd /home/ian/dev/py/mothpi/
. ./venv/bin/activate
python gdrive-upload.py
deactivate
