from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from auth_APIs.models import *
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.db.models import Avg
from chatPanel.models import *
from support.models import FavouriteDoer
# from chatPanel.serializers import JobSerializer


class AllCountryCodeSerializer(ModelSerializer):
    class Meta:
        model = AllCountries
        fields = ['id', 'sortName', 'countryName', 'phoneCode','flagIconUrl']


class CustomerRegistrationSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'fullName', 'password', 'email',
                  'mobileNo', 'profileImage', 'deviceTypeId', 'userTypeId', 'genderTypeId', 'countryCodeId', 'stripeCustomerId', 'authServiceProviderId', 'authServiceProviderType', 'city','deviceToken']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        if "authServiceProviderType" in validated_data:
            authServiceProviderType = validated_data['authServiceProviderType']
        else:
            authServiceProviderType = None
        if "authServiceProviderId" in validated_data:
            authServiceProviderId = validated_data['authServiceProviderId']
        else:
            authServiceProviderId = None
        if 'stripeCustomerId' in validated_data:
            stripeCustomerId = validated_data['stripeCustomerId']
        else:
            stripeCustomerId = None
        if 'city' in validated_data:
            city = validated_data['city']
        else:
            city = None
        if 'genderTypeId' in validated_data:
            genderTypeId = validated_data['genderTypeId']
        else:
            genderTypeId = None
        if 'deviceToken' in validated_data:
            deviceToken = validated_data['deviceToken']
        else:
            deviceToken = None
        user = User.objects.create(
            fullName=validated_data["fullName"],
            email=validated_data['email'],
            password=make_password(validated_data['password']),
            mobileNo=validated_data["mobileNo"],
            deviceTypeId=validated_data['deviceTypeId'],
            userTypeId=validated_data['userTypeId'],
            genderTypeId=genderTypeId,
            countryCodeId=validated_data["countryCodeId"],
            stripeCustomerId=stripeCustomerId,
            authServiceProviderId=authServiceProviderId,
            authServiceProviderType=authServiceProviderType,
            city=city,
            deviceToken = deviceToken
        )
        return user


class UserProfileSerializer(ModelSerializer):
    countryCodeId = serializers.IntegerField()
    doerAverageRating = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id','fullName', 'email',
                  'mobileNo', 'genderTypeId', 'countryCodeId', 'city', 'profileImage','doerAverageRating']
    def get_doerAverageRating(self,user):
        rating = JobRatingReview.objects.filter(doerId=user).aggregate(Avg('rating'))["rating__avg"] if JobRatingReview.objects.filter(doerId=user).exists() else None
        return round(rating,2) if rating is not None else None


class UserNewProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['fullName', 'email',
                  'mobileNo', 'genderTypeId', 'city', 'countryCodeId', 'profileImage','lat','lng']


class CustomerProfileSerializer(ModelSerializer):
    countryCodeId = serializers.IntegerField()

    class Meta:
        model = User
        fields = ['id','fullName', 'email',
                  'mobileNo', 'genderTypeId', 'countryCodeId', 'profileImage']

class JobSerializer2(ModelSerializer):
    userId = CustomerProfileSerializer()
    class Meta:
        model = Job
        fields = ['id','jobStatus','jobDescription','searchKeyword', 'userId','doerId']
class JobRatingReviewSerializer3(ModelSerializer):
    jobId = JobSerializer2()
    class Meta:
        model = JobRatingReview
        fields = ['jobId', 'rating','review']

