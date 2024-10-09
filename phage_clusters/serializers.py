from rest_framework import serializers
from phage_clusters.models import phage_clusters
from phage_protein.models import phage_protein_NCBI, phage_protein_PhagesDB, phage_protein_GPD, phage_protein_MGV, phage_protein_TemPhD, phage_protein_GVD


class phage_clustersSerializer(serializers.ModelSerializer):

    # trna = serializers.SerializerMethodField()
    # genes = serializers.SerializerMethodField()

    class Meta:
        model = phage_clusters
        fields = '__all__'

    # def get_trna(self, obj):
    #     trnacount = 0
    #     from phage_trna.models import phage_trna
    #     from phage.models import phage
    #     phages = phage.objects.filter(cluster=obj.cluster)
    #     for phage in phages:
    #         trnas = phage_trna.objects.filter(phage_id=phage.id)
    #         trnacount += len(trnas)
    #     return trnacount

    # def get_genes(self, obj):
    #     genecount = 0
    #     from phage_trna.models import phage_trna
    #     from phage.models import phage
    #     phages = phage.objects.filter(cluster=obj.cluster)
    #     for ph in phages:
    #         if ph.Data_Sets.id <= 5:
    #             proteins = phage_protein_NCBI.objects.filter(
    #                 Phage_Acession_ID=ph.Acession_ID)
    #             genecount += len(proteins)
    #         elif ph.Data_Sets.id == 6:
    #             proteins = phage_protein_PhagesDB.objects.filter(
    #                 Phage_Acession_ID=ph.Acession_ID)
    #             genecount += len(proteins)
    #         elif ph.Data_Sets.id == 7:
    #             proteins = phage_protein_GPD.objects.filter(
    #                 Phage_Acession_ID=ph.Acession_ID)
    #             genecount += len(proteins)
    #         elif ph.Data_Sets.id == 8:
    #             proteins = phage_protein_GVD.objects.filter(
    #                 Phage_Acession_ID=ph.Acession_ID)
    #             genecount += len(proteins)
    #         elif ph.Data_Sets.id == 9:
    #             proteins = phage_protein_MGV.objects.filter(
    #                 Phage_Acession_ID=ph.Acession_ID)
    #             genecount += len(proteins)
    #         elif ph.Data_Sets.id == 10:
    #             proteins = phage_protein_TemPhD.objects.filter(
    #                 Phage_Acession_ID=ph.Acession_ID)
    #             genecount += len(proteins)
    #     return genecount/len(phages)
