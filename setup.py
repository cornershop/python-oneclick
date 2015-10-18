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
    name='oneclick',
    #version=version,
    #version='0.0.1',
    #description=__import__('oneclick').__doc__.strip(),
    long_description=long_description,
    author='Ignacio Hermosilla',
    author_email='hermosillavenegas@gmail.com',
    maintainer='Ignacio  Hermosilla',
    maintainer_email='hermosillavenegas@gmail.com',
    #url='http://github.com/ignaciohermosilla/one_click',
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
    keywords=['oneclick', 'one_click', 'transbank', 'webpay', 'chile', 'payments'],
    install_requires=[
        'pytz',
        'arrow==0.6.0',
        'future==0.12.3',
        'rsa==3.0',
        'pyOpenSSL==0.15.1',
        'requests==2.5.3',
        'requests_toolbelt',
        'rsa',
        'loggly-python-handler'
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