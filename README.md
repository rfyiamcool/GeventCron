# GeventCron

### 原理:
gevent有个spawn_later()函数，专为定时任务打造...  

他的`缺点`就是，别让gevent调度堵塞了....尽量让你业务逻辑，采用gevent patch模块

正在尝试下，借助spawn_later周期功能，解决堵塞的问题, [查看更多GeventCron相关信息](http://xiaorui.cc)

### 安装方法:
```
pip install geventcron

or

python setup.py install
```

### 使用方法:

```
import time
import requests
import threading
import functools
from datetime import datetime


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
```
