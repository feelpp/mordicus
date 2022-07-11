#!/usr/bin/env python
# -*- coding: utf-8 -*-



from Mordicus import __name__ as Mordicus__name__
from Mordicus import __copyright__ as Mordicus__copyright__
from Mordicus import __copyright_holder__ as Mordicus__copyright_holder__
from Mordicus import __license__ as Mordicus__license__
from Mordicus import __version__ as Mordicus__version__
from Mordicus import __description__ as Mordicus__description__
from Mordicus import __long_description__ as Mordicus__long_description__
from Mordicus import __url__ as Mordicus__url__
from Mordicus import __contact__ as Mordicus__contact__


contact=""


import os
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
    import re
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
            'project': ('setup.py', Mordicus__name__),
            'version': ('setup.py', Mordicus__version__),
            'release': ('setup.py', Mordicus__version__),
            'source_dir': ('setup.py', 'doc')}}
else:
    cmdclass = {}
    command_options={}

here = os.path.abspath( os.path.dirname(__file__))

from distutils.version import StrictVersion   
import sys
python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

requirements = []
with open( os.path.join(here, "requirements.txt")) as fid:
    content = fid.read().split("\n")
    for line in content:
        if line.startswith( "#" ) or line.startswith( " " ) or line=="":
            continue
        elif line.startswith( "-e" ):
            reqs=line.split(";")
            add_req=True
            if len(reqs)>1:
                if reqs[1].startswith( "python_version" ):
                    if StrictVersion(reqs[1].split(">")[1])>StrictVersion(python_version):
                        add_req=False
            pname = reqs[0].split("#egg=")[1]
            req_line = "{} @ {}".format( pname, reqs[0][3:] )
            requirements.append( req_line )
        else:
            requirements.append( line )

## pip install .[test]
extras_require = {'test':['pytest',]}

setup(
    name=Mordicus__name__,
    version=Mordicus__version__,
    author_email=Mordicus__contact__,
    description=Mordicus__description__,
    long_description=Mordicus__long_description__,
    license=Mordicus__license__,
    url=Mordicus__url__,
    classifiers=[],
    install_requires=requirements,
    extras_require=extras_require,
    packages=find_packages("src"),
    include_package_data=True,
    cmdclass=cmdclass,
    package_dir={'': 'src'}
)
