#!/bin/sh
export DJANGO_SETTINGS_MODULE=bipolar_server.settings
./env/bin/coverage run --source='.' manage.py test
./env/bin/coverage report -m --fail-under=95 bipolar_server/toggle/*.py bipolar_server/*.py
