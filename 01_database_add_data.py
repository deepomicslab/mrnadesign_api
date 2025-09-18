from scripts import (
    import_antigen,
    import_tantigen,
    import_three_utr,
    import_mrna_task,
    import_mirtarbase_db,
    import_gtrnadb,
    import_tsnadb,
    import_rebase_db,
    import_utrdb,
    import_codon,
    import_transcripthub,
)
from scripts.import_isoform import (
    import_meta_data_to_database,
    import_reference_annotation_to_database,
)
from scripts.import_tcrabpairing import import_tcrabpairing

from datetime import timedelta
import datetime

import mrnadesign_api.settings_local as local_settings


def get_current_datetime():
    cur = datetime.datetime.now() + timedelta(hours=8)
    return cur.strftime("%Y-%m-%d %H:%M:%S")


def log(log_str):
    f = open(local_settings.TASKLOG / "additional_scripts" /
             "01_database_add_data.log", "a")
    f.write(get_current_datetime() + log_str)
    f.close()

# import_antigen.add_data()
# log(" [completed] scripts.import_antigen\n")

# import_tantigen.add_data()
# log(" [completed] scripts.import_tantigen\n")

# import_three_utr.add_data()
# log(" [completed] scripts.import_three_utr\n")

import_mrna_task.add_data()
log(" [completed] scripts.import_mrna_task\n")

# import_mirtarbase_db.add_data()
# log(" [completed] scripts.import_mirtarbase_db\n")

# import_gtrnadb.add_data()
# log(" [completed] scripts.import_gtrnadb\n")

# import_tsnadb.add_data()
# log(" [completed] scripts.import_tsnadb\n")

# import_rebase_db.add_data()
# log(" [completed] scripts.import_rebase_db\n")

# import_utrdb.add_data()
# log(" [completed] scripts.import_utrdb\n")

# import_meta_data_to_database.add_data()
# log(" [completed] scripts.import_isoform.import_meta_data_to_database\n")

# import_reference_annotation_to_database.add_data()
# log(" [completed] scripts.import_isoform.import_reference_annotation_to_database\n")

# import_transcripthub.add_data()
# log(" [completed] scripts.import_transcripthub\n")

# import_tcrabpairing.add_data()
# log(" [completed] scripts.import_tcrabpairing\n")

# import_codon.add_data()
# log(" [completed] scripts.import_codon\n")
