from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
import io
from rest_framework import status
from rest_framework.response import Response
from auth_APIs.models import *
from auth_APIs.serializers import *
import jwt
from django.db.models import Q
from slaychat_doer_admin_apis.settings import SECRET_KEY
from chatPanel.models import *
from .serializers import *
from Helpers.helper import send_notification
from paymentAPIs.serializers import *
from django.utils import timezone
from django.db.models import Avg
from support.models import *

class TransactionHistoryForCustomer(RetrieveAPIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY,
                               algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userTypeId=1)).first()
            if user is None:
                response = {
                    "error": {
                        "errorCode": 500,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "User not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            transactions = Transaction.objects.filter(Q(userId=user) & Q(paymentStatus=2)).all().order_by('-id')
            responseData = TransactionHistorySerializer(transactions, many=True)
            response = {
                "error": None,
                "response": {
                    "transactionHistory":responseData.data,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "transactions fetched successfully!"
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)
           

        except Exception as exception:
            response = {
                "error": {
                    "errorCode": 511,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(exception)
                },
                "response": None
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)