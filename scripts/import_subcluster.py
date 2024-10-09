import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()
# subcluster = models.CharField(max_length=200, blank=True, null=True)
# repsequence = models.CharField(max_length=200, blank=True, null=True)
# member = models.IntegerField(blank=True, null=True)
# average_length = models.CharField(max_length=200, blank=True, null=True)
# average_gc = models.CharField(max_length=200, blank=True, null=True)
# host = models.CharField(max_length=200, blank=True, null=True)
# average_genes = models.CharField(max_length=200, blank=True, null=True)
# average_trna = models.CharField(max_length=200, blank=True, null=True)
# cluster = models.ForeignKey(phage_clusters, on_delete=models.DO_NOTHING)


def add_data():
    from phage_clusters.models import phage_clusters
    from phage_subcluster.models import phage_subcluster

    with open('/home/platform/phage_db/phage_api/csv_data/subcluster.csv', 'r') as f:
        lines = f.readlines()

    for line in lines:
        l = line.strip().split("\t")
        dp = phage_clusters.objects.get(cluster=l[5])

        phage_subcluster.objects.create(
            subcluster=l[0], repsequence=l[1], member=l[2], average_length=l[3], average_gc=l[4], cluster=dp, host=l[6])


# subclusterid    representative_sequence member_conut    average_length  average_gc  cluster_id  host
if __name__ == "__main__":
    add_data()
