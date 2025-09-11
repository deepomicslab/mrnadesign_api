from rest_framework import serializers
from antigen.models import antigen

from transcripthub.models import transcripthub_assembly, transcripthub_annotation, genome_seq

class transcripthubAssemblySerializer(serializers.ModelSerializer):
    class Meta:
        model = transcripthub_assembly
        fields = '__all__'

class transcripthubAnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = transcripthub_annotation
        fields = '__all__'

class genomeSeqSerializer(serializers.ModelSerializer):
    class Meta:
        model = genome_seq
        fields = '__all__'