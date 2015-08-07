# encoding=UTF-8
#!/usr/bin/env python
import os
from setuptools import setup, find_packages


def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''

long_description = read_file('README.rst').strip().split('split here', 1)[0]
#version = __import__('one_click').__version__

setup(
    name='one_click',
    #version=version,
    #version='0.0.1',
    #description=__import__('one_click').__doc__.strip(),
    long_description=long_description,
    author='Ignacio Hermosilla',
    author_email='hermosillavenegas@gmail.com',
    maintainer='Ignacio  Hermosilla',
    maintainer_email='hermosillavenegas@gmail.com',
    url='http://github.com/ignaciohermosilla/one_click',
    #download_url='http://github.com/ignaciohermosilla/one_click/archive/{version}.zip'.format(version=version),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Environment :: Console',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
    keywords=['one_click', 'transbank', 'webpay', 'chile', 'payments'],
    install_requires=[
        'requests>=2.3.0',
        'six>=1.7.3',
        'PyCrypto>=2.6.1',
        'pytz',
        'M2Crypto==0.22.3',
        'PySimpleSOAP==1.16',
        'PyXML==0.8.4',
        'argparse==1.2.1',
        'arrow==0.6.0',
        'certifi==2015.04.28',
        'cffi==1.1.2',
        'cryptography==0.9.3',
        'defusedxml==0.4.1',
        'eight==0.3.2',
        'enum34==1.0.4',
        'future==0.12.3',
        'hashlib==20081119',
        'idna==2.0',
        'ipaddress==1.0.14',
        'lxml==3.4.4',
        'osa==0.1.6.6',
        'py-dom-xpath==0.1',
        'pyOpenSSL==0.15.1',
        'pyasn1==0.1.8',
        'pycparser==2.14',
        'pycrypto==2.6.1',
        'python-dateutil==2.4.2',
        'requests==2.7.0',
        'signxml==0.4.3',
        'soap2py==1.16',
        'wsgiref==0.1.2',
    ],
    tests_require=[
        'mock>=1.0.1',
        'nose>=1.3.3',
    ],
    packages=find_packages(),
    test_suite='nose.collector',
    zip_safe=True,
    license='GPLv3'
)



