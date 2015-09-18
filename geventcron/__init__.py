# coding: utf-8

import types
import logging
import time
from datetime import timedelta, datetime
import gevent
from gevent.pool import Pool
from gevent import monkey
monkey.patch_all()

def every_second(seconds):
    delta = timedelta(seconds=seconds)
    while 1:
        yield delta

def wait_until(time_label):
    if time_label == 'next_minute':
        gevent.sleep(60 - int(time.time()) % 60)
    elif time_label == 'next_hour':
        gevent.sleep(3600 - int(time.time()) % 3600)
    elif time_label == 'tomorrow':
        gevent.sleep(86400 - int(time.time()) % 86400)

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
        if isinstance(task.timer, types.GeneratorType):
            greenlet_ = gevent.spawn(task.action, *task.args, **task.kwargs)
            self.active[task.name].append(greenlet_)
            try:
                greenlet_later = gevent.spawn_later(task.timer.next().total_seconds(), self.run, task)
                self.waiting[task.name].append(greenlet_later)
                return greenlet_, greenlet_later
            except StopIteration:
                pass
            return greenlet_, None
        # Class based timer
        try:
            if task.timer.started is False:
                delay = task.timer.next().total_seconds()
                gevent.sleep(delay)
                greenlet_ = gevent.spawn(task.action, *task.args, **task.kwargs)
                self.active[task.name].append(greenlet_)
            else:
                greenlet_ = gevent.spawn(task.action, *task.args, **task.kwargs)
                self.active[task.name].append(greenlet_)
            greenlet_later = gevent.spawn_later(task.timer.next().total_seconds(), self.run, task)
            self.waiting[task.name].append(greenlet_later)
            return greenlet_, greenlet_later
        except StopIteration:
            pass
        return greenlet_, None

    def run_tasks(self):
        pool = Pool(len(self.tasks))
        for task in self.tasks:
            pool.spawn(self.run, task)
        return pool

    def run_forever(self, start_at='once'):
        if start_at not in ('once', 'next_minute', 'next_hour', 'tomorrow'):
            raise ValueError("start_at : 'once', 'next_minute', 'next_hour', 'tomorrow'")
        if start_at != 'once':
            wait_until(start_at)
        try:
            task_pool = self.run_tasks()
            while self.running:
                gevent.sleep(seconds=1)
            task_pool.join(timeout=30)
            task_pool.kill()
        except KeyboardInterrupt:
            task_pool.closed = True
            task_pool.kill()
            logging.getLogger(self.logger_name).info('Time scheduler quits')

    def stop(self):
        self.running = False
