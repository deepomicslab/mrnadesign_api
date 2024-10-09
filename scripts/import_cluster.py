import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()

# cluster = models.CharField(max_length=200, blank=True, null=True)
# subclusters = models.CharField(max_length=200, blank=True, null=True)
# member = models.IntegerField(blank=True, null=True)
# average_length = models.CharField(max_length=200, blank=True, null=True)
# average_gc = models.CharField(max_length=200, blank=True, null=True)


def add_data():
    from phage_clusters.models import phage_clusters

    with open('/home/platform/phage_db/phage_api/csv_data/cluster.csv', 'r') as f:
        lines = f.readlines()

    for line in lines:
        l = line.strip().split(", ")
        phage_clusters.objects.create(
            cluster=l[0], subclusters=l[1], member=l[2], average_length=l[3], average_gc=l[4])


if __name__ == "__main__":
    add_data()
