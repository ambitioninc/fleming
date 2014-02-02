datetime_helpers
================

This repository contains the datetime_helpers package, which contains a set of routines for doing datetime manipulation. This package is geared towards users that do datetime manipulations with regards to timezones. For example, this package allows a user to perform datetime arithmetic while crossing Daylight Savings Time boundaries. It also provides the ability to floor datetime objects to certain boundaries (such as day, week, month) while also being relative to a local time zone.

The functions in this package are outlined below.


### convert_to_tz(time, timezone)
**convert_to_tz** takes the *time* argument (naive or aware) and converts it to the *timezone* argument (assumed to be a pytz timezone). If *time* is naive, it is assumed to be a UTC time. The returned time is always an aware datetime object with *timezone* as its tzinfo field.

    from datetime_helpers import datetime_helpers
    import datetime
    import pytz
    
    # Convert a naive UTC time to US/Eastern
    t = datetime.datetime(2013, 4, 1)
    est_t = datetime_helpers.convert_to_tz(t, pytz.timezone('US/Eastern'))
    print est_t
    2013-03-31 20:00:00-04:00
    
    # Convert the US/Eastern time to US/Central
    central_t = datetime_helpers.convert_to_tz(est_t, pytz.timezone('US/Central'))
    print central_t
    2013-03-31 19:00:00-05:00
    

### timedelta_tz(time, timezone, timedelta)
**timedelta_tz** takes the *time* argument (assumed to be either a naive or aware UTC time), the *timezone* argument in which to add a time of length *timedelta* (assumed to be a datetime.timedelta argument, although the dateutils package can also be used for relativedeltas). The returned datetime is an aware datetime in UTC.

**timedelta_tz** takes care of datetime arithmetic relative to a timezone and handles the case when crossing a Daylight Savings Time (DST) boundary. For example, let's say that we start at March 1st, 2013 at 5AM UTC (which is midnight in Eastern Standard Time (EST)). In EST, DST is not in effect yet. If one was to add two weeks to that time, it would equal March 15th, 2013 at 5AM UTC. Since DST took effect on March 10th, the resulting time is now at 1 AM in EST - a potentially incorrect result depending on how your code operates. For those that wish to store times in UTC but apply time deltas relative to a different time zone, **timedelta_tz** does the trick.

    est = pytz.timezone('US/Eastern')
    
    # Create a datetime that is in UTC and is midnight in EST
    t = datetime.datetime(2013, 3, 1, 5)
    print datetime_helpers.convert_to_tz(t, est)
    2013-03-01 00:00:00-05:00
    
    t_plus_two_weeks = datetime_helpers.timedelta_tz(t, est, datetime.timedelta(weeks=2))
    print t_plus_two_weeks
    2013-03-15 04:00:00+00:00
    
    # It should still be midnight in the local timezone, except two weeks later
    print datetime_helpers.convert_to_tz(t_plus_two_weeks, est)
    2013-03-15 00:00:00-04:00
    
    
### datetime_floor_tz(time, timezone, floor)
**datetime_floor_tz** takes the *time* argument (assumed to be either a naive or aware UTC time), the *timezone* argument in which to floor the time, and the *floor* type. The *floor* variable can either be year, month, week, day, minute, or second. The returned datetime is an aware datetime in UTC.

Depending on the *floor* argument, **datetime_floor_tz** is going to take all of the attributes less than the length of *floor* and initialize them to their starting values. For example if *floor* is a year, this function is going to set the month equal to January, the day equal to the first, and all other time values equal to zero. The resulting datetime will be at the beginning of the year. Note - when using week as *floor*, it will floor the time to the previous Monday.

The *timezone* parameter is useful when you have a UTC time but want to floor it relative to another timezone. For example, although it might be March 2nd, 2013 at 2 AM in UTC, it is still March 1st in Eastern Standard Time. If *floor* was equal to a day for the example time, it would return March 1st at midnight in UTC time.

    # Do a basic datetime floor in UTC
    t = datetime.datetime(2013, 3, 20, 12)
    print datetime_helpers.datetime_floor_tz(t, pytz.utc, 'month')
    2013-03-01 00:00:00+00:00
    
    print datetime_helpers.datetime_floor_tz(t, pytz.utc, 'day')
    2013-03-20 00:00:00+00:00
    
    # Week will make it go back to the previous Monday
    print datetime_helpers.datetime_floor_tz(t, pytz.utc, 'week')
    2013-03-18 00:00:00+00:00
    
    # Create a datetime object that is March 2nd in UTC, but March 1st in EST
    t = datetime.datetime(2013, 3, 2, 3)
    print datetime_helpers.datetime_floor_tz(t, pytz.timezone('US/Eastern'), 'day')
    2013-03-01 00:00:00+00:00
    
Note - If you don't want to use a timezone in this function, use **datetime_floor(time, floor)**. It returns the floored datetime in its original timezone.  


### unix_time_tz(time, timezone)
**unix_time_tz** takes a *time* argument (assumed to be either a naive or aware UTC time) and a *timezone* argument. This function returns the unix epoch as an integer relative to the timezone. If the unix time is then fed back into the datetime constructor, the datetime object will reflect the time values from that timezone.

    est = pytz.timezone('US/Eastern')
    
    t = datetime.datetime(2013, 3, 1, 9)
    unix_t = datetime_helpers.unix_time_tz(t, est)
    print unix_t
    1362110400
    
    # If you convert the time back and replace the time zone, it
    # will accurately reflect the time within EST
    t = datetime.datetime.fromtimestamp(unix_t).replace(tzinfo=est)
    print t
    2013-03-01 04:00:00-05:00
    
Note - To return milliseconds instead of seconds, use **unix_time_tz_ms(time, timezone)**. Also, if you don't want to use a timezone in this function, use **unix_time(time)** or **unix_time_ms(time)** (for milliseconds).
    
    
