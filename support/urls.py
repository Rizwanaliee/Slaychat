from django.urls import path
from .views import *

urlpatterns = [
    path('query-list',QueryList.as_view(), name='query-list'),
    path('search-ticket',searchUserFromTickt, name='ticket-search'),
    path('filter-ticket',filterByStatusTicket, name='ticket-filter'),
]
