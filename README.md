# GeventCron

### 使用方法:

```
#coding:utf-8
import geventcron 
from datetime import datetime
import time
import os
import requests

def func_1():
    time.sleep(2)

def func_2():
    time.sleep(2)

def func_3():
    time.sleep(2)

if __name__ == "__main__":
    scheduler = geventcron.Scheduler(logger_name='task_scheduler')
    scheduler.schedule('task_1', geventsheduler.every_second(4), func_1)
    scheduler.schedule('task_2', geventsheduler.every_second(1), func_2)
    scheduler.schedule('task_3', geventsheduler.every_second(1), func_3)
    scheduler.run_forever(start_at='once')
```
