import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()
# accesion_id,  Host, Host_source,  Species, Genus, Family, Order, Class, Phylum


def add_data():
    from phage.models import phage
    from phage_hosts.models import phage_hosts

    with open('/home/platform/phage_db/phage_api/csv_data/host.csv', 'r') as f:
        lines = f.readlines()

    for line in lines:
        l = line.strip().split("\t")
        dp = phage.objects.get(Acession_ID=l[0])

        phage_hosts.objects.create(
            accesion_id=l[0], host=l[1], host_source=l[2], Species=l[3], Genus=l[4], Family=l[5], Order=l[6], Class=l[7], Phylum=l[8], phage=dp)


if __name__ == "__main__":
    add_data()
