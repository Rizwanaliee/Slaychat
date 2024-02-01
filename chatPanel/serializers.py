from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers
from .models import *
from auth_APIs.serializers import CustomerProfileSerializer,ProductSerializer,DoerOfferSerializer,DoerProfileSerializer,UserProfileSerializer
from django.db.models import Q
from django.db.models import Avg
from auth_APIs.models import *
from support.models import FavouriteDoer, QueryTicket,QueryChat


class JobAssignSerializer(ModelSerializer):
    class Meta:
        model = JobAssign
        fields = ['id', 'assignStatus', 'jobId', 'doerId', 'createdAt']

    def create(self, validated_data):
        jobAssign = JobAssign.objects.create(
            # assignStatus = validated_data['assignStatus'],
            jobId=validated_data['jobId'],
            doerId=validated_data['doerId'],

        )
        return jobAssign


class ProposalSerializer(ModelSerializer):
    class Meta:
        model = JobProposal
        fields = ['id', 'jobId', 'doerId', 'amount',
                  'discountAmount', 'shortDescription']

    def create(self, validated_data):
        proposal = JobProposal.objects.create(
            jobId=validated_data['jobId'],
            doerId=validated_data['doerId'],
            amount=validated_data['amount'],
            discountAmount=validated_data['discountAmount'],
            shortDescription=validated_data['shortDescription'],
        )
        return proposal

class JobSerializer(ModelSerializer):
    userId = CustomerProfileSerializer()
    class Meta:
        model = Job
        fields = ['id','jobStatus','jobDescription','searchKeyword', 'userId','doerId']


class JobAssignSerializer1(ModelSerializer):
    jobId = JobSerializer()
    class Meta:
        model = JobAssign
        fields = ['jobId', 'doerId','createdAt']

class JobProposalProductsSerializer(ModelSerializer):
    productId = ProductSerializer()
    offerId = DoerOfferSerializer()
    class Meta:
        model = JobProposalProduct
        fields = ['productId','offerId','quantity','discountedAmount']

class ProposalAllSerializer(ModelSerializer):
    products = SerializerMethodField()
    doerId = DoerProfileSerializer()
    doerAverageRating = SerializerMethodField()
    class Meta:
        model = JobProposal
        fields = ['id', 'jobId', 'doerId', 'amount',
                  'discountAmount', 'shortDescription','products','doerAverageRating']
    def get_products(self, id):
        products = JobProposalProduct.objects.filter(proposalId=id).all()
        serilerz = JobProposalProductsSerializer(data=products, many=True)
        serilerz.is_valid()
        return serilerz.data
    
    def get_doerAverageRating(self,proposal):
        averageRating = JobRatingReview.objects.filter(doerId=proposal.doerId.id).aggregate(Avg('rating'))["rating__avg"] if JobRatingReview.objects.filter(doerId=proposal.doerId.id).exists() else None
        return round(averageRating,2) if averageRating is not None else None

class JobRatingReviewSerializer(ModelSerializer):
    class Meta:
        model = JobRatingReview
        fields = ['jobId', 'rating','review','doerId','userId']
    def validate(self, attrs):
        return super().validate(attrs)
    def create(self, validated_data):
        return super().create(validated_data)

class JobRatingReviewSerializer2(ModelSerializer):
    jobId = JobSerializer()
    class Meta:
        model = JobRatingReview
        fields = ['jobId', 'rating','review']

class JobRatingReviewSerializer3(ModelSerializer):
    class Meta:
        model = JobRatingReview
        fields = ['jobId', 'rating','review']

class CustomerCompleteJobsSerializer(ModelSerializer):
    userId = CustomerProfileSerializer()
    doerId = DoerProfileSerializer()
    jobRating = SerializerMethodField()
    amount = SerializerMethodField()
    proposalDetails=SerializerMethodField()
   
    class Meta:
        model = Job
        fields = ['id', 'jobDescription','jobStatus','searchKeyword','userId','doerId','jobRating','amount','createdAt','proposalDetails']
    
    def get_jobRating(self, jobIns):
        rating = JobRatingReview.objects.filter(jobId = jobIns).first()
        rat =JobRatingReviewSerializer3(rating)
        return rat.data
    def get_amount(self, jobIns):
        amount =JobProposal.objects.filter(Q(jobId=jobIns) & Q(status__in=[1,2])).first().amount if JobProposal.objects.filter(Q(jobId=jobIns) & Q(status__in=[1,2])).exists() else None
        return amount
    def get_proposalDetails(selg,jobIns):
        proposal =JobProposal.objects.filter(Q(jobId=jobIns) & Q(status=2)).first()
        return ProposalAllSerializer(proposal).data if proposal else None
