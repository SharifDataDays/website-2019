from __future__ import unicode_literals
import multiprocessing

bind = "unix:/home/datadays/website-2019/aic_site/gunicorn.sock"
workers = 4
errorlog = "/home/datadays/logs/datadays_gunicorn.log"
loglevel = "debug"
proc_name = "datadays"
