from __future__ import unicode_literals
import multiprocessing

bind = "unix:/home/ssc/sites/datadays/aic_site/gunicorn.sock"
workers = 4
errorlog = "/home/ssc/logs/datadays_gunicorn.log"
loglevel = "debug"
proc_name = "datadays"
