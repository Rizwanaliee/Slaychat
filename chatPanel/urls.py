from django.urls import path
from chatPanel import views

urlpatterns = [
    path('panel/nav/status', views.ChatPanelNavStatusView.as_view()),
    path('job/initiate/panel-1', views.JobIntitiatePanelOne.as_view()),
    path('share/job/panel-2', views.ShareJobPanelTwo.as_view()),
    path('request/current/doer/panel-3', views.RequestCurrentDoerPanelThree.as_view()),
    path('create/proposal', views.CreateProposal.as_view()),
    path('get/edit/proposal', views.GetProposalForEditViaDoer.as_view()),
    path('cancel/proposal', views.CancelProposalViaDoer.as_view()),
    path('assign/jobs/for/doer', views.AssignsJobViaDoer.as_view()),
    path('get/proposal/detail', views.GetProposal.as_view()),
    path('request/for/new/proposal', views.RequestForNewOffer.as_view()),
    path('accept/proposal/with/payment', views.CustomerProposalAccept.as_view()),
    path('cancel/job/after/accept', views.CancelProposalAfterAccept.as_view()),
    path('send/notification/for/complete/job', views.SendNotificationForCompletereJobResquest.as_view()),
    path('complete/job', views.CompleteJobViaCustomer.as_view()),
    path('job/rating', views.JobRating.as_view()),
    path('customer/tasks',views.CustomerJobHistory.as_view() ),
    path('doer/tasks', views.DoerJobTask.as_view()),
    path('top/rated/doers', views.TopRatedDoers.as_view()),
    path('create/proposal/for/shared/doer', views.CreateProposalForSharedDoer.as_view()),
    path('get/proposal/for/shared/job', views.GetProposalForSharedJob.as_view()),
    path('accept/proposal/for/share/job',views.AcceptProposalForSharedDoer.as_view()),
    path('cancel/proposal/for/shared/job', views.CancelProposalViaDoerForSharedJob.as_view()),
    path('delete/shared/job/request', views.DeleteShareJob.as_view()),
    path('add/card', views.AddCardGetListOfCard.as_view()),
    path('list/card', views.AddCardGetListOfCard.as_view()),
    path('delete/card',views.CardDetachView.as_view()),
    path('set/default/card', views.MakeDefaultCardView.as_view()),
    path('add/fav/remove/fav/doer',views.AddFavDoerRemoveFavDoer.as_view()),
    ####help and support####
    path('query/listing', views.QueryListing.as_view()),
    path('initiate/query', views.InitiateQuery.as_view()),
    path('send/message', views.InsertChatToQuery.as_view()),
    path('get/chat/detail',views.GetChatByTicketId.as_view()),

    path('doer/services', views.DoerSubCategories.as_view()),
    path('delete/assign/job/doer', views.DeleteAssignJobByDoer.as_view()),
    path('job/rating/via/doer', views.JobRatingViaDoer.as_view())
]
