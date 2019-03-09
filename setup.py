# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 11:28:44 2019

@author: david
"""

from setuptools import find_packages, setup

setup(
  name="filer",
  version="0.1.0",
  packages=find_packages(),
  include_package_data=True,
  zip_safe=False,
  install_requires=[
      "flask",
  ],
)