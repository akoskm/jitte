# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages


setup(
    name='jitte',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['requests', 'lxml', 'jinja2'],
    url='http://github.com/integricho/jitte/',
    zip_safe=False,
)
