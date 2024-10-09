from rest_framework import serializers
from phage_protein.models import phage_protein_NCBI, phage_protein_PhagesDB, phage_protein_GPD, phage_protein_MGV, phage_protein_TemPhD, phage_protein_GVD,phage_protein_IMG_VR,phage_protein_CHVD,phage_protein_IGVD,phage_protein_GOV2,phage_protein_STV
from phage_protein.models import phage_protein_anticrispr
from phage_protein.models import phage_protein_tmhmm_NCBI, phage_protein_tmhmm_PhagesDB, phage_protein_tmhmm_GPD, phage_protein_tmhmm_MGV, phage_protein_tmhmm_TemPhD, phage_protein_tmhmm_GVD,phage_protein_tmhmm_IMG_VR,phage_protein_tmhmm_CHVD,phage_protein_tmhmm_IGVD,phage_protein_tmhmm_GOV2,phage_protein_tmhmm_STV
from phage_protein.models import phage_crispr
from phage_protein.models import phage_terminators
from phage_protein.models import phage_virulent_factor,phage_antimicrobial_resistance_gene
from Phage_api import settings_local as local_settings

# ['Genbank', 'RefSeq', 'DDBJ', 'EMBL', 'tpg', 'PhagesDB', 'GPD', 'GVD', 'MGV', 'TemPhD']
# [                    'NCBI'                , 'PhagesDB', 'GPD', 'MGV', 'TemPhD', 'GVD']


class phage_protein_NCBI_Serializer(serializers.ModelSerializer):
    sequence = serializers.SerializerMethodField()
    phageid=serializers.SerializerMethodField()
    class Meta:
        model = phage_protein_NCBI
        exclude = ['prosequence']

    def get_sequence(self, obj):
        # datasetlist = ['Genbank', 'RefSeq', 'DDBJ', 'EMBL', 'tpg']
        # dataset = datasetlist[int(obj.dataset)-1]
        # path = local_settings.PROTEINSEQUENCE+str(dataset) + "/" +\
        #     obj.Phage_Acession_ID + '/' + obj.Protein_id + '.fasta'
        # with open(path, 'r') as f:
        #     sequence = f.read()
        return obj.prosequence
    def get_phageid(self,obj):
        return obj.Phage_Acession_ID

class phage_protein_PhagesDB_Serializer(serializers.ModelSerializer):
    sequence = serializers.SerializerMethodField()
    phageid=serializers.SerializerMethodField()
    class Meta:
        model = phage_protein_PhagesDB
        #fields = '__all__'
        exclude = ['prosequence']

    def get_sequence(self, obj):
        # path = local_settings.PROTEINSEQUENCE+'PhagesDB/' + \
        #     obj.Phage_Acession_ID + '/' + obj.Protein_id + '.fasta'
        # with open(path, 'r') as f:
        #     sequence = f.read()
        return obj.prosequence
    def get_phageid(self,obj):
        return obj.Phage_Acession_ID

class phage_protein_GPD_Serializer(serializers.ModelSerializer):
    sequence = serializers.SerializerMethodField()
    phageid=serializers.SerializerMethodField()
    class Meta:
        model = phage_protein_GPD
        exclude = ['prosequence']

    def get_sequence(self, obj):
        # path = local_settings.PROTEINSEQUENCE+'GPD/' + \
        #     obj.Phage_Acession_ID + '/' + obj.Protein_id + '.fasta'
        # with open(path, 'r') as f:
        #     sequence = f.read()
        return obj.prosequence
    def get_phageid(self,obj):
        return obj.Phage_Acession_ID

class phage_protein_MGV_Serializer(serializers.ModelSerializer):
    sequence = serializers.SerializerMethodField()
    phageid=serializers.SerializerMethodField()
    class Meta:
        model = phage_protein_MGV
        exclude = ['prosequence']

    def get_sequence(self, obj):
        # path = local_settings.PROTEINSEQUENCE+'MGV/' + \
        #     obj.Phage_Acession_ID + '/' + obj.Protein_id + '.fasta'
        # with open(path, 'r') as f:
        #     sequence = f.read()
        return obj.prosequence
    def get_phageid(self,obj):
        return obj.Phage_Acession_ID

class phage_protein_TemPhD_Serializer(serializers.ModelSerializer):
    sequence = serializers.SerializerMethodField()
    phageid=serializers.SerializerMethodField()
    class Meta:
        model = phage_protein_TemPhD
        exclude = ['prosequence']

    def get_sequence(self, obj):
        # path = local_settings.PROTEINSEQUENCE+'TemPhD/' + \
        #     obj.Phage_Acession_ID + '/' + obj.Protein_id + '.fasta'
        # with open(path, 'r') as f:
        #     sequence = f.read()
        return obj.prosequence
    def get_phageid(self,obj):
        return obj.Phage_Acession_ID

