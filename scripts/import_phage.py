import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()


def add_data():
    from phage.models import phage
    from datasets.models import datasets

    with open('/home/platform/phage_db/phage_api/csv_data/phage.csv', 'r') as f:
        lines = f.readlines()

    for line in lines:
        l = line.strip().split(", ")
        ds = datasets.objects.get(Acession_ID=l[0])
        phage.objects.create(
            Acession_ID=l[0], Data_Sets=ds, length=l[2], gc_content=l[3], host=l[4], completeness=l[5], taxonomy=l[6], group=l[7], cluster=l[8])


if __name__ == "__main__":
    add_data()
