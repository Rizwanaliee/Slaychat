from chatPanel.models import Job,JobAssign,JobProposal
from django.db.models import Q
from datetime import datetime, timedelta

def cancelJobAfterTimout():
    time_threshold = datetime.now() - timedelta(hours=48)
    jobIds = Job.objects.filter(Q(jobStatus__in=[1,2]) & Q(createdAt__lt=time_threshold)).values_list('id', flat=True)
    if JobAssign.objects.filter(Q(jobId__in=jobIds)).exists():
        JobAssign.objects.filter(Q(jobId__in=jobIds)).all().update(assignStatus=5)
    Job.objects.filter(Q(jobStatus__in=[1,2]) & Q(createdAt__lt=time_threshold)).all().update(jobStatus=7)