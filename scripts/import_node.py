import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()


def add_data():
    from phage_hosts.models import phage_hostnode
    with open('/home/platform/phage_db/phage_api/workspace/csv_data/hostnode.csv', 'r') as f:
        lines = f.readlines()
    for line in lines:
        l = line.strip().split("\t")
        phage_hostnode.objects.create(
            node=l[0], parent=l[1], rank=l[2], phagecount=l[3])


if __name__ == "__main__":
    add_data()
