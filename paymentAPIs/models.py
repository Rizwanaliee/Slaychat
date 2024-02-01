from django.db import models
from chatPanel.models import Job, JobProposal
from auth_APIs.models import *

# Create your models here.
class Transaction(models.Model):
    paymentStatuses = ((1, "initiated"), (2, "success"), (3, "pending"),
                       (4, "Falied"), (5, "refunded"), (6, "failed"), (7, "cancelled"))
    paymentId = models.CharField(
        max_length=255, default=None, null=False, blank=False)
    jobId = models.ForeignKey(
        Job, on_delete=models.CASCADE, related_name='job_trans_Id', db_column='jobId', null=False)
    userId = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='userId_transaction', db_column='userId')
    amount = models.DecimalField(
        max_length=255, default=0.00, decimal_places=2, max_digits=10, null=False
    )
    paymentMethodId = models.ForeignKey(
        CustomerCard,on_delete=models.SET_NULL,related_name='payment_method_ref', db_column='paymentMethodId', null=True)
    paymentStatus = models.IntegerField(choices=paymentStatuses, default=1)
    proposalId = models.ForeignKey(
        JobProposal, on_delete=models.CASCADE, related_name='trans_proposal_Id', db_column='proposalId', null=True, default=None)
    reciept = models.CharField(
        max_length=255, default=None, null=True, blank=True)
    stripeFee = models.DecimalField(
        max_length=255, default=0.00, decimal_places=2, max_digits=10, null=True
    )
    netAmmount = models.DecimalField(
        max_length=255, default=0.00, decimal_places=2, max_digits=10, null=True
    )
    adminCharge = models.DecimalField(
        max_length=255, default=0.00, decimal_places=2, max_digits=10, null=True
    )
    
    createdAt = models.DateTimeField(default=now, editable=False)
    updatedAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'transactions'