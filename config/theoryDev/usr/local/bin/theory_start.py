#!/bin/bash

. /opt/crystal/venv/panel/bin/activate
export THEORY_SETTINGS_MODULE="panel.settings"
/opt/crystal/venv/panel/bin/theory_start.py $1
