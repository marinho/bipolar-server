#!/bin/sh
export DJANGO_SETTINGS_MODULE=bipolar_server.settings
coverage run --source='.' manage.py test
coverage report -m --fail-under=90 bipolar_server/toggle/*.py bipolar_server/*.py
OUT=$?

STATUS="failed"
if [ "$OUT" = "0" ]; then
    STATUS="passed"
fi

exit $OUT
