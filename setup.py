#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
    from setuptools.command.test import test
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
    from setuptools.command.test import test


class mytest(test):
    def run(self, *args, **kwargs):
        from runtests import runtests
        runtests()

setup(
    name='nexus-redis',
    version='0.3',
    author='David Cramer',
    author_email='dcramer@gmail.com',
    url='http://github.com/dcramer/nexus-redis',
    description = 'Redis Plugin for Nexus',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'nexus>=0.1.3',
    ],
    test_suite = 'nexus_redis.tests',
    include_package_data=True,
    cmdclass={"test": mytest},
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)