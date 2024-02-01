from rest_framework.generics import RetrieveAPIView, CreateAPIView, DestroyAPIView
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
from chatPanel.models import *
from .serializers import *
from Helpers.helper import *
import stripe
from paymentAPIs.serializers import *
from django.utils import timezone
import datetime
from django.db.models import Avg
from support.models import *
from django.db import transaction

class ChatPanelNavStatusView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userTypeId__in=[1, 2])).first()
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
            jobId = pythonData.get('jobId', False)
            chatId = pythonData.get('chatId', False)
            doerId = pythonData.get('doerId', False)
            if not doerId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "doerId is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            doer = User.objects.filter(
                Q(id=doerId) & Q(isVerified=True)).first()
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
            selectedSubCategories = DoerSelectedSubCategory.objects.filter(
                doerDataId__userId=doer).values_list('subCatId__subCatName', flat=True)
            if jobId and chatId:
                job = Job.objects.filter(Q(id=jobId) & Q(Q(
                    userId=user) | Q(doerId=user)) & Q(chatId=chatId) & Q(jobStatus__in=[1, 2, 3, 4])).first()
                if user.userTypeId.id == 2:
                    tem = JobProposal.objects.filter(
                        Q(jobId=job) & Q(doerId=user) & Q(status=1)).first()
                    if tem:
                        proposal = tem.id
                    else:
                        proposal = None
                else:
                    proposal = None
                if job:
                    if job.jobPanelStatus == 1:
                        response = {
                            "error": None,
                            "response": {
                                "panelStatus": 1,
                                "proposalId": proposal,
                                "message": {
                                    'success': True,
                                    "successCode": 103,
                                    "statusCode": status.HTTP_200_OK,
                                    "successMessage": "Panel status fetched successfully"
                                }
                            }
                        }
                        return Response(response, status=status.HTTP_200_OK)
                    elif job.jobPanelStatus == 2:
                        response = {
                            "error": None,
                            "response": {
                                "panelStatus": 2,
                                "proposalId": proposal,
                                "message": {
                                    'success': True,
                                    "successCode": 103,
                                    "statusCode": status.HTTP_200_OK,
                                    "successMessage": "Panel status fetched successfully"
                                }
                            }
                        }
                        return Response(response, status=status.HTTP_200_OK)
                    elif job.jobPanelStatus == 3:
                        response = {
                            "error": None,
                            "response": {
                                "panelStatus": 3,
                                "proposalId": proposal,
                                "message": {
                                    'success': True,
                                    "successCode": 103,
                                    "statusCode": status.HTTP_200_OK,
                                    "successMessage": "Panel status fetched successfully"
                                }
                            }
                        }
                        return Response(response, status=status.HTTP_200_OK)
                    elif job.jobPanelStatus == 4:
                        response = {
                            "error": None,
                            "response": {
                                "panelStatus": 4,
                                "proposalId": proposal,
                                "message": {
                                    'success': True,
                                    "successCode": 103,
                                    "statusCode": status.HTTP_200_OK,
                                    "successMessage": "Panel status fetched successfully"
                                }
                            }
                        }
                        return Response(response, status=status.HTTP_200_OK)
                    elif job.jobPanelStatus == 5:
                        response = {
                            "error": None,
                            "response": {
                                "panelStatus": 5,
                                "proposalId": proposal,
                                "message": {
                                    'success': True,
                                    "successCode": 103,
                                    "statusCode": status.HTTP_200_OK,
                                    "successMessage": "Panel status fetched successfully"
                                }
                            }
                        }
                        return Response(response, status=status.HTTP_200_OK)

                    elif job.jobPanelStatus == 6:
                        response = {
                            "error": None,
                            "response": {
                                "panelStatus": 6,
                                "proposalId": proposal,
                                "message": {
                                    'success': True,
                                    "successCode": 103,
                                    "statusCode": status.HTTP_200_OK,
                                    "successMessage": "Panel status fetched successfully"
                                }
                            }
                        }
                        return Response(response, status=status.HTTP_200_OK)
                    else:
                        lastRating = JobRatingReview.objects.filter(Q(
                            jobId__userId=user) & Q(doerId=doer)).last()

                        response = {
                            "error": None,
                            "response": {
                                "panelStatus": 0,
                                "lastJobRating":  JobRatingReviewSerializer2(lastRating).data if lastRating else None,
                                "services": selectedSubCategories if DoerSelectedSubCategory.objects.filter(doerDataId__userId=doer).exists() else [],
                                "jobRated":bool(JobRatingReview.objects.filter(Q(jobId=job) & Q(userId__isnull=False)).first()),
                                "message": {
                                    'success': True,
                                    "successCode": 103,
                                    "statusCode": status.HTTP_200_OK,
                                    "successMessage": "Panel status fetched successfully"
                                }
                            }
                        }
                        return Response(response, status=status.HTTP_200_OK)
                else:
                    lastRating = JobRatingReview.objects.filter(Q(
                        jobId__userId=user) & Q(doerId=doer)).last()
                    response = {
                        "error": None,
                        "response": {
                            "panelStatus": 0,
                            "lastJobRating":  JobRatingReviewSerializer2(lastRating).data if lastRating else None,
                            "services": selectedSubCategories if DoerSelectedSubCategory.objects.filter(doerDataId__userId=doer).exists() else [],
                            "message": {
                                'success': True,
                                "successCode": 103,
                                "statusCode": status.HTTP_200_OK,
                                "successMessage": "Panel status fetched successfully"
                            }
                        }
                    }
                    return Response(response, status=status.HTTP_200_OK)
            else:
                lastRating = JobRatingReview.objects.filter(Q(
                    jobId__userId=user) & Q(doerId=doer)).last()
                response = {
                    "error": None,
                    "response": {
                        "panelStatus": 0,
                        "lastJobRating":  JobRatingReviewSerializer2(lastRating).data if lastRating else None,
                        "services": selectedSubCategories if DoerSelectedSubCategory.objects.filter(doerDataId__userId=doer).exists() else [],
                        "message": {
                            'success': True,
                            "successCode": 103,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "Panel status fetched successfully"
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


class JobIntitiatePanelOne(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userTypeId=1) & Q(isDeleted=False)).first()
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
            jobDescription = pythonData.get('jobDescription', False)
            chatId = pythonData.get('chatId', False)
            doerId = pythonData.get('doerId', False)
            searchKeyword = pythonData.get('searchKeyword', False)
            subCatId = pythonData.get('subCatId', False)
            if not jobDescription:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "jobDescription key required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not chatId:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "chatId key required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not doerId:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "doerId key required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not searchKeyword:
                response = {
                    "error": {
                        "errorCode": 507,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "searchKeyword key required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            doer = User.objects.filter(Q(id=doerId) & Q(
                isVerified=True) & Q(userTypeId=2)).first()
            if not doer:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "ianvalif doerId please check!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if Job.objects.filter(Q(chatId=chatId) & Q(userId=user) & Q(jobStatus=1)).exists():
                response = {
                    "error": {
                        "errorCode": 506,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "job already initiated move forward to next panel action!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
            job = Job.objects.create(userId=user, jobPanelStatus=1, jobStatus=1,
                                     chatId=chatId, jobDescription=jobDescription, doerId=doer, searchKeyword=searchKeyword, subCatId=SubCategory.objects.filter(id=subCatId).first() if subCatId else None)
            response = {
                "error": None,
                "response": {
                    "jobId": job.id,
                    "panelStatus": job.jobPanelStatus,
                    "message": {
                        'success': True,
                        "successCode": 103,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "job initiated successfully!!!"
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


class ShareJobPanelTwo(RetrieveAPIView):
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
            jobId = pythonData.get('jobId', False)
            isShare = pythonData.get('isShare')
            if not jobId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "jobId key required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if isShare == None:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "isShare key required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not Job.objects.filter(Q(id=jobId) & Q(userId=user) & Q(jobStatus=1)).exists():
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Inalid jobId please check!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            job = Job.objects.filter(
                Q(id=jobId) & Q(userId=user) & Q(jobStatus=1)).first()

            if isShare:
                if JobAssign.objects.filter(Q(jobId=job) & Q(assignStatus=1)).exists():
                    response = {
                        "error": {
                            "errorCode": 506,
                            "statusCode": status.HTTP_400_BAD_REQUEST,
                            "errorMessage": "Job already share to the related doers!!"
                        },
                        "response": None
                    }
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)
                else:
                    catUsers = DoerSelectedSubCategory.objects.filter(Q(Q(subCatId__subCatName__icontains=job.searchKeyword) | Q(
                        subCatId__catId__catName__icontains=job.searchKeyword)) & Q(subCatId__catId__isApproved=True)).values_list('doerDataId__userId', flat=True)
                    productsFilter = Product.objects.filter(
                        userId__in=catUsers).values_list('userId', flat=True)
                    doers = User.objects.filter(Q(id__in=productsFilter) & Q(userTypeId=2) & Q(
                        isDeleted=False) & Q(isVerified=True) & Q(isApproved=2)).exclude(id=job.doerId.id)
                    if not doers:
                        job.jobStatus = 2
                        job.jobPanelStatus = 2
                        job.isJobShare = True
                        job.save()
                        response = {
                            "error": None,
                            "response": {
                                "jobId": job.id,
                                "panelStatus": job.jobPanelStatus,
                                "message": {
                                    'success': True,
                                    "successCode": 101,
                                    "statusCode": status.HTTP_200_OK,
                                    "successMessage": "Job successfully assign related doers!"
                                }
                            }
                        }
                        return Response(response, status=status.HTTP_200_OK)

                    for doer in doers:
                        pythonData["jobId"] = job.id
                        pythonData["doerId"] = doer.id
                        pythonData["assignStatus"] = 1
                        serializer = JobAssignSerializer(data=pythonData)
                        if serializer.is_valid(raise_exception=True):
                            serializer.save()
                            tokens = [doer.deviceToken]
                            message = f"Dear {doer.fullName} you have recieved job request please review!"
                            title = "Slaychat-Job Request Recieved!!"
                            data = {
                                "NotificationType": "Job Request",
                                "jobId": job.id
                            }
                            res = send_notification(
                                title, message, tokens, data)
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
                    job.jobStatus = 2
                    job.jobPanelStatus = 2
                    job.isJobShare = True
                    job.save()
                    response = {
                        "error": None,
                        "response": {
                            "jobId": job.id,
                            "panelStatus": job.jobPanelStatus,
                            "message": {
                                'success': True,
                                "successCode": 101,
                                "statusCode": status.HTTP_200_OK,
                                "successMessage": "Job successfully assign related doers!"
                            }
                        }
                    }
                    return Response(response, status=status.HTTP_200_OK)

            else:
                job.jobStatus = 2
                job.jobPanelStatus = 2
                job.save()
                response = {
                    "error": None,
                    "response": {
                        "jobId": job.id,
                        "panelStatus": job.jobPanelStatus,
                        "message": {
                            'success': True,
                            "successCode": 103,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "job status running!!!"
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


class RequestCurrentDoerPanelThree(RetrieveAPIView):
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
            jobId = pythonData.get('jobId', False)
            if not jobId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "jobId key required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            job = Job.objects.filter(Q(id=jobId) & Q(userId=user) & Q(
                jobStatus=2) & Q(jobPanelStatus=2)).first()
            if not job:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid jobId please check!!!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            tokens = [job.doerId.deviceToken]
            message = f"Request message from {job.userId.fullName}"
            title = "message for panel-3"
            data = {
                "NotificationType": "Cross Platform Information",
                "jobId": job.id,
                "doerId":job.doerId.id,
                "customerId":job.userId.id,
                "chatId":job.chatId,
                "customerProfileImg":job.userId.profileImage,
                "customerName":job.userId.fullName
            }
            response = send_notification(title, message, tokens, data)
            # if response:
            pythonData["jobId"] = job.id
            pythonData["doerId"] = job.doerId.id
            serializer = JobAssignSerializer(data=pythonData)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
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
            job.jobPanelStatus = 3
            job.save()
            response = {
                "error": None,
                "response": {
                    "jobId": job.id,
                    "panelStatus": job.jobPanelStatus,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "request sent to the doer successfully"
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)
            # else:
            #     response = {
            #         "error": {
            #             "errorCode": 507,
            #             "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
            #             "errorMessage": "notificaton send fail please check your device token!!"
            #         },
            #         "response": None
            #     }
            #     return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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


class CreateProposal(CreateAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY,
                               algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userTypeId=2) & Q(isVerified=True)).first()
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
            jobId = pythonData.get('jobId', False)
            discountAmount = pythonData.get('discountAmount', False)
            totalAmount = pythonData.get('totalAmount', False)
            shortDescription = pythonData.get('shortDescription', False)

            addProductWithOffer = pythonData.get('addProductWithOffer', False)
            isAvailable = pythonData.get('isAvailable')

            if not jobId or not totalAmount or not shortDescription:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "required parameters are jobId, totalAmount and shortDescription!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if isAvailable == None:
                response = {
                    "error": {
                        "errorCode": 512,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "isAvailable key required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if addProductWithOffer is None:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "atleast one product should be added please check !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            job = Job.objects.filter(
                Q(id=jobId) & Q(jobStatus=2) & Q(jobPanelStatus=3)).first()
            if not job:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            pythonData["jobId"] = job.id
            pythonData["doerId"] = user.id
            pythonData["amount"] = totalAmount
            pythonData["discountAmount"] = discountAmount
            pythonData["shortDescription"] = shortDescription
            if JobProposal.objects.filter(Q(jobId=job) & Q(doerId=user) & Q(status=1)).exists():
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "Already created proposal for this job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)

            serializer = ProposalSerializer(data=pythonData)
            if serializer.is_valid(raise_exception=True):
                proposal = serializer.save()
                for obj in addProductWithOffer:
                    JobProposalProduct.objects.create(
                        proposalId=proposal,
                        productId=Product.objects.filter(
                            id=obj["productId"]).first(),
                        offerId=Offer.objects.filter(
                            id=obj["offerId"]).first() if obj["offerId"] else None,
                        quantity=obj["quantity"],
                        discountedAmount=obj["discountedAmount"] if obj["discountedAmount"] else None
                    )
                job.jobPanelStatus = 4
                job.save()
                user.isAvailable = isAvailable
                user.save()
                if JobAssign.objects.filter(Q(doerId=user) & Q(jobId=job) & Q(assignStatus=1)).exists():
                    JobAssign.objects.filter(Q(doerId=user) & Q(
                        jobId=job) & Q(assignStatus=1)).update(assignStatus=2)
                tokens = [job.userId.deviceToken]
                message = f"Request reply from {job.doerId.fullName}"
                title = "message for panel-4"
                data = {
                    "NotificationType": "Cross Platform Information",
                    "jobId": job.id,
                    "panelStatus": job.jobPanelStatus,
                    "doerId":job.doerId.id,
                    "customerId":job.userId.id,
                    "chatId":job.chatId,
                    "doerProfileImg":job.doerId.profileImage,
                    "doerName":job.doerId.fullName
                }
                res = send_notification(title, message, tokens, data)
                response = {
                    "error": None,
                    "response": {
                        "jobId": job.id,
                        "panelStatus": job.jobPanelStatus,
                        # "proposalId":proposal.id,
                        "message": {
                            'success': True,
                            "successCode": 101,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "Proposal Reply From Doer Submitted!"
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


class GetProposalForEditViaDoer(CreateAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY,
                               algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userTypeId=2) & Q(isVerified=True)).first()
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
            jobId = pythonData.get('jobId', False)
            proposalId = pythonData.get('proposalId', False)

            if not jobId or not proposalId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "jobId, proposalId required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            job = Job.objects.filter(
                Q(id=jobId) & Q(jobStatus=2) & Q(jobPanelStatus__in=[2, 3, 4])).first()
            if not job:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            proposal = JobProposal.objects.filter(
                Q(jobId=job) & Q(id=proposalId) & Q(status=1) & Q(doerId=user)).first()
            if not proposal:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "proposal does not exists for this job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
            res = ProposalAllSerializer(proposal)

            response = {
                "error": None,
                "response": {
                    "proposalData": res.data,
                    "jobId": job.id,
                    "panelStatus": job.jobPanelStatus,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Proposal details fetched successfully!"
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

    def put(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY,
                               algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userTypeId=2) & Q(isVerified=True)).first()
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
            jobId = pythonData.get('jobId', False)
            totalAmount = pythonData.get('totalAmount', False)
            proposalId = pythonData.get('proposalId', False)
            addProductWithOffer = pythonData.get('addProductWithOffer', False)
            isAvailable = pythonData.get('isAvailable')
            if not jobId or not proposalId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "required parameters are jobId,proposalId"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if isAvailable == None:
                response = {
                    "error": {
                        "errorCode": 512,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "isAvailable key required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if addProductWithOffer is None:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "atleast one product should be added please check !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            job = Job.objects.filter(
                Q(id=jobId) & Q(jobStatus=2) & Q(jobPanelStatus__in=[2, 3, 4])).first()
            if not job:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if totalAmount:
                pythonData["amount"] = totalAmount
            porposal = JobProposal.objects.filter(Q(jobId=job) & Q(
                doerId=user) & Q(status=1) & Q(id=proposalId)).first()
            if not porposal:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "proposal id missing!!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
            with transaction.atomic():
                serializer = ProposalSerializer(
                    porposal, data=pythonData, partial=True)
                
                if serializer.is_valid(raise_exception=True):
                    proposal = serializer.save()
                    JobProposalProduct.objects.filter(
                        proposalId=proposal).all().delete()
                    for obj in addProductWithOffer:
                        JobProposalProduct.objects.create(
                            proposalId=proposal,
                            productId=Product.objects.filter(
                                id=obj["productId"]).first(),
                            offerId=Offer.objects.filter(
                                id=obj["offerId"]).first() if obj["offerId"] else None,
                            quantity=obj["quantity"],
                            discountedAmount=obj["discountedAmount"] or None
                        )
                    user.isAvailable = isAvailable
                    user.save()
                    response = {
                        "error": None,
                        "response": {
                            "message": {
                                'success': True,
                                "successCode": 101,
                                "statusCode": status.HTTP_200_OK,
                                "successMessage": "Proposal updated successfully!"
                            }
                        }
                    }
                    return Response(response, status=status.HTTP_200_OK)
                else:
                    response = {
                        "error": {
                            "errorCode": 509,
                            "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                            "errorMessage": "Somthing went wrong!!"
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


class CancelProposalViaDoerForSharedJob(CreateAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY,
                               algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userTypeId=2) & Q(isVerified=True)).first()
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
            jobId = pythonData.get('jobId', False)
            proposalId = pythonData.get('proposalId', False)
            if not jobId or not proposalId:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "required parameters are jobId,proposalId!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            job = Job.objects.filter(
                Q(id=jobId) & Q(jobStatus=2) & Q(jobPanelStatus__in=[2, 3, 4])).first()
            if not job:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            proposal = JobProposal.objects.filter(
                Q(jobId=job) & Q(doerId=user) & Q(status=1) & Q(id=proposalId)).first()
            if not proposal:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Proposal not found for this job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            proposal.status = 4
            proposal.save()
            if JobAssign.objects.filter(Q(jobId=job) & Q(doerId=user)).exists():
                JobAssign.objects.filter(Q(jobId=job) & Q(
                    doerId=user)).update(assignStatus=4)
            tokens = [job.userId.deviceToken]
            message = f"Proposal cancel via {user.fullName}"
            title = "message for panel-2"
            data = {
                "NotificationType": "Cross Platform Information",
                "jobId": job.id,
                "panelStatus": job.jobPanelStatus,
                
            }
            res = send_notification(title, message, tokens, data)
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Proposal cancel successfully!"
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


class CancelProposalViaDoer(CreateAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY,
                               algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userTypeId=2) & Q(isVerified=True)).first()
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
            jobId = pythonData.get('jobId', False)

            if not jobId:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "required parameter id jobId!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            job = Job.objects.filter(
                Q(id=jobId) & Q(jobStatus=2) & Q(jobPanelStatus=4)).first()
            if not job:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            proposal = JobProposal.objects.filter(
                Q(jobId=job) & Q(doerId=user) & Q(status=1)).first()
            if not proposal:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Proposal not found for this job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if job.isJobShare == False:
                proposal.status = 4
                proposal.save()
                job.jobStatus = 6
                job.save()
                tokens = [job.userId.deviceToken]
                message = f"Proposal cancel via {job.doerId.fullName}"
                title = "message for refresh page"
                data = {
                    "NotificationType": "Cross Platform Information",
                    "jobId": job.id,
                    "panelStatus": job.jobPanelStatus,
                    "doerId":job.doerId.id,
                    "customerId":job.userId.id,
                    "chatId":job.chatId,
                    "doerProfileImg":job.doerId.profileImage,
                    "doerName":job.doerId.fullName
                }
                res = send_notification(title, message, tokens, data)
                response = {
                    "error": None,
                    "response": {
                        "jobId": job.id,
                        "panelStatus": job.jobPanelStatus,
                        "message": {
                            'success': True,
                            "successCode": 101,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "Proposal cancel and job is end now!"
                        }
                    }
                }
                return Response(response, status=status.HTTP_200_OK)

            proposal.status = 4
            proposal.save()
            job.jobPanelStatus = 2
            job.save()
            tokens = [job.userId.deviceToken]
            message = f"Proposal cancel from {job.doerId.fullName}"
            title = "message for panel-2"
            data = {
                "NotificationType": "Cross Platform Information",
                "jobId": job.id,
                "panelStatus": job.jobPanelStatus,
            }
            res = send_notification(title, message, tokens, data)
            response = {
                "error": None,
                "response": {
                    "jobId": job.id,
                    "panelStatus": job.jobPanelStatus,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": f"Proposal cancel via {job.doerId.fullName} wait for other doers proposal"
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


class AssignsJobViaDoer(CreateAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY,
                               algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userTypeId=2) & Q(isVerified=True)).first()
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

            jobAssigns = JobAssign.objects.filter(
                Q(doerId=user) & Q(assignStatus=1)).exclude(jobId__doerId__id=user.id).order_by('-id')

            serializer = JobAssignSerializer1(data=jobAssigns, many=True)
            serializer.is_valid()

            response = {
                "error": None,
                "response": {
                    "assignJobs": serializer.data,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Job fetched successfully !"
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


class GetProposal(CreateAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
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
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            jobId = pythonData.get('jobId', False)

            if not jobId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "jobId required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            job = Job.objects.filter(
                Q(id=jobId) & Q(jobStatus=2) & Q(jobPanelStatus=4) & Q(userId=user)).first()
            if not job:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            proposal = JobProposal.objects.filter(
                Q(jobId=job) & Q(doerId=job.doerId) & Q(status=1)).first()
            if not proposal:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "proposal does not exists for this job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
            res = ProposalAllSerializer(proposal)
            if not CustomerCard.objects.filter(Q(userId=user) & Q(cardStatus=2)).first():
                response = {
                    "error": None,
                    "response": {
                        "isDefaultCard": False,
                        "proposalData": res.data,
                        "cardData": {},
                        "jobId": job.id,
                        "panelStatus": job.jobPanelStatus,
                        "message": {
                            'success': True,
                            "successCode": 101,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "Proposal details fetched successfully!"
                        }
                    }
                }
                return Response(response, status=status.HTTP_200_OK)

            cardDetail = CustomerCard.objects.filter(
                Q(userId=user) & Q(cardStatus=2)).first()
            retrive = stripe.PaymentMethod.retrieve(
                cardDetail.paymentMethodId,
            )

            response = {
                "error": None,
                "response": {
                    "isDefaultCard": True if cardDetail else False,
                    "proposalData": res.data,
                    "cardData": retrive if cardDetail else {},
                    "jobId": job.id,
                    "panelStatus": job.jobPanelStatus,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Proposal details fetched successfully!"
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


class CustomerProposalAccept(RetrieveAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
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
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            jobId = pythonData.get('jobId', False)

            if not jobId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "jobId required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            job = Job.objects.filter(
                Q(id=jobId) & Q(jobStatus=2) & Q(jobPanelStatus=4)).first()
            if not job:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            proposal = JobProposal.objects.filter(
                Q(jobId=job) & Q(doerId=job.doerId) & Q(status=1)).first()
            if not proposal:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "proposal does not exists for this job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)

            defalutPayementMethod = CustomerCard.objects.filter(
                Q(userId=user) & Q(cardStatus=2)).first()
            if not defalutPayementMethod:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Default card is missing!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            transCheck = Transaction.objects.filter(
                Q(jobId=job) & Q(userId=user) & Q(paymentStatus__in=[1, 2]))
            if transCheck:
                response = {
                    "error": {
                        "errorCode": 507,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Payment already initiated!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            try:
                res = stripe.PaymentIntent.create(
                    payment_method_types=['card'],
                    amount=round(proposal.amount*100),
                    currency='aed',
                    customer=job.userId.stripeCustomerId,
                    payment_method=defalutPayementMethod.paymentMethodId,
                    metadata={
                        "jobId": job.id
                    },
                    transfer_group=f"order{job.id}"
                )
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
            pythonData["jobId"] = job.id
            pythonData["paymentId"] = res["id"]
            pythonData["amount"] = res["amount"]/100
            pythonData["userId"] = user.id
            pythonData["paymentMethodId"] = defalutPayementMethod.id
            pythonData["paymentStatus"] = 1
            pythonData["proposalId"] = proposal.id

            serializer = TransactionCreateSerializer(data=pythonData)
            if serializer.is_valid(raise_exception=True):
                transaction = serializer.save()

                res = stripe.PaymentIntent.confirm(
                    transaction.paymentId,

                    payment_method=transaction.paymentMethodId.paymentMethodId,
                )
                # print(res)
                # chargeId = res["charges"]["data"][0]["id"]
                # reciptUrl = res["charges"]["data"][0]["receipt_url"]
                # print(reciptUrl)
                Transaction.objects.filter(id=transaction.id).update(
                    paymentStatus=2)
                proposal.status = 2
                proposal.save()
                job.jobStatus = 3
                job.jobPanelStatus = 5
                job.save()
                JobAssign.objects.filter(Q(doerId=User.objects.filter(
                    id=job.doerId.id).first()) & Q(jobId=job)).update(assignStatus=3)
                JobAssign.objects.filter(Q(jobId=job) & Q(
                    assignStatus__in=[1, 2])).all().update(assignStatus=4)
                subject = "Job accept request mail"
                messag = f"jobDetails:Text content missing"
                emailList = [job.userId.email, job.doerId.email]
                send_email_accept(emailList,subject, messag)
                tokens = [job.doerId.deviceToken]
                message = f"Proposal accept via {job.userId.fullName}"
                title = "message for refresh page"
                data = {
                    "NotificationType": "Cross Platform Information",
                    "jobId": job.id,
                    "panelStatus": job.jobPanelStatus,
                    "doerId":job.doerId.id,
                    "customerId":job.userId.id,
                    "chatId":job.chatId,
                    "customerProfileImg":job.userId.profileImage,
                    "customerName":job.userId.fullName
                }
                res = send_notification(title, message, tokens, data)
                response = {
                    "error": None,
                    "response": {
                        "jobId": job.id,
                        "panelStatus": job.jobPanelStatus,
                        "message": {
                            'success': True,
                            "successCode": 101,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "transaction created successfully."
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


class RequestForNewOffer(RetrieveAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
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
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            jobId = pythonData.get('jobId', False)
            doerId = pythonData.get('doerId', False)

            if not jobId or not doerId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "jobId,doerId required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            job = Job.objects.filter(
                Q(id=jobId) & Q(jobStatus=2) & Q(jobPanelStatus=4)).first()
            if not job:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            proposal = JobProposal.objects.filter(
                Q(jobId=job) & Q(doerId=job.doerId) & Q(status=1)).first()
            if not proposal:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "proposal does not exists for this job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
            doer = User.objects.filter(Q(id=doerId) & Q(
                isVerified=True) & Q(isDeleted=False)).first()
            if not JobAssign.objects.filter(Q(doerId=doer) & Q(jobId=job) & Q(assignStatus=2)).exists():
                response = {
                    "error": {
                        "errorCode": 506,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "Job request missing for this doer or jobId !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)

            JobProposalProduct.objects.filter(
                proposalId=proposal).all().delete()
            proposal.delete()
            job.jobPanelStatus = 2
            job.jobStatus = 2
            job.save()

            JobAssign.objects.filter(Q(doerId=doer) & Q(
                jobId=job) & Q(assignStatus=2)).first().delete()
            tokens = [job.doerId.deviceToken]
            message = f"New Proposal request via {job.userId.fullName}"
            title = "message for refresh page"
            data = {
                "NotificationType": "Cross Platform Information",
                "jobId": job.id,
                "panelStatus": job.jobPanelStatus,
                "doerId":job.doerId.id,
                "customerId":job.userId.id,
                "chatId":job.chatId,
                "customerProfileImg":job.userId.profileImage,
                "customerName":job.userId.fullName
            }
            res = send_notification(title, message, tokens, data)
            response = {
                "error": None,
                "response": {
                    "jobId": job.id,
                    "panelStatus": job.jobPanelStatus,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "request for new offer sent successfully."
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


class CancelProposalAfterAccept(RetrieveAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
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
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            jobId = pythonData.get('jobId', False)
            cancelReason = pythonData.get('cancelReason', False)
            cancelOtherReason = pythonData.get('cancelOtherReason', False)

            if not jobId or not cancelReason:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "jobId required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            job = Job.objects.filter(
                Q(id=jobId) & Q(jobStatus=3) & Q(jobPanelStatus=5)).first()
            if not job:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            transCheck = Transaction.objects.filter(
                Q(jobId=job) & Q(userId=user) & Q(paymentStatus=2)).first()
            if not transCheck:
                response = {
                    "error": {
                        "errorCode": 507,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Payment missing"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if cancelReason == 5:
                if not cancelOtherReason:
                    response = {
                        "error": {
                            "errorCode": 508,
                            "statusCode": status.HTTP_404_NOT_FOUND,
                            "errorMessage": "cancelOtherReason required"
                        },
                        "response": None
                    }
                    return Response(response, status=status.HTTP_404_NOT_FOUND)
                job.cancelOtherReason = cancelOtherReason
            transCheck.paymentStatus = 5
            transCheck.save()
            job.jobStatus = 6
            job.cancelReason = cancelReason
            job.save()
            title = "Cancel Job Proposal"
            message = "Dear slayer your job has been canceled by the customer"
            data = {
                "doerId":job.doerId.id,
                "customerId":job.userId.id,
                "chatId":job.chatId,
                "customerProfileImg":job.userId.profileImage,
                "customerName":job.userId.fullName
            }
            send_notification(title, message, [job.doerId.deviceToken], data)
            response = {
                "error": None,
                "response": {
                    "jobId": None,
                    "panelStatus": 0,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "job cancel successfully."
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



class SendNotificationForCompletereJobResquest(RetrieveAPIView):
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
            jobId = pythonData.get('jobId', False)
            if not jobId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "jobId required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            job = Job.objects.filter(
                Q(id=jobId) & Q(jobStatus=3) & Q(jobPanelStatus=5)).first()
            if not job:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            title="Dear Slayer"
            message = "Please complete your job sonsultation ASAP"
            tokens = [job.userId.deviceToken]
            data = {
                "doerId":job.doerId.id,
                "customerId":job.userId.id,
                "chatId":job.chatId,
                "customerProfileImg":job.userId.profileImage,
                "customerName":job.userId.fullName
                
            }
            send_notification(title, message, tokens, data)
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Notification sent successfully!"
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
class CompleteJobViaCustomer(RetrieveAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
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
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            jobId = pythonData.get('jobId', False)
            if not jobId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "jobId required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            job = Job.objects.filter(
                Q(id=jobId) & Q(jobStatus=3) & Q(jobPanelStatus=5)).first()
            if not job:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            transCheck = Transaction.objects.filter(
                Q(jobId=job) & Q(userId=user) & Q(paymentStatus=2)).first()
            if not transCheck:
                response = {
                    "error": {
                        "errorCode": 507,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Payment missing"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            job.jobStatus = 4
            job.jobPanelStatus = 6
            job.save()
            title="Job complete confirmation"
            message = "Job has been completed"
            tokens = [job.doerId.deviceToken]
            data = {
                "doerId":job.doerId.id,
                "customerId":job.userId.id,
                "customerId":job.userId.id,
                "chatId":job.chatId,
                "customerProfileImg":job.userId.profileImage,
                "customerName":job.userId.fullName
                
            }
            send_notification(title, message, tokens, data)

            response = {
                "error": None,
                "response": {
                    "jobId": job.id,
                    "panelStatus": job.jobPanelStatus,
                    "doerName": job.doerId.fullName,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "job complete successfully."
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


class JobRating(RetrieveAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
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
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            jobId = pythonData.get('jobId', False)
            rating = pythonData.get('rating', False)
            if not jobId or not rating:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "jobId, rating required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if rating > 5:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid rating number!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            job = Job.objects.filter(
                Q(id=jobId) & Q(jobStatus=4) & Q(jobPanelStatus=6)).first()
            if not job:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if JobRatingReview.objects.filter(Q(jobId=job) & Q(doerId__isnull=False)).exists():
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "Already Rated this job!!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
            pythonData["doerId"] = job.doerId.id
            serializer = JobRatingReviewSerializer(data=pythonData)
            if serializer.is_valid(raise_exception=True):
                rating = serializer.save()
                job.jobPanelStatus = 7
                job.save()
                response = {
                    "error": None,
                    "response": {
                        "jobId": job.id,
                        "panelStatus": job.jobPanelStatus,
                        "message": {
                            'success': True,
                            "successCode": 101,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "Rate and review successfully done!"
                        }
                    }
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "error": {
                        "errorCode": 506,
                        "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "errorMessage": "Error while add rating and review. Please try again later."
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


class CustomerJobHistory(CreateAPIView):
    permission_classes = [IsAuthenticated, ]

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
            jobContinues = Job.objects.filter(Q(userId=user) & Q(
                jobStatus__in=[1, 2, 3]) & Q(isJobShare=True)).all().order_by('-id')
            pastJobs = Job.objects.filter(Q(userId=user) & Q(
                jobStatus__in=[4, 6])).all().order_by('-id')
            inprogressJobs = CustomerJobHistorySerializer(
                data=jobContinues, many=True)
            inprogressJobs.is_valid()
            pastJobs = CustomerCompleteJobsSerializer(data=pastJobs, many=True)
            pastJobs.is_valid()
            cardDetail = CustomerCard.objects.filter(
                Q(userId=user) & Q(cardStatus=2)).first()
            if cardDetail:
                retrive = stripe.PaymentMethod.retrieve(
                    cardDetail.paymentMethodId,
                )
            response = {
                "error": None,
                "response": {
                    "inprogressJobs": inprogressJobs.data,
                    "pastJobs": pastJobs.data,
                    "cardData": retrive if cardDetail else None,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Job fetched successfully !"
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


class GetProposalForSharedJob(CreateAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
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
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            jobId = pythonData.get('jobId', False)
            proposalId = pythonData.get('proposalId', False)

            if not jobId or not proposalId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "jobId, proposalId required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            job = Job.objects.filter(
                Q(id=jobId) & Q(isJobShare=True)).first()
            if not job:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            proposal = JobProposal.objects.filter(
                Q(jobId=job) & Q(id=proposalId) & Q(status=1)).first()
            if not proposal:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "proposal does not exists for this job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
            res = ProposalAllSerializer(proposal)
            if not CustomerCard.objects.filter(Q(userId=user) & Q(cardStatus=2)).first():
                response = {
                    "error": None,
                    "response": {
                        "isDefaultCard": False,
                        "proposalData": res.data,
                        "cardData": [],
                        "jobId": job.id,
                        "message": {
                            'success': True,
                            "successCode": 101,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "Proposal details fetched successfully!"
                        }
                    }
                }
                return Response(response, status=status.HTTP_200_OK)

            cardDetail = CustomerCard.objects.filter(
                Q(userId=user) & Q(cardStatus=2)).first()
            retrive = stripe.PaymentMethod.retrieve(
                cardDetail.paymentMethodId,
            )

            response = {
                "error": None,
                "response": {
                    "isDefaultCard": True,
                    "proposalData": res.data,
                    "cardData": retrive,
                    "jobId": job.id,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Proposal details fetched successfully!"
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


class CreateProposalForSharedDoer(CreateAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY,
                               algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userTypeId=2) & Q(isVerified=True)).first()
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
            jobId = pythonData.get('jobId', False)
            discountAmount = pythonData.get('discountAmount', False)
            totalAmount = pythonData.get('totalAmount', False)
            shortDescription = pythonData.get('shortDescription', False)
            addProductWithOffer = pythonData.get('addProductWithOffer', False)

            if not jobId or not totalAmount or not shortDescription:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "required parameters are jobId, totalAmount and shortDescription!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if addProductWithOffer is None:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "atleast one product should be added please check !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            job = Job.objects.filter(
                Q(id=jobId) & Q(jobStatus=2) & Q(jobPanelStatus__in=[2, 3, 4])).first()
            if not job:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if user.id == job.doerId.id:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "doer this doer already cummunicating with customer"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            pythonData["jobId"] = job.id
            pythonData["doerId"] = user.id
            pythonData["amount"] = totalAmount
            pythonData["discountAmount"] = discountAmount
            pythonData["shortDescription"] = shortDescription
            if JobProposal.objects.filter(Q(jobId=job) & Q(doerId=user) & Q(status=1)).exists():
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "Already created proposal for this job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)

            serializer = ProposalSerializer(data=pythonData)
            with transaction.atomic():
                if serializer.is_valid(raise_exception=True):
                    proposal = serializer.save()
                    for obj in addProductWithOffer:
                        JobProposalProduct.objects.create(
                            proposalId=proposal,
                            productId=Product.objects.filter(
                                id=obj["productId"]).first(),
                            offerId=Offer.objects.filter(
                                id=obj["offerId"]).first() if obj["offerId"] else None,
                            quantity=obj["quantity"],
                            discountedAmount=obj["discountedAmount"] if obj["discountedAmount"] else None
                        )
                    if JobAssign.objects.filter(Q(doerId=user) & Q(jobId=job) & Q(assignStatus=1)).exists():
                        JobAssign.objects.filter(Q(doerId=user) & Q(
                            jobId=job) & Q(assignStatus=1)).update(assignStatus=2)
                    # tokens = [job.userId.deviceToken]
                    # message = f"Request reply from {job.doerId.fullName}"
                    # title = "message for panel-4"
                    # data = {
                    #     "NotificationType": "Cross Platform Information",
                    #     "jobId": job.id,
                    #     "panelStatus": job.jobPanelStatus,
                    # }
                    # res = send_notification(title, message, tokens, data)
                    response = {
                        "error": None,
                        "response": {
                            "message": {
                                'success': True,
                                "successCode": 101,
                                "statusCode": status.HTTP_200_OK,
                                "successMessage": "Proposal Submitted!"
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


class AcceptProposalForSharedDoer(CreateAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
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
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            jobId = pythonData.get('jobId', False)
            chatId = pythonData.get('chatId', False)
            doerId = pythonData.get('doerId', False)

            if not jobId or not chatId or not doerId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "required parameters are jobId, chatId,doerId!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            job = Job.objects.filter(
                Q(id=jobId) & Q(jobStatus=2) & Q(jobPanelStatus__in=[2, 3, 4])).first()
            if not job:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            doer = User.objects.filter(id=doerId).first()
            if doer.id == job.doerId.id:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "this doer already cummunicating with customer"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            proposal = JobProposal.objects.filter(
                Q(jobId=job) & Q(doerId=doer) & Q(status=1)).first()

            if not proposal:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "proposal not initiated from this doer!!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)

            defalutPayementMethod = CustomerCard.objects.filter(
                Q(userId=user) & Q(cardStatus=2)).first()
            if not defalutPayementMethod:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Default card is missing!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            transCheck = Transaction.objects.filter(
                Q(jobId=job) & Q(userId=user) & Q(paymentStatus__in=[1, 2]))
            if transCheck:
                response = {
                    "error": {
                        "errorCode": 507,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Payment already initiated!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            try:
                res = stripe.PaymentIntent.create(
                    payment_method_types=['card'],
                    amount=round(proposal.amount*100),
                    currency='aed',
                    customer=job.userId.stripeCustomerId,
                    payment_method=defalutPayementMethod.paymentMethodId,
                    metadata={
                        "jobId": job.id
                    },
                    transfer_group=f"order{job.id}"
                )
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
            with transaction.atomic():
                pythonData["jobId"] = job.id
                pythonData["paymentId"] = res["id"]
                pythonData["amount"] = res["amount"]/100
                pythonData["userId"] = user.id
                pythonData["paymentMethodId"] = defalutPayementMethod.id
                pythonData["paymentStatus"] = 1
                pythonData["proposalId"] = proposal.id

                serializer = TransactionCreateSerializer(data=pythonData)
                if serializer.is_valid(raise_exception=True):
                    transaction = serializer.save()

                    res = stripe.PaymentIntent.confirm(
                        transaction.paymentId,

                        payment_method=transaction.paymentMethodId.paymentMethodId,
                    )
                    Transaction.objects.filter(id=transaction.id).update(
                        paymentStatus=2)
                    proposal.status = 2
                    proposal.save()
                    job.doerId = doer
                    job.chatId = chatId
                    job.jobStatus = 3
                    job.jobPanelStatus = 5
                    job.save()
                    JobAssign.objects.filter(Q(doerId=doer) & Q(
                        jobId=job)).update(assignStatus=3)
                    JobAssign.objects.filter(Q(jobId=job) & Q(
                        assignStatus__in=[1, 2])).all().update(assignStatus=4)
                    tokens = [job.doerId.deviceToken]
                    message = f"Proposal accept via {user.fullName}"
                    title = "message for reload app"
                    data = {
                        "NotificationType": "Cross Platform Information",
                        "jobId": job.id,
                        "panelStatus": job.jobPanelStatus,
                    }
                    res = send_notification(title, message, tokens, data)
                    response = {
                        "error": None,
                        "response": {
                            "jobId": job.id,
                            "panelStatus": job.jobPanelStatus,
                            "message": {
                                'success': True,
                                "successCode": 101,
                                "statusCode": status.HTTP_200_OK,
                                "successMessage": "proposal accepted successfully."
                            }
                        }
                    }
                    return Response(response, status=status.HTTP_200_OK)

            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Proposal Submitted!"
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


class AddCardGetListOfCard(CreateAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
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
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            cardNumber = pythonData.get('cardNumber', False)
            expMonth = pythonData.get('expMonth', False)
            expYear = pythonData.get('expYear', False)
            cvv = pythonData.get('cvv', False)
            cardHolderName = pythonData.get('cardHolderName', False)
            isDefault = pythonData.get('isDefault', False)
            if not cardNumber or not expMonth or not expYear or not cvv or not cardHolderName:
                response = {
                    "error": {
                        "errorCode": 500,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "required parameter missing please check!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if isDefault == None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "isDefault key required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
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
            fingerprintCheck = paymntMethodRespon["card"]["fingerprint"]
            if CustomerCard.objects.filter(Q(userId=user) & Q(fingerprint=fingerprintCheck)):
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Card already exist!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            attactRes = stripe.PaymentMethod.attach(
                paymntMethodRespon["id"],
                customer=user.stripeCustomerId,
            )
            paymentMethodId = attactRes["id"]
            fingerPrint = attactRes["card"]["fingerprint"]
            if CustomerCard.objects.filter(Q(userId=user)).count() < 1:
                card = CustomerCard.objects.create(
                    userId=user, paymentMethodId=paymentMethodId, fingerprint=fingerPrint, cardStatus=2)
                stripe.Customer.modify(
                    user.stripeCustomerId,
                    invoice_settings={
                        "default_payment_method": paymentMethodId
                    }
                )
            else:
                if isDefault:
                    CustomerCard.objects.filter(
                        userId=user).all().update(cardStatus=1)
                    card = CustomerCard.objects.create(
                        userId=user, paymentMethodId=paymentMethodId, fingerprint=fingerPrint, cardStatus=2)
                    stripe.Customer.modify(
                        user.stripeCustomerId,
                        invoice_settings={
                            "default_payment_method": paymentMethodId
                        }
                    )

                else:
                    card = CustomerCard.objects.create(
                        userId=user, paymentMethodId=paymentMethodId, fingerprint=fingerPrint)
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "card successfully added!"
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

    def get(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userTypeId=1)).first()
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
            if not user.stripeCustomerId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Stripe CustomerId is missing!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            res = stripe.Customer.list_payment_methods(
                user.stripeCustomerId,
                type="card",
            )
            customerDefaultCard = stripe.Customer.retrieve(
                user.stripeCustomerId)
            response = {
                "error": None,
                "response": {
                    "defaultCardId": customerDefaultCard["invoice_settings"]["default_payment_method"],
                    "paymentMethodsList": res,
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Fetched paymentmethods details successfully."
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


class CardDetachView(DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userTypeId=1)).first()
            paymentMethodId = pythonData.get('paymentMethodId', False)
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
            if not user.stripeCustomerId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Stripe CustomerId is missing!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not paymentMethodId:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "paymentMethodId field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            check = CustomerCard.objects.filter(
                Q(userId=user) & Q(paymentMethodId=paymentMethodId)).first()

            if not check:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "paymentMethodId invalid!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if check.cardStatus == 2:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "errorMessage": "You can not delete default card!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            checkRes = stripe.Customer.retrieve(user.stripeCustomerId)
            if checkRes["invoice_settings"]["default_payment_method"] == paymentMethodId:

                res = stripe.PaymentMethod.detach(
                    paymentMethodId,
                )
                CustomerCard.objects.filter(Q(userId=user) & Q(
                    paymentMethodId=paymentMethodId)).delete()
                makDefaultMethod = CustomerCard.objects.filter(
                    Q(userId=user)).first()
                if CustomerCard.objects.filter(Q(userId=user)).count() > 0:
                    stripe.Customer.modify(
                        user.stripeCustomerId,
                        invoice_settings={
                            "default_payment_method": makDefaultMethod.paymentMethodId}
                    )
                    CustomerCard.objects.filter(Q(userId=user) & Q(
                        paymentMethodId=makDefaultMethod.paymentMethodId)).update(cardStatus=2)
            else:
                res = stripe.PaymentMethod.detach(
                    paymentMethodId,
                )
                CustomerCard.objects.filter(Q(userId=user) & Q(
                    paymentMethodId=paymentMethodId)).delete()

            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Card Deleted Successfully."
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


class MakeDefaultCardView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userTypeId=1)).first()
            paymentMethodId = pythonData.get('paymentMethodId', False)
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
            if not paymentMethodId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "paymentmethodId field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if not CustomerCard.objects.filter(Q(userId=user) & Q(paymentMethodId=paymentMethodId)).first():
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid payment method id!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not user.stripeCustomerId:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Stripe CustomerId is missing for this user!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            allcard = CustomerCard.objects.filter(userId=user).all()
            for card in allcard:
                if card.paymentMethodId == paymentMethodId:
                    stripe.Customer.modify(
                        user.stripeCustomerId,
                        invoice_settings={
                            "default_payment_method": paymentMethodId
                        }
                    )
                    card.cardStatus = 2
                    card.save()
                else:
                    card.cardStatus = 1
                    card.save()

            response = {
                "error": None,
                "response": {
                    "defaultPaymetmethodId": paymentMethodId,
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Default Card Set Successfully."
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


class DoerJobTask(CreateAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY,
                               algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userTypeId=2) & Q(isVerified=True)).first()
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
            activeJobs = Job.objects.filter(Q(
                jobStatus=3) & Q(jobPanelStatus=5) & Q(doerId=user)).all().order_by('-id')
            jobIds = JobAssign.objects.filter(Q(doerId=user) & Q(
                assignStatus=2)).values_list("jobId", flat=True)
            proposedJobs = Job.objects.filter(Q(jobStatus=2) & Q(
                jobPanelStatus__in=[2, 3, 4]) & Q(id__in=jobIds) & Q(isJobShare=True)).exclude(doerId__id=user.id).all().order_by("-id")
            pastJobs = Job.objects.filter(Q(doerId=user) & Q(
                jobStatus__in=[4, 6])).all().order_by('-id')
            # inprogressJobs = CustomerJobHistorySerializer(
            #     data=jobContinues, many=True)
            # inprogressJobs.is_valid()
            pastJobs = CustomerCompleteJobsSerializer(data=pastJobs, many=True)
            pastJobs.is_valid()
            activeJobs = CustomerCompleteJobsSerializer(
                data=activeJobs, many=True)
            activeJobs.is_valid()
            proposedJobs = ProposedJobsSerializer(
                data=proposedJobs, many=True, context={"doerId": user.id})
            proposedJobs.is_valid()

            response = {
                "error": None,
                "response": {
                    "activeJobs": activeJobs.data,
                    "proposedJobs": proposedJobs.data,
                    "pastJobs": pastJobs.data,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Job fetched successfully !"
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


class TopRatedDoers(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

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
            now = timezone.now()
            one_month_ago = datetime.datetime(now.year, now.month - 1, 1)
            month_end = datetime.datetime(
                now.year, now.month, 1) - datetime.timedelta(seconds=1)
            doerIds = Job.objects.filter(Q(jobStatus=4) & Q(jobPanelStatus=7) & Q(createdAt__gt=one_month_ago) & Q(
                createdAt__lt=month_end)).values_list('doerId', flat=True).distinct()
            doers = User.objects.filter(
                Q(id__in=doerIds) & Q(isVerified=True)).all()

            if not doers:
                doers = Job.objects.filter(Q(jobStatus=4) & Q(
                    jobPanelStatus=7)).values_list('doerId', flat=True).distinct()
                if JobRatingReview.objects.filter(doerId__in=doers).values_list('doerId', flat=True).exists():
                    ids = JobRatingReview.objects.filter(
                        doerId__in=doers).values_list('doerId', flat=True).distinct()
                    doers = User.objects.filter(
                        Q(id__in=ids) & Q(isVerified=True)).all()
            jsonData = TopRatedDoersSerializer(
                doers, many=True, context={"customer": user})

            response = {
                "error": None,
                "response": {
                    "topRatedDoers": jsonData.data,
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Top rated doers list fetched successfully"
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


class AddFavDoerRemoveFavDoer(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            doerId = pythonData.get('doerId', False)
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userTypeId=1)).first()
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
            if not doerId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "doerId required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not User.objects.filter(Q(id=doerId) & Q(userTypeId=2) & Q(isDeleted=False) & Q(isVerified=True)).first():
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid doerId!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            doer = User.objects.filter(Q(id=doerId) & Q(
                userTypeId=2) & Q(isDeleted=False)).first()
            if FavouriteDoer.objects.filter(Q(doerId=doer) & Q(userId=user)).first():
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": f'{doer.fullName} already added in your favourite list!'
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            FavouriteDoer.objects.create(doerId=doer, userId=user)
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": f'{doer.fullName} successfully added in your favourite list'
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

    def delete(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            doerId = pythonData.get('doerId', False)
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userTypeId=1)).first()
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
            if not doerId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "doerId required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not User.objects.filter(Q(id=doerId) & Q(userTypeId=2) & Q(isDeleted=False) & Q(isVerified=True)).first():
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid doerId!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            doer = User.objects.filter(Q(id=doerId) & Q(
                userTypeId=2) & Q(isDeleted=False)).first()
            if not FavouriteDoer.objects.filter(Q(doerId=doer) & Q(userId=user)).first():
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": f'{doer.fullName} not in favourite list!'
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            FavouriteDoer.objects.filter(
                Q(doerId=doer) & Q(userId=user)).delete()
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": f'{doer.fullName} successfully removed from favourite list!'
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

    def get(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userTypeId=1)).first()
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
            doerIds = FavouriteDoer.objects.filter(
                Q(userId=user)).all().values_list('doerId', flat=True)
            doers = User.objects.filter(Q(id__in=doerIds) & Q(
                isVerified=True) & Q(isDeleted=False)).all()
            jsonRes = DoerProfileSerializerForFavrouiteList(
                doers, many=True, context={"customer": user.id})
            response = {
                "error": None,
                "response": {
                    "favouriteList": jsonRes.data,
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": 'favourite list fetched successfully'
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


class QueryListing(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
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
            querys = QueryTicket.objects.filter(
                Q(userId=user)).all().order_by('-id')
            serializer = QuerySerializer(querys, many=True)
            response = {
                "error": None,
                "response": {
                    "queries": serializer.data,
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Query listing fetch successfully"
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


class InitiateQuery(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id'])).first()
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
            queryTitle = pythonData.get('queryTitle', False)
            query = pythonData.get('query', False)

            if not queryTitle or not query:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "queryTitle and query are required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            pythonData["userId"] = user.id
            query = QuerySerializer(data=pythonData)
            if query.is_valid():
                query.save()
                response = {
                    "error": None,
                    "response": {
                        "message": {
                            'success': True,
                            "successCode": 102,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": 'successfully submitted your query'
                        }
                    }
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "error": {
                        "errorCode": 509,
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "errorMessage": "Somthing went wrong!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

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


class InsertChatToQuery(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(id=user['user_id']).first()
            ticketId = pythonData.get('ticketId', False)
            message = pythonData.get('message', False)
            if not message:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "message field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not ticketId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "ticketId field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            query = QueryTicket.objects.filter(Q(
                id=ticketId) & Q(userId=user.id)).first()

            if not query:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid ticketId!!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            data = {
                "message": message,
                "ticketId": ticketId,
                "senderId": user.id,
                "receiverId": User.objects.filter(is_superuser=1).first().id
            }

            serializer = CreatChatRecordSerializer(data=data)
            serializer.is_valid()
            serializer.save()

            response = {
                "error": None,
                "response": {
                    "data": None,
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Message sent successfully."
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)

        except Exception as exception:
            response = {
                "error": {
                    "errorCode": 540,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(exception)
                },
                "response": None
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class GetChatByTicketId(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(id=user['user_id']).first()
            ticketId = pythonData.get('ticketId', False)
            if not ticketId:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "ticketId field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            query = QueryTicket.objects.filter(
                id=ticketId, userId=user.id).first()

            if not query:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid ticket id for not found!!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            chats = QueryChat.objects.filter(
                ticketId=ticketId).all()
            chats = ChatDetailSerializer(data=chats, many=True)
            chats.is_valid()

            response = {
                "error": None,
                "response": {
                    "chatDetails": chats.data,
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Chat list."
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)

        except Exception as exception:
            response = {
                "error": {
                    "errorCode": 540,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(exception)
                },
                "response": None
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class DeleteShareJob(DestroyAPIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
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
            jobId = pythonData.get('jobId', False)

            if not jobId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "required parameters are jobId!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            job = Job.objects.filter(Q(userId=user) & Q(
                jobStatus__in=[2, 3, 4, 5]) & Q(isJobShare=True) & Q(id=jobId)).first()
            if not job:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            jobProposalIds = JobProposal.objects.filter(Q(jobId=job)).exclude(
                doerId=job.doerId.id).values_list('id', flat=True)
            JobProposalProduct.objects.filter(
                id__in=jobProposalIds).all().delete()
            JobProposal.objects.filter(Q(jobId=job)).exclude(
                doerId=job.doerId.id).all().delete()
            JobAssign.objects.filter(Q(jobId=job)).exclude(
                doerId=job.doerId.id).all().delete()
            job.isJobShare = False
            job.save()

            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "delete all shared job request"
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


class DoerSubCategories(RetrieveAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            # token = request.META.get(
            #     'HTTP_AUTHORIZATION', " ").split(' ')[1]
            # userr = jwt.decode(token, key=SECRET_KEY,
            #                    algorithms=['HS256', ])
            # user = User.objects.filter(
            #     Q(id=userr['user_id']) & Q(userTypeId=2) & Q(isVerified=True)).first()
            # if user is None:
            #     response = {
            #         "error": {
            #             "errorCode": 500,
            #             "statusCode": status.HTTP_404_NOT_FOUND,
            #             "errorMessage": "User not found!"
            #         },
            #         "response": None
            #     }
            #     return Response(response, status=status.HTTP_404_NOT_FOUND)
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            doerId = pythonData.get('doerId', False)
            if not doerId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "doerId is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            doer = User.objects.filter(
                Q(id=doerId) & Q(isVerified=True)).first()
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

            selectedSubCategories = DoerSelectedSubCategory.objects.filter(
                doerDataId__userId=doer).values_list('subCatId__id', flat=True)
            subCats = SubCategory.objects.filter(
                id__in=selectedSubCategories).all()
            serializer = SubCatSerializer(subCats, many=True)

            response = {
                "error": None,
                "response": {
                    "services": serializer.data,
                    "message": {
                        'success': True,
                        "successCode": 103,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "services fetched"
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



class DeleteAssignJobByDoer(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
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
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            jobId = pythonData.get('jobId', False)
            if not jobId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "jobId key required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            
            if not JobAssign.objects.filter(Q(jobId=jobId) & Q(doerId=user) & Q(assignStatus__in=[1,2])).exists():
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid jobId please check!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            JobAssign.objects.filter(Q(jobId=jobId) & Q(doerId=user) & Q(assignStatus__in=[1,2])).first().delete()
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 103,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Assign job removed"
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
        

class JobRatingViaDoer(RetrieveAPIView):
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
            jobId = pythonData.get('jobId', False)
            rating = pythonData.get('rating', False)
            if not jobId or not rating:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "jobId, rating required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if rating > 5:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid rating number!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            job = Job.objects.filter(
                Q(id=jobId) & Q(jobStatus=4)).first()
            if not job:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid job !!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if JobRatingReview.objects.filter(Q(jobId=job) & Q(userId__isnull=False)).exists():
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "Already Rated this job!!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
            pythonData["userId"] = job.userId.id
            serializer = JobRatingReviewSerializer(data=pythonData)
            if serializer.is_valid(raise_exception=True):
                rating = serializer.save()
                response = {
                    "error": None,
                    "response": {
                        "jobId": job.id,
                        "message": {
                            'success': True,
                            "successCode": 101,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "Rate and review successfully done!"
                        }
                    }
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "error": {
                        "errorCode": 506,
                        "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "errorMessage": "Error while add rating and review. Please try again later."
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