class DoerProfileSerializer(ModelSerializer):
    countryCodeId = serializers.IntegerField()
    genderTypeId = serializers.CharField()
    doerAverageRating = serializers.SerializerMethodField()
    averageProductPrice =serializers.SerializerMethodField()
    totalRatingCount = serializers.SerializerMethodField()
    ratings = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id','fullName', 'email',
                  'mobileNo', 'genderTypeId', 'city', 'countryCodeId', 'profileImage','doerAverageRating','averageProductPrice','totalRatingCount','ratings','isAvailable']
    def get_doerAverageRating(self,user):
        rating = JobRatingReview.objects.filter(doerId=user).aggregate(Avg('rating'))["rating__avg"] if JobRatingReview.objects.filter(doerId=user).exists() else None
        return round(rating,2) if rating is not None else None
    def get_averageProductPrice(self,user):
        productPrice = Product.objects.filter(userId=user).aggregate(Avg('productPrice'))["productPrice__avg"] if Product.objects.filter(userId=user).exists() else None
        return round(productPrice,2) if productPrice else None
    def get_totalRatingCount(self, user):
        return JobRatingReview.objects.filter(doerId=user).all().count() if JobRatingReview.objects.filter(doerId=user).exists() else None
    def get_ratings(self,user):
        ratings = JobRatingReview.objects.filter(doerId=user).all().order_by('-jobId')
        ratingsData = {
            "lastRating":JobRatingReviewSerializer3(JobRatingReview.objects.filter(doerId=user).last()).data,
            "allRatings":JobRatingReviewSerializer3(ratings, many=True).data
        }
        return ratingsData if ratings else None

class DoerProfileSerializerForFavrouiteList(ModelSerializer):
    countryCodeId = serializers.IntegerField()
    genderTypeId = serializers.CharField()
    doerAverageRating = serializers.SerializerMethodField()
    averageProductPrice =serializers.SerializerMethodField()
    totalRatingCount = serializers.SerializerMethodField()
    isFavourite = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id','fullName', 'email',
                  'mobileNo', 'genderTypeId', 'city', 'countryCodeId', 'profileImage','doerAverageRating','averageProductPrice','totalRatingCount','isFavourite']
    def get_doerAverageRating(self,user):
        rating = JobRatingReview.objects.filter(doerId=user).aggregate(Avg('rating'))["rating__avg"] if JobRatingReview.objects.filter(doerId=user).exists() else None
        return round(rating,2) if rating is not None else None
    def get_averageProductPrice(self,user):
        productPrice = Product.objects.filter(userId=user).aggregate(Avg('productPrice'))["productPrice__avg"] if Product.objects.filter(userId=user).exists() else None
        return round(productPrice,2) if not None else None
    def get_totalRatingCount(self, user):
        return JobRatingReview.objects.filter(doerId=user).all().count() if JobRatingReview.objects.filter(doerId=user).exists() else None
    def get_isFavourite(self,user):
        return True if FavouriteDoer.objects.filter(Q(doerId=user) & Q(userId=self.context["customer"])).exists() else False

class CatSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'catName']

class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'catName','iconUrl']

