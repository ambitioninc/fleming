datetime_helpers
================

This repository contains the datetime_helpers package, which contains a set of routines for doing datetime manipulation. This package is geared towards users that do datetime manipulations with regards to timezones. For example, this package allows a user to perform datetime arithmetic while crossing Daylight Savings Time boundaries. It also provides the ability to floor datetime objects to certain boundaries (such as day, week, month) while also being relative to a local time zone.

The functions in this package are outlined below.

## convert_to_tz(time, timezone)
