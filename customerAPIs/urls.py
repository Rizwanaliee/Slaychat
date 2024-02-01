from django.urls import path
from customerAPIs import views

urlpatterns = [
    path('search/doer', views.SearchDoerView.as_view()),
    path('suggestion/by/search', views.SuggestionBySearch.as_view()),
    path('doer/details/for/customer', views.DoerProfileAllDetailForCustomerView.as_view())
]