class ProposedJobsSerializer(ModelSerializer):
    userId = CustomerProfileSerializer()
    proposalId = SerializerMethodField()
   
    class Meta:
        model = Job
        fields = ['id', 'jobDescription','jobStatus','searchKeyword','userId','proposalId','createdAt']
    
    def get_proposalId(self, jobIns):
        proposal =JobProposal.objects.filter(Q(jobId=jobIns) & Q(status=1) & Q(doerId=self.context["doerId"])).first()
        return ProposalAllSerializer(proposal).data


class CustomerJobHistorySerializer(ModelSerializer):
    proposals = SerializerMethodField()
    otherParams = SerializerMethodField()
    doerId = DoerProfileSerializer()
    class Meta:
        model = Job
        fields = ['id', 'jobDescription','searchKeyword','otherParams','isJobShare','doerId','createdAt','proposals']
    def get_proposals(self, id):
        proposals = JobProposal.objects.filter(Q(jobId = id) & Q(status__in=[1,2])).all().order_by('-status')
        serilerz = ProposalAllSerializer(data=proposals, many=True)
        serilerz.is_valid()
        return serilerz.data
    def get_otherParams(self, id):
        job = Job.objects.filter(id=id.id).first()
        if Job.objects.filter(Q(id=id.id) & Q(jobStatus__in=[1,2]) & Q(isJobShare=True)).exists():
            status = {
                "customStatus":"Posted"
            }

        elif Job.objects.filter(Q(id=id.id) & Q(jobStatus=3)).exists():
            status = {
                "customStatus":"Running",
                "doerAverageRating":round(JobRatingReview.objects.filter(jobId__doerId=Job.objects.filter(Q(id=id.id) & Q(jobStatus=3)).first().doerId.id).aggregate(Avg('rating'))["rating__avg"]) if JobRatingReview.objects.filter(doerId=job.doerId.id).exists() else None
            }
        else:
            status = {}
        return status
    

class TopRatedDoersSerializer(ModelSerializer):
    countryCodeId = serializers.IntegerField()
    genderTypeId = serializers.CharField()
    doerAverageRating = serializers.SerializerMethodField()
    averageProductPrice =serializers.SerializerMethodField()
    totalRatingCount = serializers.SerializerMethodField()
    doerServices = SerializerMethodField()
    isFavourite = SerializerMethodField()

    class Meta:
        model = User
        fields = ['id','fullName', 'email',
                  'mobileNo', 'genderTypeId', 'city', 'countryCodeId', 'profileImage','doerAverageRating','averageProductPrice','totalRatingCount','doerServices','isFavourite']
    def get_doerAverageRating(self,user):
        rating = JobRatingReview.objects.filter(doerId=user).aggregate(Avg('rating'))["rating__avg"] if JobRatingReview.objects.filter(doerId=user).exists() else None
        return round(rating,2) if rating is not None else None
    def get_averageProductPrice(self,user):
        productPrice = Product.objects.filter(userId=user).aggregate(Avg('productPrice'))["productPrice__avg"] if Product.objects.filter(userId=user).exists() else None
        return round(productPrice,2) if not None else None
    def get_totalRatingCount(self, user):
        return JobRatingReview.objects.filter(doerId=user).all().count() if JobRatingReview.objects.filter(doerId=user).exists() else None
    def get_doerServices(self, user):
        return DoerSelectedSubCategory.objects.filter(doerDataId__userId=user).all().values_list('subCatId__subCatName',flat=True) if DoerSelectedSubCategory.objects.filter(doerDataId__userId=user).exists() else None
    def get_isFavourite(self,user):
        return True if FavouriteDoer.objects.filter(Q(doerId=user) & Q(userId=self.context["customer"])).exists() else False


### for help and support ###

class QuerySerializer(ModelSerializer):
    class Meta:
        model=QueryTicket
        fields= ['id','status','queryTitle','query','userId','createdAt']
    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        return super().create(validated_data)

class CreatChatRecordSerializer(ModelSerializer):
    class Meta:
        model=QueryChat
        fields = ['id', 'ticketId','senderId','receiverId','message','createdAt']
    def validate(self, attrs):
        return super().validate(attrs)
    def create(self, validated_data):
        return super().create(validated_data)

        
class ChatDetailSerializer(serializers.ModelSerializer):
    senderId = UserProfileSerializer()
    receiverId = UserProfileSerializer()

    class Meta:
        model = QueryChat
        fields = ['id', 'message', 'receiverId', 'senderId','createdAt']
