from django.db import models
from auth_APIs.models import User, SubCategory, Product, Offer
from django.utils.timezone import now

# Create your models here.


class Job(models.Model):
    jobStatuses = ((1, "initiated"), (2, "Running"), (3, "Accepted"),
                   (4, "completed"), (5, "failed"), (6, "cancelled"),(7, "cancelTimeOut"))
    jobPanelStatuses = ((1, "intitiate"), (2, "share_job"), (3,
                        "request_proposal"), (4, "waiting"), (5, "cust_proposal_action"),(6, "rating_review"),(7, "complete"))
    jobCancelReason = ((1, "AcceptedByMistake"), (2, "DoerWasLate"), (3,
                        "Doer did not provide the promised services"), (4, "Doer did not show up"), (5, "Other reasons"))
    jobStatus = models.IntegerField(
        choices=jobStatuses, null=False, default=1)
    jobPanelStatus = models.IntegerField(
        choices=jobPanelStatuses, null=True, default=None)
    jobDescription = models.TextField(null=False)
    userId = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='user_panel_ref', db_column='userId', null=False)
    doerId = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='doer_panel_ref', db_column='doerId', null=True, default=None)
    chatId = models.CharField(max_length=255, null=False)
    isJobShare = models.BooleanField(default=False)
    searchKeyword = models.CharField(max_length=255, null=True, default=None)
    subCatId = models.ForeignKey(SubCategory, on_delete=models.CASCADE,
                               related_name='subCat_panel_ref', db_column='subCatId', null=True, default=None)
    cancelOtherReason = models.CharField(max_length=255, null=True, default=None)
    cancelReason = models.IntegerField(
        choices=jobCancelReason, null=True, default=None)

    createdAt = models.DateTimeField(default=now, editable=False)
    updatedAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'jobs'


class JobAssign(models.Model):
    assignStatus = models.IntegerField(
        choices=((1, "initiated"), (2, "ProposalCreated"), (3, "Accepted"), (4, "rejected"),(5, "cancelTimeOut")), default=1)
    jobId = models.ForeignKey(
        Job, on_delete=models.CASCADE, related_name='jobId_assign_Id', db_column='jobId', null=False)
    doerId = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='doer_assign_ref', db_column='doerId', null=False)
    createdAt = models.DateTimeField(default=now, editable=False)
    updatedAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'job_assign'


class JobProposal(models.Model):
    status = models.IntegerField(
        choices=((1, "initiated"), (2, "Accepted"), (3, "Rejected"), (4 , "cancelled")), default=1)
    jobId = models.ForeignKey(
        Job, on_delete=models.CASCADE, related_name='jobId_proposal_Id', db_column='jobId', null=False)
    doerId = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='doer_proposal_ref', db_column='doerId', null=False)
    amount = models.DecimalField(
        max_length=255, default=0.00, decimal_places=2, max_digits=10, null=True
    )
    discountAmount = models.DecimalField(
        max_length=255, default=0.00, decimal_places=2, max_digits=10, null=True
    )
    shortDescription = models.TextField(null=True, default=None)
    createdAt = models.DateTimeField(default=now, editable=False)
    updatedAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'job_proposals'


class JobProposalProduct(models.Model):

    proposalId = models.ForeignKey(
        JobProposal, on_delete=models.CASCADE, related_name='proposal_Id', db_column='proposalId', null=False)
    productId = models.ForeignKey(Product, on_delete=models.CASCADE,
                                  related_name='productId_proposal_ref', db_column='productId', null=False)
    offerId = models.ForeignKey(Offer, on_delete=models.CASCADE,
                                related_name='offerId_proposal_ref', db_column='offerId', null=True, default=None)
    quantity = models.IntegerField(null=False, default=1)
    discountedAmount = models.DecimalField(
        max_length=255, default=0.00, decimal_places=2, max_digits=10, null=True
    )
    createdAt = models.DateTimeField(default=now, editable=False)
    updatedAt = models.DateTimeField(default=now, editable=False)
    class Meta:
        db_table = 'job_proposal_products'


class JobRatingReview(models.Model):
    jobId = models.ForeignKey(
        Job, on_delete=models.CASCADE, related_name='jobId_rating_ref', db_column='jobId', null=False)
    doerId = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='doerId_rating_ref', db_column='doerId', null=True, default=None)
    userId = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='customer_rating_ref', db_column='userId', null=True, default=None)
    rating = models.IntegerField(null=False)
    review = models.TextField(null=True, default=None)
    createdAt = models.DateTimeField(default=now, editable=False)
    class Meta:
        db_table = 'rating_reviews'