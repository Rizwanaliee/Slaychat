from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser
import io
from rest_framework import status
from rest_framework.response import Response
from auth_APIs.models import *
from auth_APIs.serializers import *
import jwt
from django.db.models import Q
from slaychat_doer_admin_apis.settings import SECRET_KEY
from auth_APIs.serializers import *

class SearchDoerView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userTypeId=1)).first()
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
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            keyword = pythonData.get('keyword', False)
            if not keyword:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "keyword field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
            selectedSubcats = DoerSelectedSubCategory.objects.filter(Q(Q(subCatId__subCatName__icontains=keyword) | Q(subCatId__catId__catName__icontains = keyword)) & Q(subCatId__catId__isApproved=True)).first()
            if selectedSubcats:
                catUsers = DoerSelectedSubCategory.objects.filter(Q(Q(subCatId__subCatName__icontains=keyword) | Q(subCatId__catId__catName__icontains = keyword)) & Q(subCatId__catId__isApproved=True)).values_list('doerDataId__userId', flat=True)
                productsFilter = Product.objects.filter(userId__in = catUsers).values_list('userId', flat=True)
                doers = User.objects.filter(Q(id__in=productsFilter) & Q(userTypeId=2) & Q(isDeleted=False) & Q(isVerified=True) & Q(isApproved=2)).all()
                serializer = DoerProfileForSearchSerializer(data=doers, many=True, context={'keyword': keyword,'customer':user})
                serializer.is_valid()
                if request.query_params:
                    if int(request.query_params.get('sort_by')) == 1:
                        doerData = serializer.data
                    elif int(request.query_params.get('sort_by')) == 2:
                        doerData = sorted(serializer.data, key=lambda x: x['doerAverageRating'], reverse=True)
                    elif int(request.query_params.get('sort_by')) == 3:
                        
                        if not user.lat or user.lat != 0:
                            doerData = serializer.data
                        else:
                            latitude = user.lat
                            longitude = user.lng
                            limit = 5000
                            radius = 25
                            query = """SELECT id ,( 6371 * acos( cos( radians(%2f) ) * cos( radians( lat ) ) * cos( radians( lng ) - radians(%2f) ) + sin( radians(%2f) ) * sin(radians(lat)) ) ) AS distance FROM users HAVING distance < %2f ORDER BY distance asc LIMIT 0, %d""" % (
                                float(latitude),
                                float(longitude),
                                float(latitude),
                                radius,
                                limit
                            )
                            usersQuerySet = User.objects.raw(query)
                            user_Ids = []
                            for user_id in usersQuerySet:
                                user_Ids.append(user_id.id)
                            doersNear = User.objects.filter(Q(id__in=user_Ids) & Q(id__in=productsFilter) & Q(userTypeId=2) & Q(isDeleted=False) & Q(isVerified=True) & Q(isApproved=2)).all()
                            serializer = DoerProfileForSearchSerializer(data=doersNear, many=True, context={'keyword': keyword,'customer':user})
                            serializer.is_valid()
                            doerData = serializer.data
                    elif int(request.query_params.get('sort_by')) == 4:
                        doerData = sorted(serializer.data, key=lambda x: x['price'], reverse=False)
                    elif int(request.query_params.get('sort_by')) == 5:
                        doerData = sorted(serializer.data, key=lambda x: x['price'], reverse=True)
                    else:
                        doerData = serializer.data
                else:
                    doerData = serializer.data
                
              
                response = {
                "error": None,
                    "response": {
                        "doersData":doerData,
                        "message": {
                            'success': True,
                            "successCode": 101,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "Doers fetched successfully"
                        }
                    }
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Doers not found"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

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

class SuggestionBySearch(RetrieveAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userTypeId=1)).first()
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
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            keyword = pythonData.get('keyword', False)
            if not keyword:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "keyword field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
            subCats = SubCategory.objects.filter(Q(subCatName__icontains = keyword) & Q(catId__isApproved = True)).all()
            serializer = SubCatForSearchSerializer(data=subCats, many=True)
            serializer.is_valid()
            response = {
                "error": None,
                    "response": {
                        "suggestions":serializer.data,
                        "message": {
                            'success': True,
                            "successCode": 101,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "Suggestion fetched successfully"
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

class DoerProfileAllDetailForCustomerView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userTypeId=1)).first()
            if user is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "User not found invalid access token!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            doerId = pythonData.get('doerId', False)
            if not doerId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "doerId field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            doer = User.objects.filter(Q(id=doerId) & Q(isApproved=2) & Q(isDeleted = False) & Q(isVerified = True)).first()
            if not doer:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid doerId!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            doerData = DoerUserData.objects.filter(userId=doer).first()
            data = DoerProfileSerializer(doer)
            data2 = DoerDataSerializer(doerData)
            products = Product.objects.filter(Q(userId=doer) & Q(isDeleted = False)).all()
            data3 = ProductSerializer(data=products, many = True)
            data3.is_valid()
            gellery = Gellery.objects.filter(userId = doer).all()
            data4 = DoerGellerySerializer(data=gellery, many=True)
            data4.is_valid()
            services = DoerSelectedSubCategory.objects.filter(doerDataId = doerData).values_list('subCatId__subCatName', flat=True)
            response = {
                "error": None,
                "response": {
                    "basicDetails": data.data,
                    "services":services,
                    "identityAndCompanyData": data2.data,
                    "productsDetails": data3.data,
                    "gellery":data4.data,
                    "message": {
                        'success': True,
                        "successCode": 103,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Doer details fetched successfully."
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