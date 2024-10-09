from rest_framework import serializers
from phage_hosts.models import phage_hosts
from phage_hosts.models import phage_hostnode


class phage_hostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = phage_hosts
        fields = '__all__'


class phage_hostnodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = phage_hostnode
        fields = '__all__'
