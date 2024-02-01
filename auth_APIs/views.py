from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser
import io
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from auth_APIs.models import *
from auth_APIs.serializers import *
from django.contrib.auth.models import update_last_login
from django.contrib.auth.hashers import make_password
import jwt
from slaychat_doer_admin_apis.settings import SECRET_KEY
from django.db.models import Q
from itertools import chain
from Helpers.helper import s3_helper, send_notification
import stripe


class CountryCodeList(ListAPIView):
    queryset = AllCountries.objects.all().order_by('sortName')
    serializer_class = AllCountryCodeSerializer
    permission_classes = [AllowAny, ]

    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = AllCountryCodeSerializer(queryset, many=True)
        response = {
            "error": None,
            "response": {
                "data": serializer.data,
                "message": {
                    'success': True,
                    "successCode": 101,
                    "statusCode": status.HTTP_200_OK,
                    "successMessage": "All country code data."
                }
            }
        }
        return Response(response, status=status.HTTP_200_OK)


class CustomerRegistrationView(CreateAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            userTypeId = pythonData.get('userTypeId', False)
            deviceTypeId = pythonData.get('deviceTypeId', False)
            genderTypeId = pythonData.get('genderTypeId', False)
            email = pythonData.get('email', False)
            mobileNo = pythonData.get('mobileNo', False)
            password = pythonData.get('password', False)
            countryCodeId = pythonData.get('countryCodeId', False)
            authServiceProviderId = pythonData.get(
                'authServiceProviderId', False)
            cardNumber = pythonData.get('cardNumber', False)
            expMonth = pythonData.get('expMonth', False)
            expYear = pythonData.get('expYear', False)
            cvv = pythonData.get('cvv', False)
            cardHolderName = pythonData.get('cardHolderName', False)
            userCheck = User.objects.filter(
                Q(Q(email=email) | Q(mobileNo=mobileNo) | Q(authServiceProviderId=authServiceProviderId)) & Q(isDeleted=False)).first()
            if userCheck:
                response = {
                    "error": {
                        "errorCode": 500,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "User already registered"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not userTypeId:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "User type field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if not email:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Email field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not mobileNo:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "mobileNo field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if not password:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "password field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if not countryCodeId:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "countryCode field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if userTypeId != 1 and userTypeId != 2:

                response = {
                    "error": {
                        "errorCode": 506,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Invalid userType"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if deviceTypeId != 1 and deviceTypeId != 2:

                response = {
                    "error": {
                        "errorCode": 507,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Invalid deviceType"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not genderTypeId:
                response = {
                    "error": {
                        "errorCode": 508,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "genderTypeId field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if cardNumber:
                if not expMonth or not expYear or not cvv or not cardHolderName:
                    response = {
                        "error": {
                            "errorCode": 509,
                            "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "errorMessage": "card details missing please check!"
                        },
                        "response": None
                    }
                    return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            response = stripe.Customer.create(
                email=email,
                name=pythonData["fullName"],
                metadata={
                    "name": pythonData['fullName'],
                    "mobileNo": pythonData['mobileNo'],
                }
            )
            pythonData['stripeCustomerId'] = response['id']
            serializer = CustomerRegistrationSerializer(data=pythonData)
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                if cardNumber:
                    paymntMethodRespon = stripe.PaymentMethod.create(
                        type="card",
                        card={
                            "number": cardNumber,
                            "exp_month": expMonth,
                            "exp_year": expYear,
                            "cvc": cvv,
                        },
                        billing_details={
                            "name": cardHolderName
                        }
                    )

                    attactRes = stripe.PaymentMethod.attach(
                        paymntMethodRespon["id"],
                        customer=user.stripeCustomerId,
                    )
                    paymentMethodId = attactRes["id"]
                    fingerPrint = attactRes["card"]["fingerprint"]
                    stripe.Customer.modify(
                        user.stripeCustomerId,
                        invoice_settings={
                            "default_payment_method": paymentMethodId
                        }
                    )
                    card = CustomerCard.objects.create(
                        userId=user, paymentMethodId=paymentMethodId, fingerprint=fingerPrint,cardStatus=2)
                if user is not None:
                    refresh = RefreshToken.for_user(user)
                    data = {
                        "userId": user.id,
                        "fullName": user.fullName,
                        "mobileNo": user.mobileNo,
                        "email": user.email,
                        "userTypeId": user.userTypeId.id,
                        "isVerified": user.isVerified,
                        "countryCodeId": user.countryCodeId.id,
                        "stripeCustomerId": user.stripeCustomerId,
                        "gender": user.genderTypeId.name,
                        "token": str(RefreshToken.for_user(user).access_token),
                        "refreshToken": str(refresh),
                    }
                    response = {
                        "error": None,
                        "response": {
                            "userData": data,
                            "message": {
                                'success': True,
                                "successCode": 101,
                                "statusCode": status.HTTP_200_OK,
                                "successMessage": "Customer registered successfully."
                            }
                        }
                    }
                    return Response(response, status=status.HTTP_200_OK)
                else:
                    response = {
                        "error": {
                            "errorCode": 502,
                            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                            "errorMessage": "Error while registring user. Please try again later."
                        },
                        "response": None
                    }
                return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "errorMessage": "Error while registring user. Please try again later."
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as exception:
            response = {
                "error": {
                    "errorCode": 504,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(exception)
                },
                "response": None
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class LoginView(RetrieveAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            email_mobileNo = pythonData.get(
                'mobileNo', False)
            userTypeId = pythonData.get('userTypeId', False)
            deviceTypeId = pythonData.get('deviceTypeId', False)
            password = pythonData.get('password', False)
            deviceToken = pythonData.get('deviceToken', False)
            countryCodeId= pythonData.get('countryCodeId',False)

            if not userTypeId:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "User type field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not email_mobileNo:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Please enter email / mobileNo / User ID and password to login!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not password:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Please enter password to login!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if userTypeId != 1 and userTypeId != 2:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_401_UNAUTHORIZED,
                        "errorMessage": "Cross application login is prohibited!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)

            if not deviceTypeId:
                response = {
                    "error": {
                        "errorCode": 512,
                        "statusCode": status.HTTP_401_UNAUTHORIZED,
                        "errorMessage": "device Type field required"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)
            if not countryCodeId:
                response = {
                        "error": {
                            "errorCode": 513,
                            "statusCode": status.HTTP_401_UNAUTHORIZED,
                            "errorMessage": "countryCodeId required!"
                        },
                        "response": None
                    }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)
            user = User.objects.filter(
                Q(mobileNo=email_mobileNo) & Q(userTypeId=userTypeId) & Q(isDeleted=False) & Q(countryCodeId=countryCodeId)).first()
            if user is None:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "User not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if not user.check_password(request.data['password']):
                response = {
                    "error": {
                        "errorCode": 506,
                        "statusCode": status.HTTP_401_UNAUTHORIZED,
                        "errorMessage": "Please enter your correct password!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)

            if user.isDeleted == 1:
                response = {
                    "error": {
                        "errorCode": 507,
                        "statusCode": status.HTTP_401_UNAUTHORIZED,
                        "errorMessage": "Your account has been deleted. Please contact to admin for further assistance!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)

            if user.isActive == 0:
                response = {
                    "error": {
                        "errorCode": 508,
                        "statusCode": status.HTTP_401_UNAUTHORIZED,
                        "errorMessage": "Your account is rejected by admin, please contact to admin for futher assistance!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)

            if user.isApproved == 3:
                response = {
                    "error": {
                        "errorCode": 510,
                        "statusCode": status.HTTP_401_UNAUTHORIZED,
                        "errorMessage": "Your account is disapproved. Please contact to admin for futher assistance!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)
            if user.userTypeId == 2:
                if not user.isVerified:
                    response = {
                        "error": {
                            "errorCode": 511,
                            "statusCode": status.HTTP_401_UNAUTHORIZED,
                            "errorMessage": "Your registration not completed!"
                        },
                        "response": None
                    }
                    return Response(response, status=status.HTTP_401_UNAUTHORIZED)

            update_last_login(None, user)
            if deviceToken:
                User.objects.filter(id=user.id).update(
                    deviceToken=deviceToken)

            User.objects.filter(id=user.id).update(
                deviceTypeId=deviceTypeId)

            refresh = RefreshToken.for_user(user)
            data = {
                "userId": user.id,
                "fullName": user.fullName,
                "mobileNo": user.mobileNo,
                "userTypeId": user.userTypeId.id,
                "email": user.email,
                "isVerified": user.isVerified,
                "profileImage": user.profileImage,
                "token": str(refresh.access_token),
                "refreshToken": str(refresh),
            }

            response = {
                "error": None,
                "response": {
                    "userData": data,
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Logged in successfully."
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


class AccountVerification(RetrieveAPIView):

    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            email = pythonData.get('email', False)
            mobileNo = pythonData.get('mobileNo', False)
            if not email and not mobileNo:
                response = {
                    "error": {
                        "errorCode": 500,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Pass atleast one parameter"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            userCheck = User.objects.filter(
                Q(Q(email=email) & Q(isDeleted=False) | Q(mobileNo=mobileNo)) & Q(isDeleted=False)).first()
            if not userCheck:
                response = {
                    "error": {
                        "errorCode": 500,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "not registerd user"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            data = {
                "countryCode": userCheck.countryCodeId.phoneCode
            }
            response = {
                "error": None,
                "response": {
                    "userData": data,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Verified User"
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                "error": {
                    "errorCode": 616,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(e)
                },
                "response": None
            }
            return Response(response, status=status_code)


class ForgetPasswordUpdate(UpdateAPIView):

    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            mobileNo = pythonData.get(
                'mobileNo', False)
            newPassword = pythonData.get('newPassword', False)
            userTypeId = pythonData.get('userTypeId', False)
            if not mobileNo:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Mobile no field is required"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not newPassword:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "newPassword field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if not userTypeId or not userTypeId in [1,2]:
                response = {
                    "error": {
                        "errorCode": 514,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "please check userTypeId!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
     

            user = User.objects.filter(
                Q(mobileNo=mobileNo) & Q(isDeleted=False)).first()
            if user is None:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "User not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if user.userTypeId.id != userTypeId:
                response = {
                    "error": {
                        "errorCode": 515,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Invalid user!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            # if user.userType == 3:
            #     response = {
            #         "error": {
            #             "errorCode": 505,
            #             "statusCode": status.HTTP_404_NOT_FOUND,
            #             "errorMessage": "This this admin user you can't change password"
            #         },
            #         "response": None
            #     }
            #     return Response(response, status=status.HTTP_404_NOT_FOUND)
            user.password = make_password(newPassword)
            user.save()

            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Password changed successfully."
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


class DoerRegistrationView(CreateAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            deviceTypeId = pythonData.get('deviceTypeId', False)
            genderTypeId = pythonData.get('genderTypeId', False)
            email = pythonData.get('email', False)
            mobileNo = pythonData.get('mobileNo', False)
            password = pythonData.get('password', False)
            countryCodeId = pythonData.get('countryCodeId', False)
            authServiceProviderId = pythonData.get(
                'authServiceProviderId', False)
            userCheck = User.objects.filter(
                Q(Q(email=email) | Q(mobileNo=mobileNo) | Q(authServiceProviderId=authServiceProviderId)) & Q(isDeleted=False)).first()
            if userCheck:
                response = {
                    "error": {
                        "errorCode": 500,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "User already registered"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not email:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Email field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not mobileNo:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "mobileNo field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if not password:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "password field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if not countryCodeId:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "countryCode field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if deviceTypeId != 1 and deviceTypeId != 2:

                response = {
                    "error": {
                        "errorCode": 507,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Invalid deviceType"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not genderTypeId:
                response = {
                    "error": {
                        "errorCode": 508,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "genderTypeId field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            pythonData["userTypeId"] = 2
            serializer = CustomerRegistrationSerializer(data=pythonData)
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                if user is not None:
                    addtional = DoerUserData.objects.create(userId=user)
                    refresh = RefreshToken.for_user(user)
                    data = {
                        "userId": user.id,
                        "fullName": user.fullName,
                        "mobileNo": user.mobileNo,
                        "email": user.email,
                        "userTypeId": user.userTypeId.id,
                        "isVerified": user.isVerified,
                        "countryCodeId": user.countryCodeId.id,
                        "gender": user.genderTypeId.name,
                        "token": str(RefreshToken.for_user(user).access_token),
                        "refreshToken": str(refresh),
                    }
                    response = {
                        "error": None,
                        "response": {
                            "doerData": data,
                            "message": {
                                'success': True,
                                "successCode": 101,
                                "statusCode": status.HTTP_200_OK,
                                "successMessage": "Doer registered successfully."
                            }
                        }
                    }
                    return Response(response, status=status.HTTP_200_OK)
                else:
                    response = {
                        "error": {
                            "errorCode": 502,
                            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                            "errorMessage": "Error while registring user. Please try again later."
                        },
                        "response": None
                    }
                return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "errorMessage": "Error while registring user. Please try again later."
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as exception:
            response = {
                "error": {
                    "errorCode": 504,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(exception)
                },
                "response": None
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            refreshToken = pythonData.get('refresh', False)
            if not refreshToken:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Token is required to logout!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            user = jwt.decode(refreshToken, key=SECRET_KEY,
                              algorithms=['HS256', ])
            userr = User.objects.filter(
                Q(id=user['user_id'])).first()
            if userr is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "User not found invalid access token!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            RefreshToken(refreshToken).blacklist()
            userr.deviceToken = None
            userr.save()
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Logout successfully."
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


class BasicUpdateProfile(UpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(id=userr['user_id']).first()
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            email = pythonData.get('email', False)
            mobileNo = pythonData.get('mobileNo', False)
            genderTypeId = pythonData.get('genderTypeId', False)
            countryCodeId = pythonData.get('countryCodeId', False)
            if user is None:
                response = {
                    "error": {
                        "errorCode": 500,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "User not found with this user id."
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_200_OK)
            if mobileNo:
                if mobileNo != user.mobileNo:
                    if User.objects.filter(Q(Q(mobileNo=mobileNo)) & Q(isDeleted=False)).exists():
                        response = {
                            "error": {
                                "errorCode": 504,
                                "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                                "errorMessage": "mobileNo already exists."
                            },
                            "response": None
                        }
                        return Response(response, status=status.HTTP_200_OK)
            if email:
                if email != user.email:
                    if User.objects.filter(Q(email=email) & Q(isDeleted=False)).exists():
                        response = {
                            "error": {
                                "errorCode": 501,
                                "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                                "errorMessage": "this email already exists."
                            },
                            "response": None
                        }
                        return Response(response, status=status.HTTP_200_OK)
            if genderTypeId:
                if genderTypeId != 1 and genderTypeId != 2 and genderTypeId != 3:

                    response = {
                        "error": {
                            "errorCode": 502,
                            "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "errorMessage": "Invalid genderTypeId"
                        },
                        "response": None
                    }
                    return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if countryCodeId:
                if contryInst := AllCountries.objects.filter(
                    id=countryCodeId
                ).first():
                    pythonData["countryCodeId"] = contryInst.id
                else:
                    response = {
                        "error": {
                            "errorCode": 503,
                            "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "errorMessage": "Invalid countryCodeId"
                        },
                        "response": None
                    }
                    return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            serializer = UserNewProfileSerializer(
                user, data=pythonData, partial=True
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                response = {
                    "error": None,
                    "response": {
                        "message": {
                            'success': True,
                            "successCode": 103,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "User profile updated successfully."
                        }
                    }
                }
                return Response(response, status=status.HTTP_200_OK)
        except Exception as exception:
            response = {
                "error": {
                    "errorCode": 514,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(exception)
                },
                "response": None
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class ProfileDetailView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(id=user['user_id']).first()
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
            if user.userTypeId.id == 1:
                data = CustomerProfileSerializer(user)
                response = {
                    "error": None,
                    "response": {
                        "cutomerDetails": data.data,
                        "message": {
                            'success': True,
                            "successCode": 103,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "Customer details fetched successfully."
                        }
                    }
                }
            else:
                data = UserProfileSerializer(user)
                response = {
                    "error": None,
                    "response": {
                        "doerDetails": data.data,
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


class CustomerServiceProviderRegisterLogin(CreateAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            authServiceProviderId = pythonData.get(
                'authServiceProviderId', False)
            authServiceProviderType = pythonData.get(
                'authServiceProviderType', False)
            email = pythonData.get('email', False)
            fullName = pythonData.get('fullName', False)
            mobileNo = pythonData.get('mobileNo', False)
            deviceTypeId = pythonData.get('deviceTypeId', False)
            genderTypeId = pythonData.get('genderTypeId', False)
            countryCodeId = pythonData.get('countryCodeId', False)
            userTypeId = pythonData.get('userTypeId', False)
            city = pythonData.get('city', False)
            deviceToken = pythonData.get('deviceToken', False)

            if not authServiceProviderType:
                response = {
                    "error": {
                        "errorCode": 500,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Auth Service Provider Type is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not authServiceProviderId:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Auth Service Provider Id is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not deviceTypeId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Device Type is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not userTypeId:
                response = {
                    "error": {
                        "errorCode": 509,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "userTypeId is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            user = User.objects.filter(
                Q(authServiceProviderId=authServiceProviderId) & Q(isDeleted=False)).first()

            if user is None:
                if not mobileNo:
                    response = {
                        "error": {
                            "errorCode": 503,
                            "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "errorMessage": "mobileNo is required!"
                        },
                        "response": None
                    }
                    return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                if not fullName:
                    response = {
                        "error": {
                            "errorCode": 504,
                            "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "errorMessage": "fullName is required!"
                        },
                        "response": None
                    }
                    return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                if not email:
                    response = {
                        "error": {
                            "errorCode": 505,
                            "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "errorMessage": "email is required!"
                        },
                        "response": None
                    }
                    return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

                if not countryCodeId:
                    response = {
                        "error": {
                            "errorCode": 509,
                            "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "errorMessage": "countryCodeId is required!"
                        },
                        "response": None
                    }
                    return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

                userCheck = User.objects.filter(
                    Q(email=email) | Q(mobileNo=mobileNo) | Q(authServiceProviderId=authServiceProviderId)).first()
                if userCheck:
                    response = {
                        "error": {
                            "errorCode": 508,
                            "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "errorMessage": "User already registered"
                        },
                        "response": None
                    }
                    return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                if userTypeId == 2:
                    # if not city:
                    #     response = {
                    #         "error": {
                    #             "errorCode": 510,
                    #             "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                    #             "errorMessage": "city field required"
                    #         },
                    #         "response": None
                    #     }
                    #     return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                    if city:
                        pythonData['city'] = city

                pythonData['password'] = "Social@123"
                pythonData['userTypeId'] = userTypeId

                if user is None:
                    serializer = CustomerRegistrationSerializer(
                        data=pythonData)
                    if serializer.is_valid(raise_exception=True):
                        user = serializer.save()
                        if user.userTypeId.id == 2:
                            DoerUserData.objects.create(userId=user)
                        data = {
                            "userId": user.id,
                            "fullName": user.fullName,
                            "mobileNo": user.mobileNo,
                            "email": user.email,
                            "userTypeId": user.userTypeId.id,
                            "isVerified": user.isVerified,
                            "token": str(RefreshToken.for_user(user).access_token),
                            "refreshToken": str(RefreshToken.for_user(user)),
                        }
                        if user.userTypeId.id == 1:
                            var = "customerData"
                        else:
                            var = "doerData"
                        response = {
                            "error": None,
                            "response": {
                                var: data,
                                "message": {
                                    'success': True,
                                    "successCode": 103,
                                    "statusCode": status.HTTP_200_OK,
                                    "successMessage": "signUp successfully."
                                }
                            }
                        }
                        return Response(response, status=status.HTTP_200_OK)

            if user.isDeleted == 1:
                response = {
                    "error": {
                        "errorCode": 507,
                        "statusCode": status.HTTP_401_UNAUTHORIZED,
                        "errorMessage": "Your account has been deleted. Please contact to admin for further assistance!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)
            # if user.isActive == 0:
            #     response = {
            #         "error": {
            #             "errorCode": 519,
            #             "statusCode": status.HTTP_401_UNAUTHORIZED,
            #             "errorMessage": "Your account has been deactivated. Please contact admin for further assistance!"
            #         },
            #         "response": None
            #     }

            #     return Response(response, status=status.HTTP_401_UNAUTHORIZED)
            if user.userTypeId == 2:
                if not user.isVerified:
                    response = {
                        "error": {
                            "errorCode": 511,
                            "statusCode": status.HTTP_401_UNAUTHORIZED,
                            "errorMessage": "Your registration not completed!"
                        },
                        "response": None
                    }
                    return Response(response, status=status.HTTP_401_UNAUTHORIZED)
            update_last_login(None, user)
            User.objects.filter(
                Q(authServiceProviderId=authServiceProviderId) & Q(isDeleted=False)).update(deviceTypeId=deviceTypeId)
            if deviceToken:
                User.objects.filter(
                    Q(authServiceProviderId=authServiceProviderId) & Q(isDeleted=False)).update(deviceToken=deviceToken)
            data = {
                "userId": user.id,
                "fullName": user.fullName,
                "mobileNo": user.mobileNo,
                "email": user.email,
                "userTypeId": user.userTypeId.id,
                "isVerified": user.isVerified,
                "profileImage": user.profileImage,
                "token": str(RefreshToken.for_user(user).access_token),
                "refreshToken": str(RefreshToken.for_user(user)),
            }
            if user.userTypeId.id == 1:
                var = "customerData"
            else:
                var = "doerData"
            response = {
                "error": None,
                "response": {
                    var: data,
                    "message": {
                        'success': True,
                        "successCode": 104,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Logged in successfylly."
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as exception:
            response = {
                "error": {
                    "errorCode": 520,
                    "statusCode": status.HTTP_200_OK,
                    "errorMessage": str(exception)
                },
                "response": None
            }
            return Response(response, status=status.HTTP_200_OK)


class ChangePasswordView(UpdateAPIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id'])).first()
            if user is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "User not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            oldPassword = pythonData.get(
                'oldPassword', False)
            newPassword = pythonData.get('newPassword', False)
            if not oldPassword:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "oldPassword field is required"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not newPassword:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "New password field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if not user.check_password(oldPassword):
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_401_UNAUTHORIZED,
                        "errorMessage": "Please enter your correct old password!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)

            user.password = make_password(newPassword)
            user.save()

            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Password changed successfully."
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


class PasswordVerification(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(id=user['user_id']).first()
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            password = pythonData.get('password', False)

            if user is None:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "User not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if not password:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Please enter your password!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not user.check_password(password):
                response = {
                    "error": {
                        "errorCode": 506,
                        "statusCode": status.HTTP_401_UNAUTHORIZED,
                        "errorMessage": "Wrong Password! Unauthorized User"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)

            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Valid password"
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                "error": {
                    "errorCode": 616,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(e)
                },
                "response": None
            }
            return Response(response, status=status_code)


class DoerNavStatusView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userTypeId=2)).first()
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

            doerData = DoerUserData.objects.filter(userId=user).first()
            if not doerData:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Please register new doer user first!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            data = {
                "personalInformation": True if user.city else False,
                "workServices": True if DoerSelectedSubCategory.objects.filter(doerDataId=doerData).exists() else False,
                "identification": True if doerData.idImageUrl else False,
                "billingInfo": True,
                "compInfo": True if doerData.companyId else False,
                "about": True if doerData.about else False
            }

            response = {
                "error": None,
                "response": {
                    "navStatus": data,
                    "message": {
                        'success': True,
                        "successCode": 103,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Doer nav statuses successfully."
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


class SubCatListView(ListAPIView):
    permission_classes = [IsAuthenticated, ]

    def list(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userTypeId=2)).first()
            if user is None:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "User not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if request.query_params.get('search'):
                queryone = SubCategory.objects.filter(
                    Q(catId__catAddedBy=1) & Q(catId__isApproved=True) & Q(subCatName__icontains=request.query_params.get('search'))).order_by('-id')
                queryTwo = SubCategory.objects.filter(Q(catId__catAddedBy=2) & Q(
                    catId__userId=user) & Q(catId__isApproved=True) & Q(subCatName__icontains=request.query_params.get('search'))).order_by('-id')
                queryset = sorted(chain(
                    queryone, queryTwo), key=lambda data: data.id, reverse=True)
            else:
                queryone = SubCategory.objects.filter(
                    Q(catId__catAddedBy=1) & Q(catId__isApproved=True)).order_by('-id')
                queryTwo = SubCategory.objects.filter(Q(catId__catAddedBy=2) & Q(
                    catId__userId=user) & Q(catId__isApproved=True)).order_by('-id')
                queryset = sorted(chain(
                    queryone, queryTwo), key=lambda data: data.id, reverse=True)
            serializer = SubCatSerializer(queryset, many=True)
            response = {
                "error": None,
                "response": {
                    "serviceData": serializer.data,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "sub cat list fetched according to the user and admin added"
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


class AddCustomCategoryView(CreateAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userTypeId=2)).first()
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
            categoryName = pythonData.get('categoryName', False)
            subCategoryNames = pythonData.get('subCategoryNames', False)
            if not categoryName:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "categoryName field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
            if Category.objects.filter(catName__contains=categoryName).exists():
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "category already exists!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)

            if not subCategoryNames:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "subCategoryNames field and atleast one subCategoryName is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)

            cat_inst = Category.objects.create(
                catName=categoryName, catAddedBy=2, userId=user)
            for subCat in subCategoryNames:
                SubCategory.objects.create(catId=cat_inst, subCatName=subCat)

            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "category and sub category added successfully"
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


class SelectSubCategoriesViews(UpdateAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userTypeId=2)).first()
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
            subCategoryIds = pythonData.get('subCategoryIds', False)

            if SubCategory.objects.filter(Q(catId__userId=user) & Q(catId__isApproved=False)).exists():
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "dear doer your custom category pending for approval by admin!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)

            if not subCategoryIds:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "subCategoryIds field and atleast one subCategoryIds is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
            if DoerSelectedSubCategory.objects.filter(Q(subCatId__in=subCategoryIds) & Q(doerDataId__userId=user)).exists():
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "subcategories already exists"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
            doerDataInst = DoerUserData.objects.filter(userId=user).first()
            for subCat in subCategoryIds:
                subCateIn = SubCategory.objects.filter(id=subCat).first()
                DoerSelectedSubCategory.objects.create(
                    doerDataId=doerDataInst, subCatId=subCateIn)
            doerDataInst.userNavStatus = 2
            doerDataInst.save()
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "sub category selected successfully"
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


class AddIdentityView(UpdateAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userTypeId=2)).first()
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
            identityUrl = pythonData.get('identityUrl', False)
            if not identityUrl:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "identityUrl field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
            doerDataInst = DoerUserData.objects.filter(userId=user).first()
            doerDataInst.idImageUrl = identityUrl
            doerDataInst.userNavStatus = 4
            doerDataInst.save()
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "identity url added successfully"
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


class AddAboutView(UpdateAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userTypeId=2)).first()
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
            about = pythonData.get('about', False)
            if not about:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "about field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
            doerDataInst = DoerUserData.objects.filter(userId=user).first()
            doerDataInst.about = about
            doerDataInst.userNavStatus = 6
            doerDataInst.save()
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "about added successfully"
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


class CompanyList(ListAPIView):
    queryset = Company.objects.filter(
        Q(companyType=2) & Q(isApproved=True)).order_by('-id')
    permission_classes = [AllowAny, ]

    def post(self, request):
        pythonData = JSONParser().parse(io.BytesIO(request.body))
        search = pythonData.get('search', False).strip()
        if search:
            queryset = Company.objects.filter(Q(companyType=2) & Q(
                companyName__icontains=search) & Q(isApproved=True)).order_by('-id')
            serializer = CompanySerializer(queryset, many=True)
            response = {
                "error": None,
                "response": {
                    "companyData": serializer.data,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Company list fetched successfully"
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        queryset = self.get_queryset()
        serializer = CompanySerializer(queryset, many=True)
        response = {
            "error": None,
            "response": {
                "companyData": serializer.data,
                "message": {
                    'success': True,
                    "successCode": 101,
                    "statusCode": status.HTTP_200_OK,
                    "successMessage": "Company list fetched successfully"
                }
            }
        }
        return Response(response, status=status.HTTP_200_OK)


class AddCompanyView(UpdateAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userTypeId=2)).first()
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
            companyId = pythonData.get('companyId', False)
            if not companyId:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "companyId field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
            if Company.objects.filter(Q(userId=user) & Q(isApproved=False)).exists():
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "your added company still not approved!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
            company = Company.objects.filter(id=companyId).first()
            if not company:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "Invalid companyId!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
            doerDataInst = DoerUserData.objects.filter(userId=user).first()
            doerDataInst.companyId = company
            doerDataInst.userNavStatus = 5
            doerDataInst.save()
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Company added successfully"
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


class AddOtherCompanyView(UpdateAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userTypeId=2)).first()
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
            companyName = pythonData.get('companyName', False)
            companyAddress = pythonData.get('companyAddress', False)
            if not companyName:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "companyName field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
            if not companyAddress:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "companyAddress field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
            company = Company.objects.filter(
                companyName__contains=companyName).first()
            if company:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "company already exists!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
            comp = Company.objects.create(
                companyName=companyName, companyType=2, userId=user, address=companyAddress)
            # doerDataInst = DoerUserData.objects.filter(userId=user).first()
            # doerDataInst.companyId = comp
            # doerDataInst.userNavStatus = 5
            # doerDataInst.save()
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Company added successfully"
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


class CompleteDoerProfile(UpdateAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userTypeId=2)).first()
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
            doerData = DoerUserData.objects.filter(userId=user).first()
            if user.city and DoerSelectedSubCategory.objects.filter(doerDataId=doerData).exists() and doerData.idImageUrl and doerData.companyId and doerData.about:
                user.isVerified = True
                user.save()
                response = {
                    "error": None,
                    "response": {
                        "isVerified": True,
                        "message": {
                            'success': True,
                            "successCode": 101,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "Profile Completed Successfully"
                        }
                    }
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "Registration Incomplete!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)

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


class DoerProfileAllDetailView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userTypeId=2)).first()
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
            if not user.isVerified:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Please complete your profile first!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            doerData = DoerUserData.objects.filter(userId=user).first()
            selectedServices = DoerSelectedSubCategory.objects.filter(
                doerDataId=doerData).all()
            data = DoerProfileSerializer(user)
            data2 = DoerDataSerializer(doerData)
            data3 = DoerSelectedSubcategory(data=selectedServices, many=True)
            data3.is_valid()
            response = {
                "error": None,
                "response": {
                    "basicDetails": data.data,
                    "identityAndCompanyData": data2.data,
                    "selectedServicess": data3.data,
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


class ServicesUpdateView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userTypeId=2)).first()
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
            subCategoryIds = pythonData.get('subCategoryIds', False)
            if not subCategoryIds:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "subCategoryIds field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not user.isVerified:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_401_UNAUTHORIZED,
                        "errorMessage": "Your registration not completed!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)

            doerData = DoerUserData.objects.filter(userId=user).first()
            selected = DoerSelectedSubCategory.objects.filter(
                doerDataId=doerData).all()
            for subCat in selected:
                subCat.delete()
            for subcat in subCategoryIds:
                subCatIns = SubCategory.objects.filter(id=subcat).first()
                DoerSelectedSubCategory.objects.create(
                    doerDataId=doerData, subCatId=subCatIns)
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 103,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Doer servicess update successfully."
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


class IdentityUpdateView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userTypeId=2)).first()
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
            identityUrl = pythonData.get('identityUrl', False)
            if not identityUrl:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "identityUrl field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not user.isVerified:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_401_UNAUTHORIZED,
                        "errorMessage": "Your registration not completed!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)
            DoerUserData.objects.filter(
                userId=user).update(idImageUrl=identityUrl)
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 103,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Doer identity update successfully."
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


class GelleryListAddLdelete(ListAPIView):
    permission_classes = [IsAuthenticated, ]

    def list(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY,
                               algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userTypeId=2)).first()
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
            query = Gellery.objects.filter(userId=user).all().order_by('-id')
            serializer = DoerGellerySerializer(query, many=True)
            response = {
                "error": None,
                "response": {
                    "data": serializer.data,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Gellery Images Fetched Successfully!"
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

    def post(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userTypeId=2)).first()
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
            imageUrls = pythonData.get('imageUrls', False)
            if not imageUrls:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "imageUrl field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            for image in imageUrls:
                if not Gellery.objects.filter(Q(imageUrl__exact=image) & Q(userId=user)).exists():
                    Gellery.objects.create(imageUrl=image, userId=user)
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Gellery Images Added Successfully!"
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

    def delete(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userTypeId=2)).first()
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
            imageIds = pythonData.get('imageIds', False)
            if not imageIds:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "imageId field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            for imageId in imageIds:
                if Gellery.objects.filter(Q(userId=user) & Q(id=imageId)).exists():
                    # delete_file_from_bucket(Gellery.objects.filter(
                    #     Q(userId=user) & Q(id=imageId)).first().imageUrl)
                    Gellery.objects.filter(
                        Q(userId=user) & Q(id=imageId)).delete()
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Gellery Images deleted Successfully!"
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


class ProductListAddLdelete(ListAPIView):
    permission_classes = [IsAuthenticated, ]

    def list(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY,
                               algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userTypeId=2)).first()
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
            query = Product.objects.filter(Q(userId=user) & Q(
                isDeleted=False)).all().order_by('-id')
            serializer = DoerProductSerializer(query, many=True)
            response = {
                "error": None,
                "response": {
                    "productData": serializer.data,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Products Fetched Successfully!"
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

    def post(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userTypeId=2)).first()
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
            productName = pythonData.get('productName', False)
            productPrice = pythonData.get('productPrice', False)
            productDescription = pythonData.get('productDescription', False)
            productImageUrl = pythonData.get('productImageUrl', False)

            if not productName:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "productName field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not productPrice:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "productPrice field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not productDescription:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "productDescription field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not productImageUrl:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "productImageUrl field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if Product.objects.filter(Q(userId=user) & Q(isDeleted=False) & Q(productName__icontains=productName)).exists():
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_208_ALREADY_REPORTED,
                        "errorMessage": "product already exists!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_208_ALREADY_REPORTED)
            pythonData["userId"] = user.id
            serializer = DoerProductSerializer(data=pythonData)
            if serializer.is_valid(raise_exception=True):
                product = serializer.save()
                response = {
                    "error": None,
                    "response": {
                        "message": {
                            'success': True,
                            "successCode": 101,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "Products Added Successfully!"
                        }
                    }
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "error": {
                        "errorCode": 506,
                        "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "errorMessage": "Error while add product. Please try again later."
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

    def put(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userTypeId=2)).first()
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
            productId = pythonData.get('productId', False)
            if not productId:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "productId field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if not Product.objects.filter(Q(userId=user) & Q(isDeleted=False) & Q(id=productId)).exists():
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_208_ALREADY_REPORTED,
                        "errorMessage": "Invalid productId!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_208_ALREADY_REPORTED)
            product = Product.objects.filter(Q(userId=user) & Q(
                isDeleted=False) & Q(id=productId)).first()
            serializer = DoerProductSerializer(
                product, data=pythonData, partial=True)
            if serializer.is_valid(raise_exception=True):
                product = serializer.save()
                response = {
                    "error": None,
                    "response": {
                        "message": {
                            'success': True,
                            "successCode": 101,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "Product Updated Successfully!"
                        }
                    }
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "error": {
                        "errorCode": 506,
                        "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "errorMessage": "Error while update product. Please try again later."
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

    def delete(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userTypeId=2)).first()
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
            productId = pythonData.get('productId', False)
            if not productId:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "productId field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if Product.objects.filter(Q(id=productId) & Q(userId=user) & Q(isDeleted=False)).exists():
                product = Product.objects.filter(Q(id=productId) & Q(
                    userId=user) & Q(isDeleted=False)).update(isDeleted=True)
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Product deleted Successfully!"
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


class OfferListAddEditdelete(ListAPIView):
    permission_classes = [IsAuthenticated, ]

    def list(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY,
                               algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userTypeId=2)).first()
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
            query = Offer.objects.filter(Q(userId=user) & Q(
                isDeleted=False)).all().order_by('-id')
            serializer = DoerOfferListSerializer(query, many=True)

            response = {
                "error": None,
                "response": {
                    "offerData": serializer.data,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Offers Fetched Successfully!"
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

    def post(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userTypeId=2)).first()
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
            productIds = pythonData.get('productIds', False)
            offerPercentage = pythonData.get('offerPercentage', False)
            offerDescription = pythonData.get('offerDescription', False)

            if not offerPercentage:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "offerPercentage field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not offerDescription:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "offerDescription field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not productIds:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "productIds field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if Offer.objects.filter(Q(userId=user) & Q(isDeleted=False) & Q(offerPercentage=offerPercentage)).exists():
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_208_ALREADY_REPORTED,
                        "errorMessage": "offer already exists!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_208_ALREADY_REPORTED)
            pythonData["userId"] = user.id
            serializer = DoerOfferSerializer(data=pythonData)
            if serializer.is_valid(raise_exception=True):
                offer = serializer.save()
                for product in productIds:
                    if Product.objects.filter(Q(userId=user) & Q(isDeleted=False) & Q(id=product)).exists():
                        OfferProducts.objects.create(
                            offerId=offer, productId=Product.objects.filter(Q(userId=user) & Q(isDeleted=False) & Q(id=product)).first())
                response = {
                    "error": None,
                    "response": {
                        "message": {
                            'success': True,
                            "successCode": 101,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "Offer Added Successfully!"
                        }
                    }
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "error": {
                        "errorCode": 506,
                        "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "errorMessage": "Error while add offer. Please try again later."
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

    def put(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userTypeId=2)).first()
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
            productIds = pythonData.get('productIds', False)
            offerId = pythonData.get('offerId', False)
            offerPercentage = pythonData.get('offerPercentage', False)

            if not offerId:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "offerId field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            offerIns = Offer.objects.filter(Q(userId=user) & Q(
                isDeleted=False) & Q(id=offerId)).first()
            if not offerIns:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid offerId!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if offerPercentage and offerIns.offerPercentage != offerPercentage:
                if Offer.objects.filter(Q(userId=user) & Q(isDeleted=False) & Q(offerPercentage=offerPercentage)).exists():
                    response = {
                        "error": {
                            "errorCode": 505,
                            "statusCode": status.HTTP_208_ALREADY_REPORTED,
                            "errorMessage": "offer already exists!"
                        },
                        "response": None
                    }
                    return Response(response, status=status.HTTP_208_ALREADY_REPORTED)
            pythonData["userId"] = user.id
            pythonData["offerPercentage"] = offerPercentage
            serializer = DoerOfferSerializer(
                offerIns, data=pythonData, partial=True)
            if serializer.is_valid(raise_exception=True):
                offer = serializer.save()
                if productIds:
                    OfferProducts.objects.filter(
                        offerId=offerIns).all().delete()
                    for product in productIds:
                        if Product.objects.filter(Q(userId=user) & Q(isDeleted=False) & Q(id=product)).exists():
                            OfferProducts.objects.create(
                                offerId=offer, productId=Product.objects.filter(Q(userId=user) & Q(isDeleted=False) & Q(id=product)).first())
                response = {
                    "error": None,
                    "response": {
                        "message": {
                            'success': True,
                            "successCode": 101,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "Offer updated Successfully!"
                        }
                    }
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "error": {
                        "errorCode": 506,
                        "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "errorMessage": "Error while update offer. Please try again later."
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

    def delete(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userTypeId=2)).first()
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
            offerId = pythonData.get('offerId', False)
            if not offerId:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "offerId field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if Offer.objects.filter(Q(id=offerId) & Q(userId=user) & Q(isDeleted=False)).exists():
                offer = Offer.objects.filter(Q(id=offerId) & Q(
                    userId=user) & Q(isDeleted=False)).update(isDeleted=True)
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Offer deleted Successfully!"
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

# Customer

class CategoryList(ListAPIView):
    permission_classes = [AllowAny, ]

    def list(self, request):
        try:
            query = SubCategory.objects.all().order_by('?')[:8]
            serializer = SubCatForChangesSerializer(query, many=True)
            response = {
                "error": None,
                "response": {
                    "categoryData": serializer.data,
                    "sumitKiDemand":serializer.data,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "category Fetched Successfully!"
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


class OfferListByProductId(ListAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY,
                               algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userTypeId=2)).first()
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
            productId = pythonData.get('productId', False)
            if not productId:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "productId field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if not Product.objects.filter(Q(userId=user) & Q(isDeleted=False) & Q(id=productId)).exists():
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_208_ALREADY_REPORTED,
                        "errorMessage": "Invalid productId!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_208_ALREADY_REPORTED)
            product = Product.objects.filter(Q(userId=user) & Q(
                isDeleted=False) & Q(id=productId)).first()
            query = OfferProducts.objects.filter(
                Q(productId=product)).all().order_by('-id')
            serializer = OfferByProductIdSerializer(query, many=True)
            response = {
                "error": None,
                "response": {
                    "offerDetails": serializer.data,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Offers Fetched Successfully!"
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


class DeviceTokenUpdate(UpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY,
                               algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id'])).first()
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
            deviceToken = pythonData.get('deviceToken', False)
            if not deviceToken:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "deviceToken field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            user.deviceToken = deviceToken
            user.save()
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Token Updated Successfully Successfully!"
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


class LatLongUpdate(UpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY,
                               algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id'])).first()
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
            latitude = pythonData.get('latitude', False)
            longitude = pythonData.get('longitude', False)
            if not latitude or not longitude:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "latitude, longitude required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            user.lat=latitude
            user.lng=longitude
            user.save()
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "lat long updated Successfully!"
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
        


class TopSearches(UpdateAPIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            if request.query_params:
                searchVal = request.query_params.get('search').strip()
                catIds = SubCategory.objects.filter(Q(subCatName__icontains=searchVal) | Q(catId__catName__icontains=searchVal)).values_list('catId__id', flat=True)
                catefories = Category.objects.filter(Q(isApproved=True) & Q(catName__icontains=searchVal) | Q(id__in=catIds)).order_by('catAddedBy')
                response = {
                    "error": None,
                    "response": {
                        "topSearchesData":CatForTopSearchesSerializer(catefories, many=True).data,
                        "message": {
                            'success': True,
                            "successCode": 101,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "top searches result!"
                        }
                    }
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                catefories = Category.objects.filter(Q(isApproved=True)).order_by('catAddedBy')
                response = {
                    "error": None,
                    "response": {
                        "topSearchesData":CatForTopSearchesSerializer(catefories, many=True).data,
                        "message": {
                            'success': True,
                            "successCode": 101,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "top searches result!"
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
        
class SendNotificationForAnyUser(UpdateAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            userId = pythonData.get('userId', False)
            title = pythonData.get('title', False)
            message = pythonData.get('message', False)
            data=pythonData.get('additionalData', False)
            if not userId or not title or not message or not data:
                response = {
                    "error": {
                        "errorCode": 500,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "required parameters missing[userId,title,message and additionalData]!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            user = User.objects.filter(
                Q(id=userId)).first()
            if user is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "User not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            tokens = [user.deviceToken]
            res = send_notification(title, message,tokens,data)
            response = {
                "error": None,
                "response": {
                    "firbase_response":res,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Hit notification API successfully!"
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


class Testing(UpdateAPIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            # res=stripe.Account.create(
            # type="custom",
            # country="AE",
            # email="nothing@yopmail.com",
            # default_currency="aed"
            # )
            res=stripe.Account.create(
            type="custom",
            country="AE",
            email="nothing@yopmail.com",
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
            )
            # res=stripe.AccountLink.create(
            # account="acct_1N5j3YR4xbPacV67",
            # refresh_url="https://example.com/reauth",
            # return_url="https://example.com/return",
            # type="account_onboarding",
            # )
            # res = stripe.Account.create_external_account(
            #     'acct_1N5j3YR4xbPacV67', 
            #     external_account={
            #         'object': 'bank_account',
            #         'country': 'AE',
            #         'currency': 'aed',
            #         'routing_number': '033',
            #         'account_number': '000123456789012345678901',
            #         'account_holder_name': 'Jane Doe'
            #     }
            # )
           
            # res=stripe.Transfer.create(
            #     amount=round(50 * 100),
            #     currency="aed",
            #     destination="acct_1N5j3YR4xbPacV67",
            #     transfer_group=f"order23",
            #     source_transaction="ch_3N5jN1JrhHazCO5H0KsNdlq7"
            # )
            print(res)
            response = {
                "error": None,
                "response": {
                    "res":res,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "updated Successfully!"
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



class DeleteMyAccount(UpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY,
                               algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(isDeleted=False)).first()
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
            user.isDeleted=True
            user.save()
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Account deleted successfully!"
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