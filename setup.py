#!/usr/bin/env python

from distutils.core import setup, Command
import os
import os.path


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = 'geventcron',
    version = '1.5',
    description = 'Gevent Crontab Scheduler',
    long_description = open('README.md').read(),
    keywords = ["gevent cron scheduler","fengyun"],
    url = 'http://xiaorui.cc',
    author = 'ruifengyun',
    author_email = 'rfyiamcool@163.com',
    install_requires = ['gevent'],
    packages = ['geventcron'],
    license =  "MIT",
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
