#!/bin/sh

cd /home/ian/dev/py/mothpi/
. ./venv/bin/activate
python listen3.py
deactivate
