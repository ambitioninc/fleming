[![Build Status](https://travis-ci.org/ambitioninc/fleming.png)](https://travis-ci.org/ambitioninc/fleming)
Fleming
================

This repository contains the Fleming package, which contains a set of routines for doing datetime manipulation. Named after Sandford Fleming, the father of worldwide standard timezones, this package is meant to aid datetime manipulations with regards to timezones.

Fleming addresses some of the common difficulties with timezones and datetime objects, such as performing arithmetic and datetime truncation across a Daylight Savings Time border. It also provides utilities for generating date ranges and getting unix times with respect to timezones.

Fleming accepts pytz timezone objects as parameters, and it is assumed that the user has a basic understanding of pytz. Click [here](http://pytz.sourceforge.net/) for more information about pytz.

## Installation
To install the latest release, type:

    pip install fleming
    
To install the latest code directly from source, type:

    pip install git+git://github.com/ambitioninc/fleming.git

## Function Overview
A brief description of each function in this package is below. More detailed descriptions and advanced usage of the functions follow after that.
- convert_to_tz: Converts a datetime object into a provided timezone.
- add_timedelta: Adds a timedelta to a datetime object.
- floor: Truncates a datetime object down to a time interval.
- intervals: Gets a range of times at a given timedelta interval.
- unix_time: Returns a unix time stamp of a datetime object.

Note that all of these functions properly handle Daylight Savings Time transitions and other artifacts not normally supported in datetime manipulation. Keep reading for more detailed descriptions and examples of the functions.

### convert_to_tz(dt, tz, return_naive=False)
Given an aware or naive datetime dt, convert it to the timezone tz.

**Args:**
- dt: A naive or aware datetime object. If dt is naive, it has UTC set as its timezone.
- tz: A pytz timezone object specifying the timezone to which dt should be converted.
- return_naive: A boolean describing whether the return value should be a naive datetime object.

**Returns:**
An aware datetime object that was the result of converting dt into tz. If return_naive is True, the returned value has no tzinfo set.

**Examples:**

    import fleming
    import datetime
    import pytz

    dt = datetime.datetime(2013, 2, 4)
    print dt
    2013-02-04 00:00:00

    # Convert naive UTC time to aware EST time
    dt = fleming.convert_to_tz(dt, pytz.timezone('US/Eastern'))
    print dt
    2013-02-03 19:00:00-05:00

    # Convert aware EST time to aware CST time
    dt = fleming.convert_to_tz(dt, pytz.timezone('US/Central'))
    print dt
    2013-02-03 18:00:00-06:00

    # Convert aware CST time back to naive UTC time
    dt = fleming.convert_to_tz(dt, pytz.utc, return_naive=True)
    print dt
    2013-02-04 00:00:00

### add_timedelta(dt, td, within_tz=None, return_naive=False)
Given a naive or aware datetime dt, add a timedelta td to it and return it. If within_tz is specified, the datetime arithmetic happens with regard to the timezone. Proper measures are used to ensure that datetime arithmetic across a DST border is handled properly.

**Args:**
- dt: A naive or aware datetime object. If it is naive, it is assumed to be UTC.
- td: A timedelta (or relativedelta) object to add to dt.
- within_tz: A pytz timezone object. If provided, dt will be converted to this timezone before datetime arithmetic and then converted back to its original timezone afterwards.
- return_naive: A boolean defaulting to False. If True, the result is returned as a naive datetime object with tzinfo equal to None.

**Returns:**
An aware datetime object that results from adding td to dt. The timezone of the returned datetime will be equivalent to the original timezone of dt (or its DST equivalent if a DST border was crossed). If return_naive is True, the returned value has no tzinfo object.

**Examples:**

    import pytz
    import datetime
    import fleming

    # Do a basic timedelta addition to a naive UTC time and create an aware UTC time
    # two weeks in the future
    dt = datetime.datetime(2013, 3, 1)
    dt = fleming.add_timedelta(dt, datetime.timedelta(weeks=2))
    print dt
    2013-03-15 00:00:00+00:00

    # Do addition on an EST datetime where the arithmetic does not cross over DST
    dt = fleming.convert_to_tz(dt, pytz.timezone('US/Eastern'))
    print dt
    2013-03-14 20:00:00-04:00

    dt = fleming.add_timedelta(dt, datetime.timedelta(weeks=2, days=1))
    print dt
    2013-03-29 20:00:00-04:00

    # Do timedelta arithmetic such that it starts in DST and crosses over into no DST.
    # Note that the hours stay in tact and the timezone changes
    dt = fleming.add_timedelta(dt, datetime.timedelta(weeks=-4))
    print dt
    2013-03-01 20:00:00-05:00

    # Take a UTC time and do datetime arithmetic in regards to EST. Do the arithmetic
    # such that a DST border is crossed
    dt = datetime.datetime(2013, 3, 1, 5)
    # It should be midnight in EST
    print fleming.convert_to_tz(dt, pytz.timezone('US/Eastern'))
    2013-03-01 00:00:00-05:00

    # Do arithmetic on the UTC time with respect to EST.
    dt = fleming.add_timedelta(
        dt, datetime.timedelta(weeks=2), within_tz=pytz.timezone('US/Eastern'))
    # The hour (4) of the returned UTC time is different that the original (5).
    print dt
    2013-03-15 04:00:00+00:00

    # However, the hours in EST still reflect midnight
    print fleming.convert_to_tz(dt, pytz.timezone('US/Eastern'))
    2013-03-15 00:00:00-04:00


### floor(dt, floor, within_tz=None, return_naive=False)
Perform a 'floor' on a datetime, where the floor variable can be: 'year', 'month', 'day', 'hour', 'minute', 'second', or 'week'. This function will round the datetime down to the beginning of the start of the floor.

**Args:**
- dt: A naive or aware datetime object. If it is naive, it is assumed to be UTC.
- floor: The interval to be floored. Can be 'year', 'month', 'week', 'day', 'hour', 'minute', or 'second'.
- within_tz: A pytz timezone object. If given, the floor will be performed with respect to the timezone.
- return_naive: A boolean specifying whether to return the datetime object as naive.

**Returns:**
An aware datetime object that results from flooring dt to floor. The timezone of the returned datetime will be equivalent to the original timezone of dt (or its DST equivalent if a DST border was crossed). If return_naive is True, the returned value has no tzinfo object.

**Raises:**
ValueError if floor is not a valid floor value.

**Examples:**

    import datetime
    import pytz
    import fleming

    # Do basic floors in naive UTC time. Results are UTC aware
    print fleming.floor(datetime.datetime(2013, 3, 3, 5), 'year')
    2013-01-01 00:00:00+00:00

    print fleming.floor(datetime.datetime(2013, 3, 3, 5), 'month')
    2013-03-01 00:00:00+00:00

    # Weeks start on Monday, so the floor will be for the previous Monday
    print fleming.floor(datetime.datetime(2013, 3, 3, 5), 'week')
    2013-02-25 00:00:00+00:00

    print fleming.floor(datetime.datetime(2013, 3, 3, 5), 'day')
    2013-03-03 00:00:00+00:00

    # Use return_naive if you don't want to return aware datetimes
    print fleming.floor(
        datetime.datetime(2013, 3, 3, 5), 'day', return_naive=True)
    2013-03-03 00:00:00

    # Peform a floor in EST. The result is in EST
    dt = fleming.convert_to_tz(
        datetime.datetime(2013, 3, 4, 6), pytz.timezone('US/Eastern'))
    print dt
    2013-03-04 01:00:00-05:00

    print fleming.floor(dt, 'year')
    2013-01-01 00:00:00-05:00

    print fleming.floor(dt, 'day')
    2013-03-04 00:00:00-05:00

    # Now perform a floor that starts out of DST and ends up in DST. The
    # timezones before and after the floor will be different, but the
    # time values are correct
    dt = fleming.convert_to_tz(
        datetime.datetime(2013, 11, 28, 6), pytz.timezone('US/Eastern'))
    print dt
    2013-11-28 01:00:00-05:00

    print fleming.floor(dt, 'month')
    2013-11-01 00:00:00-04:00

    # Start with a naive UTC time and floor it with respect to EST
    dt = datetime.datetime(2013, 2, 1)
    # Since it is January 31 in EST, the resulting floored value
    # for a day will be the previous day. Also, the returned value is
    # in the original timezone of UTC
    print fleming.floor(dt, 'day', within_tz=pytz.timezone('US/Eastern'))
    2013-01-31 00:00:00+00:00

    # Similarly, EST values can be floored relative to CST values.
    dt = fleming.convert_to_tz(
        datetime.datetime(2013, 2, 1, 5), pytz.timezone('US/Eastern'))
    print dt
    2013-02-01 00:00:00-05:00

    # Since it is January 31 in CST, the resulting floored value
    # for a day will be the previous day. Also, the returned value is
    # in the original timezone of EST
    print fleming.floor(dt, 'day', within_tz=pytz.timezone('US/Central'))
    2013-01-31 00:00:00-05:00


### intervals(start_dt, td, within_tz=None, stop_dt=None, is_stop_dt_inclusive=False, count=0, return_naive=False)
Returns a range of datetime objects starting from start_dt and going in increments of timedelta td. If stop_dt is specified, the intervals go to stop_dt (and include stop_dt in the return if is_stop_dt_inclusive=True). If stop_dt is None, the count variable is used to control how many iterations are in the time intervals.

**Args:**
- start_dt: A naive or aware datetime object from which to start the time intervals. If it is naive, it is assumed to be UTC.
- td: A timedelta object describing the time interval in the intervals.
- within_tz: A pytz timezone object. If provided, the intervals will be computed with respect to this timezone.
- stop_dt: A naive or aware datetime object that specifies the end of the intervals. Defaults to being exclusive in the intervals. If naive, it is assumed to be in UTC.
- is_stop_dt_inclusive: True if the stop_dt should be included in the time intervals. Defaults to False.
- count: An integer specifying a count of intervals to use if stop_dt is None.
- return_naive: All datetimes in the intervals are returned as naive objects.

**Returns:**
A generator of datetime objects.

**Examples:**

    import datetime
    import pytz
    import fleming

    # Using a naive UTC time, get intervals of time for every day.
    for dt in fleming.intervals(datetime.datetime(2013, 2, 3), datetime.timedelta(days=1), count=5):
        print dt
    2013-02-03 00:00:00+00:00
    2013-02-04 00:00:00+00:00
    2013-02-05 00:00:00+00:00
    2013-02-06 00:00:00+00:00
    2013-02-07 00:00:00+00:00

    # Use an EST time. Do intervals of a day. Cross the DST time border on March 10th.
    est_dt = fleming.convert_to_tz(datetime.datetime(2013, 3, 9, 5), pytz.timezone('US/Eastern'))
    for dt in fleming.intervals(est_dt, datetime.timedelta(days=1), count=5):
        print dt
    2013-03-09 00:00:00-05:00
    2013-03-10 00:00:00-05:00
    2013-03-11 00:00:00-04:00
    2013-03-12 00:00:00-04:00
    2013-03-13 00:00:00-04:00

    # Similarly, we can iterate through UTC times while doing the date range with respect to EST. Note
    # that the UTC hour changes as the DST border is crossed on March 10th.
    for dt in fleming.intervals(
            datetime.datetime(2013, 3, 9, 5), datetime.timedelta(days=1), within_tz=pytz.timezone('US/Eastern'),
            count=5):
        print dt
    2013-03-09 05:00:00+00:00
    2013-03-10 05:00:00+00:00
    2013-03-11 04:00:00+00:00
    2013-03-12 04:00:00+00:00
    2013-03-13 04:00:00+00:00

    # Use a stop time. Note that the stop time is exclusive
    for dt in fleming.intervals(
            datetime.datetime(2013, 3, 9), datetime.timedelta(weeks=1), stop_dt=datetime.datetime(2013, 3, 23)):
        print dt
    2013-03-09 00:00:00+00:00
    2013-03-16 00:00:00+00:00

    # Make the previous range inclusive
    for dt in fleming.intervals(
            datetime.datetime(2013, 3, 9), datetime.timedelta(weeks=1), stop_dt=datetime.datetime(2013, 3, 23),
            is_stop_dt_inclusive=True):
        print dt
    2013-03-09 00:00:00+00:00
    2013-03-16 00:00:00+00:00
    2013-03-23 00:00:00+00:00

    # Arbitrary timedeltas can be used for any sort of time range
    for dt in fleming.intervals(
            datetime.datetime(2013, 3, 9), datetime.timedelta(days=1, hours=2, minutes=1), count=5):
        print dt
    2013-03-09 00:00:00+00:00
    2013-03-10 02:01:00+00:00
    2013-03-11 04:02:00+00:00
    2013-03-12 06:03:00+00:00
    2013-03-13 08:04:00+00:00


### unix_time(dt, within_tz=None, return_ms=False)
Converts a naive or aware datetime object to unix timestamp. If within_tz is present, the timestamp returned is relative to that time zone.

**Args:**
- dt: A naive or aware datetime object. If it is naive, it is assumed to be UTC.
- within_tz: A pytz timezone object if the user wishes to return the unix time relative to another timezone.
- return_ms: A boolean specifying to return the value in milliseconds since the Unix epoch. Defaults to False.

**Returns:**
An integer timestamp since the Unix epoch. If return_ms is True, returns the timestamp in milliseconds.

**Examples:**

    import datetime
    import pytz
    import fleming

    # Do a basic naive UTC conversion
    dt = datetime.datetime(2013, 4, 2)
    print fleming.unix_time(dt)
    1364860800

    # Convert a time in a different timezone
    dt = fleming.convert_to_tz(
        datetime.datetime(2013, 4, 2, 4), pytz.timezone('US/Eastern'))
    print dt
    2013-04-02 00:00:00-04:00

    print fleming.unix_time(dt)
    1364875200

    # Print millisecond returns
    print fleming.unix_time(dt, return_ms=True)
    1364875200000

    # Do a unix_time conversion with respect to another timezone. When
    # it is converted back to a datetime, the time values are correct.
    # The original timezone, however, needs to be added back
    dt = datetime.datetime(2013, 2, 1, 5)

    # Print its EST time for later reference
    print fleming.convert_to_tz(dt, pytz.timezone('US/Eastern'))
    2013-02-01 00:00:00-05:00

    unix_tz_dt = fleming.unix_time(
        dt, within_tz=pytz.timezone('US/Eastern'))
    print unix_tz_dt
    1359676800

    # The datetime should match the original UTC time converted in
    # the timezone of the within_tz parameter. Tz information is
    # originally lost when converting to unix time, so replace the
    # tzinfo object here
    dt = datetime.datetime.fromtimestamp(unix_tz_dt).replace(
        tzinfo=pytz.timezone('US/Eastern'))
    print dt
    2013-02-01 00:00:00-05:00


### License
MIT License (see LICENSE.md)
