#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shutil
import os
from setuptools import setup, find_packages
from bipolar_server.version import version_number


# Copy manage.py as bipolar-manage before
shutil.copyfile("manage.py", "bipolar-manage")

setup(
    name='bipolar-server',
    version=version_number,
    description='Microservice for feature toggle pattern, compatible with any language, platform and framework.',
    long_description='''Microservice for feature toggle pattern implementation, which is platform-agnostic and follows a simple approach.''',
    keywords='python django feature toggle permissions',
    author='Marinho Brandao',
    author_email='marinho@gmail.com',
    url='http://github.com/marinho/bipolar/',
    license='GPL',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
    ],
    packages=find_packages(),
    zip_safe=False, # This prevents using .egg (we need files instead of .egg
    include_package_data=True,
    install_requires=[
        "python-dateutil>=1.5,!=2.0",
        "Django",
        "South",
        "jellyfish",
        "django-tastypie",
        "requests",
        "python-social-auth",
        #"pusher"
    ],
    scripts=['bipolar-manage',],
)

