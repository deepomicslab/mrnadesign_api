from scripts import (
    import_antigen,
    import_tantigen,
    import_three_utr,
)
from datetime import timedelta
import datetime

import mrnadesign_api.settings_local as local_settings


def get_current_datetime():
    cur = datetime.datetime.now() + timedelta(hours=8)
    return cur.strftime("%Y-%m-%d %H:%M:%S")


def log(log_str):
    f = open(local_settings.TASKLOG+"additional_scripts/" +
             "01_database_add_data.log", "a")
    f.write(get_current_datetime() + log_str)
    f.close()

import_antigen.add_data()
log(" [completed] scripts.import_antigen\n")


import_tantigen.add_data()
log(" [completed] scripts.import_tantigen\n")

import_three_utr.add_data()
log(" [completed] scripts.import_three_utr\n")