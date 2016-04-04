#coding:utf-8

import os
import requests
import threading
import functools
from datetime import datetime
import time

import geventcron


def async(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        my_thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        my_thread.start()
    return wrapper

@async
def func_1():
    print 'Call func_1'

def func_2():
    print 'Call func_2'

def func_3():
    print 'Call func_3'

#尽量别用堵塞的模块,可以用grequests
def block():
    requests.get("http://www.google.com/")

if __name__ == "__main__":
    scheduler = geventcron.Scheduler(logger_name='task_scheduler')
    scheduler.schedule('task_1', geventcron.Interval("*/1 * * * *"), func_1)
    scheduler.schedule('task_2', geventcron.Interval(2), func_2)
    scheduler.schedule('task_3', geventcron.Interval(3), func_3)
    # scheduler.run_forever()
    scheduler.daemon(flag=True)
    print "daemon"
    time.sleep(100)
