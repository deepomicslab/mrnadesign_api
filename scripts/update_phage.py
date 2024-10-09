import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()
# accesion_id,  Host, Host_source,  Species, Genus, Family, Order, Class, Phylum


def add_data():
    from phage.models import phage

    phages = phage.objects.all()
    for p in phages:
        p.group = p.group.replace("group", 'Cluster')
        p.cluster = p.cluster.replace("cluster", 'Subcluster')
        p.save()


if __name__ == "__main__":
    add_data()
