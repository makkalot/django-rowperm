import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-rowperm',
    version='0.1',
    description="A Django app for row-level permissions!",
    long_description=read('README'),
    author='Deniz Kurucu',
    author_email='makkalot@gmail.com',
    license='BSD',
    url='',
    download_url='',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    package_data = {
        'rowperm': []
    },
    zip_safe=False,
)
