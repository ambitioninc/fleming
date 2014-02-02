datetime_helpers
================

This repository contains the datetime_helpers package, which contains a set of routines for doing datetime manipulation. This package is geared towards users that do datetime manipulations with regards to timezones. For example, this package allows a user to perform datetime arithmetic while crossing Daylight Savings Time boundaries. It also provides the ability to floor datetime objects to certain boundaries (such as day, week, month) while also being relative to a local time zone.

The functions in this package are outlined below.

### convert_to_tz(dt, tz, return_naive=False):
Given an aware or naive datetime dt, convert it to the timezone tz.

**Args:**
- dt: A naive or aware datetime object. If dt is naive, it has UTC set as its timezone.
- tz: A pytz timezone object specifying the timezone to which dt should be converted.
- return_naive: A boolean describing whether the return value should be a naive datetime object.

**Returns:**
An aware datetime object that was the result of converting dt into tz. If return_naive is True, the returned value has no tzinfo set.

**Examples:**
    import datetime_helpers
    import datetime
    import pytz

    dt = datetime.datetime(2013, 2, 4)
    print dt
    2013-02-04 00:00:00

    # Convert naive UTC time to aware EST time
    dt = datetime_helpers.convert_to_tz(dt, pytz.timezone('US/Eastern'))
    print dt
    2013-02-03 19:00:00-05:00

    # Convert aware EST time to aware CST time
    dt = datetime_helpers.convert_to_tz(dt, pytz.timezone('US/Central'))
    print dt
    2013-02-03 18:00:00-06:00

    # Convert aware CST time back to naive UTC time
    dt = datetime_helpers.convert_to_tz(dt, pytz.utc, return_naive=True)
    print dt
    2013-02-04 00:00:00
