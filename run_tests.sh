#!/bin/sh
export DJANGO_SETTINGS_MODULE=project.settings
./env/bin/coverage run --source='.' manage.py test
./env/bin/coverage report -m --fail-under=95 toggle/*.py project/*.py
