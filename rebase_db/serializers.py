from rest_framework import serializers
from rebase_db.models import rebase_data, rebase_enzyme_link


class rebaseDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = rebase_data
        fields = '__all__'

class rebaseLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = rebase_enzyme_link
        fields = '__all__'