class phage_protein_GVD_Serializer(serializers.ModelSerializer):
    sequence = serializers.SerializerMethodField()
    phageid=serializers.SerializerMethodField()
    class Meta:
        model = phage_protein_GVD
        exclude = ['prosequence']

    def get_sequence(self, obj):
        # path = local_settings.PROTEINSEQUENCE+'GVD/' + \
        #     obj.Phage_Acession_ID + '/' + obj.Protein_id + '.fasta'
        # with open(path, 'r') as f:
        #     sequence = f.read()
        return obj.prosequence
    def get_phageid(self,obj):
        return obj.Phage_Acession_ID

class phage_protein_IMG_VR_Serializer(serializers.ModelSerializer):
    sequence = serializers.SerializerMethodField()
    phageid=serializers.SerializerMethodField()
    class Meta:
        model = phage_protein_IMG_VR
        exclude = ['prosequence']
    def get_sequence(self, obj):
        return obj.prosequence
    def get_phageid(self,obj):
        return obj.Phage_Acession_ID

class phage_protein_CHVD_Serializer(serializers.ModelSerializer):
    sequence = serializers.SerializerMethodField()
    phageid=serializers.SerializerMethodField()
    class Meta:
        model = phage_protein_CHVD
        exclude = ['prosequence']
    def get_sequence(self, obj):
        return obj.prosequence
    def get_phageid(self,obj):
        return obj.Phage_Acession_ID

class phage_protein_IGVD_Serializer(serializers.ModelSerializer):
    sequence = serializers.SerializerMethodField()
    phageid=serializers.SerializerMethodField()
    class Meta:
        model = phage_protein_IGVD
        exclude = ['prosequence']
    def get_sequence(self, obj):
        return obj.prosequence
    def get_phageid(self,obj):
        return obj.Phage_Acession_ID

class phage_protein_GOV2_Serializer(serializers.ModelSerializer):
    sequence = serializers.SerializerMethodField()
    phageid=serializers.SerializerMethodField()
    class Meta:
        model = phage_protein_GOV2
        exclude = ['prosequence']
    def get_sequence(self, obj):
        return obj.prosequence
    def get_phageid(self,obj):
        return obj.Phage_Acession_ID

class phage_protein_STV_Serializer(serializers.ModelSerializer):
    sequence = serializers.SerializerMethodField()
    phageid=serializers.SerializerMethodField()
    class Meta:
        model = phage_protein_STV
        exclude = ['prosequence']
    def get_sequence(self, obj):
        return obj.prosequence
    def get_phageid(self,obj):
        return obj.Phage_Acession_ID

class phage_protein_anticrispr_Serializer(serializers.ModelSerializer):
    # protein = serializers.SerializerMethodField()
    class Meta:
        model = phage_protein_anticrispr
        fields = '__all__'


class phage_protein_tmhmm_NCBI_Serializer(serializers.ModelSerializer):
    class Meta:
        model = phage_protein_tmhmm_NCBI
        fields = '__all__'


class phage_protein_tmhmm_PhagesDB_Serializer(serializers.ModelSerializer):
    class Meta:
        model = phage_protein_tmhmm_PhagesDB
        fields = '__all__'


class phage_protein_tmhmm_GPD_Serializer(serializers.ModelSerializer):
    class Meta:
        model = phage_protein_tmhmm_GPD
        fields = '__all__'


class phage_protein_tmhmm_MGV_Serializer(serializers.ModelSerializer):
    class Meta:
        model = phage_protein_tmhmm_MGV
        fields = '__all__'


class phage_protein_tmhmm_TemPhD_Serializer(serializers.ModelSerializer):
    class Meta:
        model = phage_protein_tmhmm_TemPhD
        fields = '__all__'


class phage_protein_tmhmm_GVD_Serializer(serializers.ModelSerializer):
    class Meta:
        model = phage_protein_tmhmm_GVD
        fields = '__all__'

class phage_protein_tmhmm_IMG_VR_Serializer(serializers.ModelSerializer):
    class Meta:
        model = phage_protein_tmhmm_IMG_VR
        fields = '__all__'

class phage_protein_tmhmm_CHVD_Serializer(serializers.ModelSerializer):
    class Meta:
        model = phage_protein_tmhmm_CHVD
        fields = '__all__'

class phage_protein_tmhmm_IGVD_Serializer(serializers.ModelSerializer):
    class Meta:
        model = phage_protein_tmhmm_IGVD
        fields = '__all__'

class phage_protein_tmhmm_GOV2_Serializer(serializers.ModelSerializer):
    class Meta:
        model = phage_protein_tmhmm_GOV2
        fields = '__all__'

class phage_protein_tmhmm_STV_Serializer(serializers.ModelSerializer):
    class Meta:
        model = phage_protein_tmhmm_STV
        fields = '__all__'
        

class phage_crispr_Serializer(serializers.ModelSerializer):
    class Meta:
        model = phage_crispr
        fields = '__all__'


class phage_phage_terminators_Serializer(serializers.ModelSerializer):
    class Meta:
        model = phage_terminators
        fields = '__all__'



class phage_virulent_factor_Serializer(serializers.ModelSerializer):
    class Meta:
        model = phage_virulent_factor
        fields = '__all__'

class phage_antimicrobial_resistance_gene_Serializer(serializers.ModelSerializer):
    class Meta:
        model = phage_antimicrobial_resistance_gene
        fields = '__all__'