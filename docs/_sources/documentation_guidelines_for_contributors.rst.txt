Guidelines for Contributors
===========================

Contributions to the project are welcome. Please feel free to submit pull requests
using the standard `GitHub flow <https://guides.github.com/introduction/flow/>`_.


Version Control
^^^^^^^^^^^^^^^

The CFELPyUtils library is developed using the `Git <https://git-scm.com>`_ version
control system.

It uses the branching strategy proposed by Vincent Driessen and commonly known as
`Gitflow <https://nvie.com/posts/a-successful-git-branching-model>`_.


Python
^^^^^^

The CFELPyUtils library is mainly developed in `Python  <https://www.python.org>`_.

* All code in the library must run with both version 2 and 3 of Python, except for
  facility-specific code that specifically requires one of the two versions (for
  example, Python 2 for the LCSL facility). The code must specifically support all the
  currently active versions of python:

  * Python 2

    * 2.7

  * Python 3

    * 3.5
    * 3.6
    * 3.7

* The `python-future <https://python-future.org>`_ project should be used to ensure
  that code contributed to the project is compatible with all the supported versions of
  Python.

* The Python coding style should follow for the most part the `Google Python \
  Coding Style <https://github.com/google/styleguide/blob/gh-pages/pyguide.md>`_.

* All docstrings should be written following the `Google Style \
  <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html>`_.

* `Pylint <https://www.pylint.org>`_ should be run on the code before
  submission, as stated in the Google Python Coding Style Guide. In the root
  folder of the CFELPyUtils repository, contributors can find  a 'pylintrc' file with
  the settings that should be applied when linting the code. Please see `here
  <http://pylint.pycqa.org/en/latest/user_guide/run.html?highlight=pylintrc>`_ how to
  use the pylintrc file.
  
* The `Black <https://github.com/psf/black>`_ Python code formatter should be run on
  the code before submission.


C/C++
^^^^^

Some extension can, for performance reason, be written using the `C++
<https://en.wikipedia.org/wiki/C%2B%2B>`_ or  `C
<https://en.wikipedia.org/wiki/C_(programming_language)>`_ programming languages.

* All C++ code in OnDA must follow at most the C++98 ISO standard, and the code
  must compile on a Linux RHEL7/CentOS7 platform using the standard development stack
  that comes with these systems.

* Part of the C++11 standard can be used when writing extensions. However, it must be
  possible to compile the code using version 4.8 of the 'gcc' compiler (in order to
  create the Linux binary Python wheel).

* All C code in OnDA must follow at most the C99 ISO standard, and the code
  must compile on a Linux RHEL7/CentOS7 platform using the standard development stack
  that comes with these systems.

* The `Cython <http://cython.org>`_ project should be used to interface C/C++ code with
  Python.
