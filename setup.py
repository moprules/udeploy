#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup
from udeploy import __version__
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="udeploy",
    version=__version__,
    entry_points={
        'console_scripts': ['udeploy=udeploy:main'],
    },
    author="Oleg Silver",
    author_email="rav-navini-gego-cutropal@yandex.ru",
    description="Простой скрипт на питоне, который поможет развернуть ваше приложение",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ogurechik/udeploy",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.6',
    license='MIT',
)
