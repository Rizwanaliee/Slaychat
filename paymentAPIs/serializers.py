from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Transaction
from auth_APIs.models import CustomerCard
import stripe
from django.db.models import Q

class TransactionCreateSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id','jobId','paymentId','userId','amount','paymentMethodId','paymentStatus','proposalId']
    def create(self, validated_data):
        tarnsaction = Transaction.objects.create(
        jobId=validated_data["jobId"],
        paymentId = validated_data["paymentId"],
        userId=validated_data["userId"],
        amount=validated_data["amount"],
        paymentMethodId=validated_data["paymentMethodId"],
        paymentStatus=validated_data["paymentStatus"],
        proposalId = validated_data["proposalId"]
        )
        return tarnsaction


class TransactionHistorySerializer(ModelSerializer):
    cardDetails = SerializerMethodField()
    serviceName= SerializerMethodField()
    class Meta:
        model = Transaction
        fields = ['id','paymentId','jobId','userId','amount','paymentMethodId','createdAt','cardDetails','serviceName']
    def get_cardDetails(self, trans):
        card = CustomerCard.objects.filter(id=trans.paymentMethodId.id).first()
        retrive = stripe.PaymentMethod.retrieve(
            card.paymentMethodId,
        )
        return retrive if card else None
    def get_serviceName(self,trans):
        return trans.jobId.searchKeyword if trans else None