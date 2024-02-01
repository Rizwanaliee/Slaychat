from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin


class AllCountries(models.Model):
    sortName = models.CharField(max_length=255)
    countryName = models.CharField(max_length=255)
    phoneCode = models.IntegerField()
    flagIconUrl = models.CharField(max_length=255, null=True, default=None)

    def __int__(self):
        return self.phoneCode

    class Meta:
        db_table = 'all_countries'

# class AllCountries(models.Model):
#     sortName = models.CharField(max_length=255)
#     countryName = models.CharField(max_length=255)
#     phoneCode = models.IntegerField()
#     flagIconUrl = models.CharField(max_length=255, null=True, default=None)

#     def __int__(self):
#         return self.phoneCode

#     class Meta:
#         db_table = 'all_countries'


class userType(models.Model):
    name = models.CharField(max_length=255, null=False)
    createdAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'userTypes'


class genderType(models.Model):
    name = models.CharField(max_length=255, null=False)
    createdAt = models.DateTimeField(default=now, editable=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'genderTypes'


class deviceType(models.Model):
    name = models.CharField(max_length=255, null=False)
    createdAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'deviceTypes'


class CustomAccountManager(BaseUserManager):
    def create_superuser(self, email, fullName, password, **other_fields):
        # other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)

        return self.create_user(email, fullName, password, **other_fields)


class User(AbstractBaseUser, PermissionsMixin):
    userApprovalStatus = ((1, "pending"), (2, "approved"), (3, "disapproved"))
    providers = ((1, "google"), (2, "facebook"), (3, "apple"))
    fullName = models.CharField(max_length=255, null=True)
    mobileNo = models.CharField(max_length=255, null=False)
    email = models.EmailField(max_length=255, null=False)
    password = models.CharField(max_length=255, null=False)
    isActive = models.BooleanField(default=True)
    isDeleted = models.BooleanField(default=False)
    isVerified = models.BooleanField(default=False)
    deviceTypeId = models.ForeignKey(deviceType, on_delete=models.CASCADE,
                                     related_name='deviceType_ref', db_column='deviceTypeId', null=True, default=None)
    userTypeId = models.ForeignKey(userType, on_delete=models.CASCADE,
                                   related_name='userType_ref', db_column='userTypeId', null=True, default=None)
    genderTypeId = models.ForeignKey(genderType, on_delete=models.CASCADE,
                                     related_name='genderType_ref', db_column='genderTypeId', null=True, default=None)
    deviceToken = models.CharField(max_length=255, null=True)
    profileImage = models.CharField(max_length=255, null=True, blank=True)
    last_login = models.DateTimeField(default=now, editable=False)
    isAvailable = models.BooleanField(default=False)
    isApproved = models.IntegerField(
        choices=userApprovalStatus, null=False, default=1)
    admin_forget_password_token = models.CharField(
        max_length=200, default=False, null=True)
    stripeCustomerId = models.CharField(
        max_length=255, null=True, default=None)

    countryCodeId = models.ForeignKey(AllCountries, on_delete=models.SET_NULL,
                                      related_name='countryCode_ref', db_column='countryCodeId', null=True, default=None)
    authServiceProviderId = models.CharField(
        max_length=255, null=True, unique=True)
    authServiceProviderType = models.IntegerField(choices=providers, null=True)

    city = models.CharField(max_length=255, null=True, default=None)
    lat = models.FloatField(default=0.00, blank=True, null=True)
    lng = models.FloatField(default=0.00, blank=True, null=True)
   

    createdAt = models.DateTimeField(default=now, editable=False)
    updatedAt = models.DateTimeField(default=now, editable=False)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['fullName', 'mobileNo']
    objects = CustomAccountManager()

    class Meta:
        db_table = 'users'


class Company(models.Model):
    compType = ((1, "individual"), (2, "company"))
    companyType = models.IntegerField(
        choices=compType, null=False, default=1)
    companyName = models.CharField(max_length=255, null=False)
    address = models.CharField(max_length=255, null=True, blank=True)
    logo = models.CharField(max_length=255, null=True, blank=True)
    isApproved = models.BooleanField(default=False, null=True)
    userId = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='user_comp_ref', db_column='userId', null=True, default=None)
    createdAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'companies'


