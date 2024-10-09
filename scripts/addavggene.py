
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")
django.setup()


def countgenessubcluster():
    from phage.models import phage
    from phage_protein.models import phage_protein_NCBI, phage_protein_PhagesDB, phage_protein_GPD, phage_protein_MGV, phage_protein_TemPhD, phage_protein_GVD
    from phage_subcluster.models import phage_subcluster

    for subcluster in phage_subcluster.objects.all():
        genecount = 0
        phages = phage.objects.filter(subcluster=subcluster.subcluster)

        for ph in phages:
            if ph.Data_Sets.id <= 5:
                proteins = phage_protein_NCBI.objects.filter(
                    Phage_Acession_ID=ph.Acession_ID)
                genecount += len(proteins)
            elif ph.Data_Sets.id == 6:
                proteins = phage_protein_PhagesDB.objects.filter(
                    Phage_Acession_ID=ph.Acession_ID)
                genecount += len(proteins)
            elif ph.Data_Sets.id == 7:
                proteins = phage_protein_GPD.objects.filter(
                    Phage_Acession_ID=ph.Acession_ID)
                genecount += len(proteins)
            elif ph.Data_Sets.id == 8:
                proteins = phage_protein_GVD.objects.filter(
                    Phage_Acession_ID=ph.Acession_ID)
                genecount += len(proteins)
            elif ph.Data_Sets.id == 9:
                proteins = phage_protein_MGV.objects.filter(
                    Phage_Acession_ID=ph.Acession_ID)
                genecount += len(proteins)
            elif ph.Data_Sets.id == 10:
                proteins = phage_protein_TemPhD.objects.filter(
                    Phage_Acession_ID=ph.Acession_ID)
                genecount += len(proteins)

        subcluster.average_genes = genecount/len(phages)
        subcluster.save()


def countgenecluster():
    from phage_subcluster.models import phage_subcluster
    from phage_clusters.models import phage_clusters

    for cluster in phage_clusters.objects.all():
        subclusters = phage_subcluster.objects.filter(
            cluster__cluster=cluster.cluster)
        genes = 0
        for subcluster in subclusters:
            genes = genes+float(subcluster.average_genes) * \
                int(subcluster.member)

        cluster.average_genes = genes/int(cluster.member)
        cluster.save()


countgenecluster()