class SubCatForTopSearchSerializer(ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['subCatName']

class SubCatForChangesSerializer(ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id','subCatName']


class CatForTopSearchesSerializer(ModelSerializer):
    relatedSubcategories=serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['catName','relatedSubcategories']
    def get_relatedSubcategories(self, catIns):
        return SubCategory.objects.filter(catId=catIns).values_list('subCatName', flat=True)



class SubCatSerializer(ModelSerializer):
    catId = CatSerializer()

    class Meta:
        model = SubCategory
        fields = ['id', 'subCatName', 'catId']


class CompanySerializer(ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'companyName', 'address', 'logo']


class DoerDataSerializer(ModelSerializer):
    companyId = CompanySerializer()

    class Meta:
        model = DoerUserData
        fields = ['idImageUrl', 'companyId','about']


class DoerSelectedSubcategory(ModelSerializer):
    subCatId = SubCatSerializer()

    class Meta:
        model = DoerSelectedSubCategory
        fields = ['id', 'subCatId']


class DoerGellerySerializer(ModelSerializer):
    class Meta:
        model = Gellery
        fields = ['id', 'imageUrl', 'createdAt']


class DoerProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','userId', 'productName','productPrice','productDescription','productImageUrl','createdAt']
    def create(self, validated_data):
        product = Product.objects.create(
            userId = validated_data['userId'],
            productName = validated_data['productName'],
            productPrice = validated_data['productPrice'],
            productDescription =  validated_data['productDescription'],
            productImageUrl =  validated_data['productImageUrl']
        )
        return product

class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','productName','productPrice','productDescription','productImageUrl']


class OfferProductsSerializer(ModelSerializer):
    productId = ProductSerializer()
    class Meta:
        model = OfferProducts
        fields = ['productId']

class DoerOfferSerializer(ModelSerializer):
    class Meta:
        model = Offer
        fields = ['id','userId', 'offerPercentage','offerDescription','createdAt']
    def create(self, validated_data):
        return Offer.objects.create(
            userId=validated_data['userId'],
            offerPercentage=validated_data['offerPercentage'],
            offerDescription=validated_data['offerDescription'],
        )

class DoerOfferListSerializer(ModelSerializer):
    products = serializers.SerializerMethodField()
    productIds = serializers.SerializerMethodField()
    productNames = serializers.SerializerMethodField()
    class Meta:
        model = Offer
        fields = ['id','userId', 'offerPercentage','offerDescription','products','productIds','productNames','createdAt']

    def get_products(self, id):
        offerProducts = OfferProducts.objects.filter(offerId=id).all()
        serializer = OfferProductsSerializer(data = offerProducts, many=True)
        serializer.is_valid()
        return serializer.data

    def get_productIds(self, id):
        offerProducts = OfferProducts.objects.filter(offerId=id).values_list('productId', flat=True)
        return offerProducts
    
    def get_productNames(self, id):
        productNames = OfferProducts.objects.filter(offerId=id).values_list('productId__productName', flat=True)
        return productNames

class SubCatForSearchSerializer(ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'subCatName']

class DoerProfileForSearchSerializer(ModelSerializer):
    countryCodeId = serializers.IntegerField()
    genderTypeId = serializers.CharField()
    subCategories = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    offerPercentage = serializers.SerializerMethodField()
    isFavourite = serializers.SerializerMethodField()
    doerAverageRating = serializers.SerializerMethodField()
    averageProductPrice =serializers.SerializerMethodField()
    totalRatingCount = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id','fullName', 'email',
                  'mobileNo', 'genderTypeId', 'city', 'countryCodeId', 'profileImage','subCategories', 'price', 'offerPercentage','isFavourite','doerAverageRating','averageProductPrice','totalRatingCount']
    def get_subCategories(self, id):
        doerdata = DoerUserData.objects.filter(userId=id).first()
        selectedSubCat = DoerSelectedSubCategory.objects.filter(doerDataId=doerdata).values_list('subCatId', flat=True)
        quer2 = SubCategory.objects.filter(Q(id__in=selectedSubCat)).all()
        subCats = SubCategory.objects.filter(Q(catId__userId=id)).all().union(quer2)
        serializer = SubCatForSearchSerializer(data = subCats, many=True)
        serializer.is_valid()
        return serializer.data

    def get_price(self, id):
        keyword = self.context['keyword']
        if product := Product.objects.filter(
            Q(isDeleted=False) & Q(userId=id) & Q(productName__icontains=keyword)
        ).first():
            return product.productPrice
        if price := Product.objects.filter(
            Q(isDeleted=False) & Q(userId=id)
        ).first():
            return price.productPrice
        else:
            return None
    
    def get_offerPercentage(self, id):
        offer = Offer.objects.filter(Q(isDeleted = False) & Q(userId = id)).first()
        if offer:
            return offer.offerPercentage
        else:
            return None
    def get_isFavourite(self,user):
        return True if FavouriteDoer.objects.filter(Q(doerId=user) & Q(userId=self.context["customer"])).exists() else False
    
    def get_doerAverageRating(self,user):
        rating = JobRatingReview.objects.filter(doerId=user).aggregate(Avg('rating'))["rating__avg"] if JobRatingReview.objects.filter(doerId=user).exists() else None
        return round(rating,2) if rating is not None else None
    def get_averageProductPrice(self,user):
        productPrice = Product.objects.filter(userId=user).aggregate(Avg('productPrice'))["productPrice__avg"] if Product.objects.filter(userId=user).exists() else None
        return round(productPrice,2) if not None else None
    def get_totalRatingCount(self, user):
        return JobRatingReview.objects.filter(doerId=user).all().count() if JobRatingReview.objects.filter(doerId=user).exists() else None
        
class OfferByProductIdSerializer(ModelSerializer):
    offerId = DoerOfferSerializer()
    class Meta:
        model = OfferProducts
        fields = ['offerId']