
from authentication.BusinessLogic.Threading import start_new_thread
from apscheduler.schedulers.background import BackgroundScheduler


@start_new_thread
def scheduler_start(function, duration):
    print('Scheduler start')
    scheduler = BackgroundScheduler()
    scheduler.add_job(function, 'interval', seconds=duration)
    scheduler.start()
