Welcome to fleming's documentation!
===================================
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

Contents:

.. toctree::
   :maxdepth: 2

   ref/fleming
   contributing
   release_notes/index

Installation
============

To install the latest release, type::

    pip install fleming

To install the latest code directly from source, type::

    pip install git+git://github.com/ambitioninc/fleming.git

Function Overview
=================

A brief description of each function in this package is below. More detailed
descriptions and advanced usage of the functions follow after that. Click on
the function names to go to their detailed descriptions.

* :ref:`convert_to_tz <ref-fleming-convert_to_tz>` : Converts a datetime object into a provided timezone.
* :ref:`add_timedelta <ref-fleming-add_timedelta>` : Adds a timedelta to a datetime object.
* :ref:`floor <ref-fleming-floor>` : Rounds a datetime object down to the previous time interval.
* :ref:`ceil <ref-fleming-ceil>` : Rounds a datetime object up to the next time interval.
* :ref:`intervals <ref-fleming-intervals>` : Gets a range of times at a given timedelta interval.
* :ref:`unix_time <ref-fleming-unix_time>` : Returns a unix time stamp of a datetime object.
