#!/usr/bin/env python3
from setuptools import setup

setup(
    name='upb',
    version='0.0.3',
    packages=['upb', 'upb.tools'],
    install_requires=['pyserial-asyncio>=0.4.0'],
    exclude_package_data={'': ['test']},
    author='James Hilliard',
    author_email='james.hilliard1@gmail.com',
    description='Library for interacting with UPB Devices.',
    url='https://github.com/jameshilliard/upb',
    license='MIT',
    python_requires='>=3.6',
)
