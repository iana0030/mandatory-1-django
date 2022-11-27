from rest_framework import serializers
from .models import Ledger


class LedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ledger
        fields = ['transaction_id', 'amount', 'time_stamp', 'text', 'account']
        
        
        