class DoerUserData(models.Model):
    userId = models.OneToOneField(User, on_delete=models.CASCADE, unique=True,
                                  related_name='doer_user_ref', db_column='userId')
    userNav = ((1, "personalInformation"), (2, "workServices"),
               (3, "identification"), (4, "billingInfo"), (5, "compInfo"),(6, "about"))
    userNavStatus = models.IntegerField(
        choices=userNav, null=False, default=1)
    idImageUrl = models.CharField(max_length=255, null=True, blank=True)
    companyId = models.ForeignKey(Company, on_delete=models.CASCADE,
                                  related_name='company_info_ref', db_column='companyId', null=True, default=None)
    about = models.TextField(null=True, default=None)
    createdAt = models.DateTimeField(default=now, editable=False)
    updatedAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'doer_data'


class Category(models.Model):
    addedBy = ((1, "admin"), (2, "doer"))
    userId = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='user_cat_ref', db_column='userId', null=False)
    catAddedBy = models.IntegerField(
        choices=addedBy, null=False, default=1)
    iconUrl = models.CharField(max_length=255, null=True, blank=True)
    catName = models.CharField(max_length=255, null=True, blank=True)
    isApproved = models.BooleanField(default=False)
    createdAt = models.DateTimeField(default=now, editable=False)
    updatedAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'category'


class SubCategory(models.Model):
    catId = models.ForeignKey(Category, on_delete=models.CASCADE,
                              related_name='cat_ref', db_column='catId', null=False)
    iconUrl = models.CharField(max_length=255, null=True, blank=True)
    subCatName = models.CharField(max_length=255, null=True, blank=True)
    createdAt = models.DateTimeField(default=now, editable=False)
    updatedAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'sub_category'


class DoerSelectedSubCategory(models.Model):
    doerDataId = models.ForeignKey(DoerUserData, on_delete=models.CASCADE,
                                   related_name='doer_data_ref', db_column='doerDataId')
    subCatId = models.ForeignKey(SubCategory, on_delete=models.CASCADE,
                                 related_name='selected_sub_cat_ref', db_column='subCatId', null=False)
    createdAt = models.DateTimeField(default=now, editable=False)
    updatedAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'doer_selected_sub_category'


class Gellery(models.Model):
    userId = models.ForeignKey(User, on_delete=models.SET_NULL,
                               related_name='doer_gellery_ref', db_column='userId', null=True)
    imageUrl = models.CharField(max_length=255, null=False)
    createdAt = models.DateTimeField(default=now, editable=False)
    updatedAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'gellery'


class Product(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='doer_product_ref', db_column='userId')
    productName = models.CharField(max_length=255, null=False)
    productPrice = models.DecimalField(
        max_length=255, default=0.00, decimal_places=2, max_digits=10, null=False
    )
    productDescription = models.TextField(null=True, default=None)
    productImageUrl = models.CharField(max_length=255, null=False)
    isDeleted = models.BooleanField(default=False)
    createdAt = models.DateTimeField(default=now, editable=False)
    updatedAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'doer_products'


class Offer(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='doer_offer_ref', db_column='userId')
    offerPercentage = models.DecimalField(
        max_length=255, default=0.00, decimal_places=2, max_digits=10, null=False
    )
    offerDescription = models.TextField(null=True, default=None)
    isDeleted = models.BooleanField(default=False)
    createdAt = models.DateTimeField(default=now, editable=False)
    updatedAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'doer_offers'


class OfferProducts(models.Model):
    offerId = models.ForeignKey(Offer, on_delete=models.CASCADE,
                                related_name='doer_offer_products_ref', db_column='offerId')
    productId = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='doer_offer_product_ref', db_column='productId')
    createdAt = models.DateTimeField(default=now, editable=False)
    updatedAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'doer_offer_products'


class CustomerCard(models.Model):
    cardStatusVal = ((1, "ordinary"), (2, "default"))
    userId = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='customerCard', db_column='userId')
    paymentMethodId = models.CharField(max_length=255, null=False, blank=False)
    fingerprint = models.CharField(max_length=255, null=False, blank=False)
    cardStatus = models.IntegerField(choices=cardStatusVal, null=False, default=1)
    createdAt = models.DateTimeField(default=now, editable=False)
    class Meta:
        db_table = 'customer_cards'