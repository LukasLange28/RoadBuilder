# Copyright (C) 2023 LukasLange28
import os
from setuptools import find_packages, setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="RoadBuilder",
    version=read('VERSION.txt'),
    author="Lukas Lange",
    description=("Road builder"),
    license="GPL 3.0",
    keywords="xml vehicles track interface",
    url="https://github.com/LukasLange28/RoadBuilder/",
    packages=find_packages(),
    include_package_data=True,
    long_description=read('README.md'),
    install_requires=[
        'PyQt5',
        'track_generator',
    ],
    entry_points={
        'console_scripts': [
            'RoadBuilder = RoadBuilder.starter:start',
        ]
    }
)