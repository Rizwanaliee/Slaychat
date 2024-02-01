from django.db import models
from auth_APIs.models import User
from django.utils.timezone import now


class QueryTicket(models.Model):
    status = models.IntegerField(
        choices=((1, "Pending"), (2, "Open"), (3, "Closed")), default=1)
    queryTitle = models.CharField(max_length=255, null=False)
    query = models.TextField(null=False)
    userId = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='userId_Query', db_column='userId', null=False)

    createdAt = models.DateTimeField(default=now, editable=False)
    updatedAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'query_tickets'


class QueryChat(models.Model):
    ticketId = models.ForeignKey(QueryTicket, on_delete=models.CASCADE,
                                 related_name='ticketId_QueryChat', db_column='ticketId', null=True)
    senderId = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name='senderId_QueryChat', db_column='senderId', null=False)
    receiverId = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name='receiverId_QueryChat', db_column='receiverId', null=False)
    message = models.TextField(null=False)
    isRead = models.BooleanField(default=False)
    createdAt = models.DateTimeField(default=now, editable=False)
    updatedAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'query_chats'


class FavouriteDoer(models.Model):
    userId = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="userId",
        related_name="favourite_from_userId",
    )
    doerId = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="doerId",
        related_name="favourite_to_doerId",
        null=True
    )
    createdAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'favourite_doers'
