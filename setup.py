# pylint: disable=C0111
#
#    This file is part of cfelpyutils.
#
#    cfelpyutils is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    cfelpyutils is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with cfelpyutils.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from setuptools import setup

import cfelpyutils


setup(
    name='cfelpyutils',
    version=cfelpyutils.__version__,
    url="https://github.com/ondateam/cfelpyutils",
    license="GNU General Public License v3.0",
    author="OnDA Team",
    author_email="valerio.mariani@desy.de",
    description="Utility functions and classes for CFEL software "
                "projects",
    long_description=(
        """
        CfelPyUtils is a library of several utility functions and
        classes used by several software projects developed at the
        Center For Free Electron Laser Science (CFEL) in Hamburg.
        """
    ),
    install_requires=['numpy'],
    packages=['cfelpyutils'],
    include_package_data=True,
    platforms='any',
    classifiers=[
        "Programming Language :: Python",

        "Development Status :: 4 - Beta",

        "Programming Language :: Python :: 3",

        "Programming Language :: Python :: 2",

        "Operating System :: OS Independent",

        "Topic :: Software Development :: Libraries :: Python Modules",

        "License :: OSI Approved :: GNU General Public License v3 "
        "or later (GPLv3+)",

        "Natural Language :: English",

        "Intended Audience :: Science/Research",
    ],
)
