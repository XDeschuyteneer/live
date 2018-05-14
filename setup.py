# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='livedata-subscribetags',
    version='0.1.0',
    description='Sample script to subscribe to changes of tag\'s value  ',
    long_description=readme,
    author='HMS Industrial Netwoks S.A.',
    author_email='ewon@hms-networks.com',
    url='https://developer.ewon.biz/content/apiv2',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    scripts=['APIv2/example.py'],
    entry_points={
        'console_scripts': [
            'livedata-subscribetags=APIv2.example:launch',
        ],
    },
    install_requires=[
        'stomp.py',
        'websocket-client',
    ],
    dependency_links=['git+https://github.com/gschizas/websocket-client.git@patch-1#egg=websocket-client-0'],
)
