# coding: utf-8
import threading
# import types
import logging


import gevent
from gevent.pool import Pool
from gevent import monkey
from crontab import CronTab
monkey.patch_all()


class Interval(object):
    def __init__(self, zt):
        self.is_seconds = False
        if isinstance(zt, int):
            self.per = int(zt)
            self.is_seconds = True
        else:
            self.per = CronTab(zt)
        self.started = True

    def next(self):
        if self.is_seconds:
            return self.per
        return self.per.next()


class Task(object):
    def __init__(self, name, action, timer, *args, **kwargs):
        self.name = name
        self.action = action
        self.timer = timer
        self.args = args
        self.kwargs = kwargs


class Scheduler(object):
    '''
    Time-based scheduler
    '''
    def __init__(self, logger_name='greenlock.task'):
        self.logger_name = logger_name
        self.tasks = []
        self.active = {}  # action task name registry
        self.waiting = {}  # action task name registry
        self.running = True

    def schedule(self, name, timer, func, *args, **kwargs):
        self.tasks.append(Task(name, func, timer, *args, **kwargs))
        self.active[name] = []  # list of greenlets
        self.waiting[name] = []

    def unschedule(self, task_name):
        for greenlet in self.waiting[task_name]:
            try:
                gevent.kill(greenlet)
            except BaseException:
                pass

    def stop_task(self, task_name):
        for greenlet in self.active[task_name]:
            try:
                gevent.kill(greenlet)
                self.active[task_name] = []
            except BaseException:
                pass

    def _remove_dead_greenlet(self, task_name):
        for greenlet in self.active[task_name]:
            try:
                # Allows active greenlet continue to run
                if greenlet.dead:
                    self.active[task_name].remove(greenlet)
            except BaseException:
                pass

    def run(self, task):
        self._remove_dead_greenlet(task.name)
        greenlet_ = gevent.spawn(task.action, *task.args, **task.kwargs)
        self.active[task.name].append(greenlet_)
        try:
            greenlet_later = gevent.spawn_later(task.timer.next(), self.run, task)
            self.waiting[task.name].append(greenlet_later)
            return greenlet_, greenlet_later
        except StopIteration:
            pass
        except Exception:
            pass
        return greenlet_, None

    def run_tasks(self):
        pool = Pool(len(self.tasks))
        for task in self.tasks:
            pool.spawn(self.run, task)
        return pool

    def daemon(self, flag=False):
        if flag:
            self.run_forever
        else:
            my_thread = threading.Thread(target=self.run_forever)
            my_thread.start()

    def run_forever(self):
        try:
            task_pool = self.run_tasks()
            while self.running:
                gevent.sleep(seconds=0.1)
            task_pool.join(timeout=30)
            task_pool.kill()
        except KeyboardInterrupt:
            task_pool.closed = True
            task_pool.kill()
            logging.getLogger(self.logger_name).info('Time scheduler quits')

    def stop(self):
        self.running = False
