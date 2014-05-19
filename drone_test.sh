#!/bin/sh
export DJANGO_SETTINGS_MODULE=project.settings
coverage run --source='.' manage.py test
coverage report -m --fail-under=90 toggle/*.py project/*.py
OUT=$?

STATUS="failed"
if [ "$OUT" = "0" ]; then
    STATUS="passed"
fi

exit $OUT
