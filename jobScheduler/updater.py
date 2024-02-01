from apscheduler.schedulers.background import BackgroundScheduler
from .cancelJobAfterTimout import cancelJobAfterTimout

def start():
    scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
    scheduler.add_job(cancelJobAfterTimout, 'interval', hours=48)
    scheduler.start()