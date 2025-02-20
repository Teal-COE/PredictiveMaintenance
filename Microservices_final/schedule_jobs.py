import schedule
import time
from job1 import start,start1
import mailbody_anomaly

config = {'60'}
def hourly_prediciton_trigger():
    pass


#schedule.every(1).seconds.do(start1)
# schedule.every(7).seconds.do(start1)
schedule.every(1).minutes.do(mailbody_anomaly.analyse_anomaly)
schedule.every().hour.at(":27").do(start)
while True:
    schedule.run_pending()
    time.sleep(1)