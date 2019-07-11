.. image:: https://travis-ci.org/ambitioninc/fleming.png
   :target: https://travis-ci.org/ambitioninc/fleming

.. image:: https://coveralls.io/repos/ambitioninc/fleming/badge.png
    :target: https://coveralls.io/r/ambitioninc/fleming

.. image:: https://img.shields.io/pypi/v/fleming.svg
    :target: https://pypi.python.org/pypi/fleming
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/fleming.svg
    :target: https://pypi.python.org/pypi/fleming
    :alt: Number of PyPI downloads

Fleming
=======

Fleming contains a set of routines for doing datetime manipulation. Named
after `Sandford Fleming`_, the father of worldwide standard timezones, this
package is meant to aid datetime manipulations with regards to timezones.

Fleming addresses some of the common difficulties with timezones and datetime
objects, such as performing arithmetic and datetime truncation across a
Daylight Savings Time border. It also provides utilities for generating date
ranges and getting unix times with respect to timezones.

Fleming accepts pytz timezone objects as parameters, and it is assumed that the
user has a basic understanding of pytz. Click `here`_ for more information
about pytz.

.. _Sandford Fleming: https://en.wikipedia.org/wiki/Sandford_Fleming
.. _here: http://pytz.sourceforge.net/

Installation
------------
To install the latest release, type::

    pip install fleming

To install the latest code directly from source, type::

    pip install git+git://github.com/ambitioninc/fleming.git

Documentation
=============

Full documentation is available at http://fleming.readthedocs.org/

License
=======
MIT License (see LICENSE.rst)
