# from slay.settings import NOTIFICATION_SERVER_KEY
# import requests
import json
import boto3
import os
from slaychat_doer_admin_apis import settings
import uuid
from django.core.mail import send_mail
import requests


def send_notification(title, message, deviceTokens, data):
    serverToken = settings.NOTIFICATION_SERVER_KEY
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + serverToken,
    }


    body = {
        "registration_ids": deviceTokens,
        "notification": {
            "body": message,
            "title": title,
            "vibrate": 1,
            "sound": 1
        },
        "data": data
    }
    response = requests.post(
        "https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
    data = response.json()
    if data['failure'] == 0:
        return True
    else:
        return False

# def send_notification1(deviceTokens, data):
#     serverToken = NOTIFICATION_SERVER_KEY
#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': 'key=' + serverToken,
#     }

#     body = {
#         "registration_ids": deviceTokens,
#         "data": data
#     }
#     response = requests.post(
#         "https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
#     data = response.json()
#     if data['failure'] == 0:
#         return True
#     else:
#         return False

def s3_helper(file):
    s3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY,
                              aws_secret_access_key=settings.AWS_SECRET_KEY,
                              region_name=settings.REGION_NAME
                              )

    bucket = s3.Bucket(settings.S3_BUCKET)
    split_tup = os.path.splitext(file.name)
    file_extension = split_tup[1]
    new_file_name = "image"+str(uuid.uuid4())[:8]+file_extension
    bucket.put_object(Key=new_file_name, Body=file)
    file_url = 's3_url/'+new_file_name
    return file_url

def fileExists(file):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(settings.S3_BUCKET)
    print(bucket)
    key = file
    objs = list(bucket.objects.filter(Prefix=key))
    if any([w.key == file for w in objs]):
        print("Exists!")
    else:
        print("Doesn't exist")

def delete_file_from_bucket(fileName):
    bucket_name = settings.S3_BUCKET
    file_name = fileName
    s3_client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY,
                              aws_secret_access_key=settings.AWS_SECRET_KEY,
                              region_name=settings.REGION_NAME
                              )
    response = s3_client.delete_object(Bucket=bucket_name, Key=file_name)
    return True


def send_email(email, subject, message):
    subject = subject
    message = message
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True

def send_email_forget_pass(email, token):
    subject = 'Your forget password link'
    message = f'Hi, click on the link and reset the password {settings.BASE_URL}/admin-change-password/{token}/'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True



def send_email_accept(emaillist, subject, message):
    subject = subject
    message = message
    email_from = settings.EMAIL_HOST_USER
    recipient_list = emaillist
    send_mail(subject, message, email_from, recipient_list)
    return True
