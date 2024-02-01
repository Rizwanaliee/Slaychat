from django.urls import path
from auth_APIs import views

urlpatterns = [
    path('country/code/list',views.CountryCodeList.as_view()),
    path('customer/resgistration', views.CustomerRegistrationView.as_view()),
    path('login', views.LoginView.as_view()),
    path('account/verify', views.AccountVerification.as_view()),
    path('change/password', views.ForgetPasswordUpdate.as_view()),
    path('doer/registration', views.DoerRegistrationView.as_view()),
    path('logout', views.LogoutView.as_view()),
    path('profile/update', views.BasicUpdateProfile.as_view()),
    path('profile/details', views.ProfileDetailView.as_view()),
    path('customer/social/signIn/signUp', views.CustomerServiceProviderRegisterLogin.as_view()),
    path('update/password', views.ChangePasswordView.as_view()),
    path('password/verification', views.PasswordVerification.as_view()),
    path('doer/nav/status', views.DoerNavStatusView.as_view()),
    path('sub/cat/list', views.SubCatListView.as_view()),
    path('add/custom/category', views.AddCustomCategoryView.as_view()),
    path('doer/select/sub/category', views.SelectSubCategoriesViews.as_view()),
    path('add/identity', views.AddIdentityView.as_view()),
    path('add/about',views.AddAboutView.as_view()),
    path('company/list', views.CompanyList.as_view()),
    path('add/company', views.AddCompanyView.as_view()),
    path('add/other/company', views.AddOtherCompanyView.as_view()),
    path('complete/doer/profile', views.CompleteDoerProfile.as_view()),
    ####
    path('doer/user/all/detail', views.DoerProfileAllDetailView.as_view()),
    path('update/servicess', views.ServicesUpdateView.as_view()),
    path('identity/update', views.IdentityUpdateView.as_view()),
    path('gellery/list/add/delete', views.GelleryListAddLdelete.as_view()),
    path('product/list/add/delete', views.ProductListAddLdelete.as_view()),
    path('offer/list/add/update/delete', views.OfferListAddEditdelete.as_view()),
    path('category/list',views.CategoryList.as_view()),
    #panel flow APIs
    path('offer/list/by/product', views.OfferListByProductId.as_view()),
    path('device/token/update', views.DeviceTokenUpdate.as_view()),
    path('lat/long/update', views.LatLongUpdate.as_view()),
    path('top/searches/services', views.TopSearches.as_view()),
    path('send/notification/for/any/user', views.SendNotificationForAnyUser.as_view()),
    path('delete/my/account', views.DeleteMyAccount.as_view()),
    path('testing',views.Testing.as_view())
]
