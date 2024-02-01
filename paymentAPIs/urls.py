from django.urls import path
from .views import *

urlpatterns = [
    path('transaction/history/customer',TransactionHistoryForCustomer.as_view())
]
