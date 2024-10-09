from rest_framework import serializers
from phage_lifestyle.models import phage_lifestyle


class phage_lifestyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = phage_lifestyle
        fields = '__all__'
