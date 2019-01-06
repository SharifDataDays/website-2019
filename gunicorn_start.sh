#!/bin/sh

export DJANGO_SETTINGS_MODULE='aic_site.settings.development'

exec /home/ssc/VEnvs/datadays/bin/gunicorn -c gunicorn.conf.py aic_site.wsgi:application
