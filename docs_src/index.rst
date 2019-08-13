.. cfelpyutils documentation master file, created by
   sphinx-quickstart on Tue Jul 10 12:10:05 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

The CFELPyUtils Library
=======================

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

The CFELPyUtils library is available on the `Python Package Index
<https://pypi.org/>`_ (PyPI). It can be installed using the 'pip' command:

.. code-block:: bash

    python3 -m pip install cfelpyutils

Or, for Python 2:

.. code-block:: bash

    python2 -m pip install cfelpyutils

It is also available as a package for the `Anaconda <https://anaconda.org/>`_ Python
distribution. It can be installed using the 'conda' command:

.. code-block:: bash

    conda install -c ondateam cfelpyutils

The library can also be installed manually by checking out the repository and running:

.. code-block:: bash

    python setup.py install 


Authors
-------

The CFELPyUtils library is currently developed in the lab of 
`Henry Chapman <https://cid.cfel.de/>`_ at the Center For Free Electron Laser Science
in Hamburg. 

Many people from different institutions worlwide contribute code, testing and support
to the project:

* **Valerio Mariani** (corresponding author: valerio.mariani@desy.de)
* Anton Barty
* Andrew Morgan
* Thomas A. White


Code Documentation
------------------

Code documentation for the CFELPyUtils library can be found :doc:`here <cfelpyutils>`.


Source Code
-----------

The source code of the CFELPyUtils library can be found on GitHub:
https://github.com/ondateam/cfelpyutils


Guidelines for Contributors
---------------------------

Contributions to the projects are welcome. Please see the guidelines for contributors
:doc:`here <documentation_guidelines_for_contributors>`.