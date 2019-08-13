.. cfelpyutils documentation master file, created by
   sphinx-quickstart on Tue Jul 10 12:10:05 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

CFELPyUtils
===========

.. toctree::
   :hidden:

   cfelpyutils


Introduction
------------

CFELPyUtils is a utility library written in Python and developed at the Center For Free
Electron Laser Science (CFEL) in Hamburg. It contains several functions and classes
that perform various tasks related to the processing of x-ray imaging data (currently,
mostly reading and applying geometry information to x-ray detector data). It is used by
several internal and released CFEL software projects.


Installation
------------

The CFELPyUtils library is available on PyPI and can be installed using the pip
command:

.. code-block:: bash

    python3 -m pip install cfelpyutils

Or, for python2:

.. code-block:: bash

    python -m pip install cfelpyutils


It is also available as an Anaconda package in the 'ondateam' channel. It can be
installed using the 'conda' command:

.. code-block:: bash

    conda install -c ondateam cfelpyutils


Code Documentation
------------------

Code documentation for the CFELPyUtils library can be found :doc:`here <cfelpyutils>`.