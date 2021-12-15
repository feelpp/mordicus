#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__='MORDICUS FUI Project'
__version__='0.1.0'

name = 'Mordicus'
contact=""


import os
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
    import re, os
    def find_packages(path='.'):
        ret = []
        for root, dirs, files in os.walk(path):
            if '__init__.py' in files:
                ret.append(re.sub('^[^A-z0-9_]+', '', root.replace('/', '.')))
        return ret



try:
    from sphinx.setup_command import BuildDoc
    HAVE_SPHINX = True
except:
    print("Sphinx documentation not available on your installation")
    HAVE_SPHINX = False


if HAVE_SPHINX:
    cmdclass = {'build_sphinx': BuildDoc}
    command_options={
        'build_sphinx': {
            'project': ('setup.py', "mordicus"),
            'version': ('setup.py', "0.1"),
            'release': ('setup.py', "0.1.0"),
            'source_dir': ('setup.py', 'doc')}}
else:
    cmdclass = {}
    command_options={}

here = os.path.abspath( os.path.dirname(__file__))

requirements = []
with open( os.path.join(here, "requirements.txt")) as fid:
    content = fid.read().split("\n")
    for line in content:
        if line.startswith( "#" ) or line.startswith( " " ) or line=="":
            continue
        elif line.startswith( "-e" ):
            pname = line.split("#egg=")[1]
            req_line = "{} @ {}".format( pname, line[3:] )
            requirements.append( req_line )
        else:
            requirements.append( line )

## pip install .[test]
extras_require = {'test':['pytest',]}

setup(
    name=name,
    version=__version__,
    author_email=contact,
    description="",
    long_description="",
    license="",
    url="",
    classifiers=[
        'Development Status :: 1 - Beta',
    ],
    install_requires=requirements,
    extras_require=extras_require,
    packages=find_packages("src"),
    include_package_data=True,
    cmdclass=cmdclass,
    package_dir={'': 'src'}
)
