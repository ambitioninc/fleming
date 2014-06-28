Contributing
============

Contributions and issues are most welcome! All issues and pull requests are
handled through github on the `ambitioninc repository`_. Please check for any
existing issues before filing a new one!

.. _ambitioninc repository: https://github.com/ambitioninc/fleming

Running the tests
-----------------

Once you have cloned the source code, you can run the code quality and unit
tests by running::

    $ git clone git://github.com/ambitioninc/fleming.git
    $ cd fleming
    $ virtualenv env
    $ . env/bin/activate
    $ python setup.py install
    $ pip install -r requirements/test.txt
    $ nosetests --cover-branches --with-coverage --cover-min-percentage=100 --cover-package=fleming

While 100% code coverage does not make a library bug-free, it significantly
reduces the number of easily caught bugs! Please make sure coverage is at 100%
before submitting a pull request!

Code Quality
------------

For code quality, please run::

    $ find fleming | grep .py$ | grep -v __init__.py | xargs pyflakes
    $ find fleming | grep .py$ | xargs pep8 --max-line-length=120

Code Styling
------------
Please arrange imports with the following style::

    # Standard library imports
    import os

    # Third party package imports
    from mock import patch

    # Local package imports
    from fleming import floor

Please follow `Google's python style`_ guide wherever possible.

.. _Google's python style: http://google-styleguide.googlecode.com/svn/trunk/pyguide.html

Building the docs
-----------------

When in the project directory::

    $ pip uninstall -y fleming && python setup.py install
    $ pip install -r requirements/docs.txt
    $ cd docs
    $ make html
    $ open docs/_build/html/index.html

Vulnerability Reporting
-----------------------

For any security issues, please do NOT file an issue or pull request on github!
Please contact `security@ambition.com`_ with the GPG key provided on `Ambition's
website`_.

.. _security@ambition.com: mailto:security@ambition.com
.. _Ambition's website: http://ambition.com/security/

