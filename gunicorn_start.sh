#!/bin/sh

export DJANGO_SETTINGS_MODULE='aic_site.settings.development'

exec /home/datadays/env/bin/gunicorn -c gunicorn.conf.py aic_site.wsgi:application
