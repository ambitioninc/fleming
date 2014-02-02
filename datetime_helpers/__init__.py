"""
Provides helpers for manipulating datetime objects with respect to time zones.

Authors:
    Wes Kendall (https://github.com/wesleykendall)
    Jeff McRiffey (https://github.com/jmcriffey)
    Josh Marlow (https://github.com/joshmarlow)
"""
import datetime

import pytz


def attach_tz_if_none(dt, tz):
    """Makes a naive timezone aware or returns it if it is already aware.

    Attaches the timezone tz to the datetime dt if dt has no tzinfo. If
    dt already has tzinfo set, return dt.

    Args:
        dt: A naive or aware datetime object.
        tz: A pytz timezone object.

    Returns:
        An aware datetime dt with tzinfo set to tz. If dt already had tzinfo
        set, dt is returned unchanged.
    """
    return tz.localize(dt) if dt.tzinfo is None else dt


def remove_tz_if_return_naive(dt, return_naive):
    """A helper function to strip tzinfo objects if return_naive is True.

    Returns a naive datetime object if return_naive is True.

    Args:
        dt: A datetime object.
        return_naive: A boolean.

    Returns:
        A naive dt if return_naive is True.
    """
    return dt.replace(tzinfo=None) if return_naive else dt


def convert_to_tz(dt, tz, return_naive=False):
    """Converts a time into another timezone.

    Given an aware or naive datetime dt, convert it to the timezone tz.

    Args:
        dt: A naive or aware datetime object. If dt is naive, it has UTC
            set as its timezone.
        tz: A pytz timezone object specifying the timezone to which dt
            should be converted.
        return_naive: A boolean describing whether the return value
            should be a naive datetime object.

    Returns:
        An aware datetime object that was the result of converting dt
        into tz. If return_naive is True, the returned value has no
        tzinfo set.

    Examples:
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
    """
    return remove_tz_if_return_naive(
        tz.normalize(attach_tz_if_none(dt, pytz.utc)), return_naive)


def dst_normalize(dt):
    """Normalizes a datetime that crossed a DST border to its new DST timezone.

    Given an aware datetime object dt, call pytz's normalize function on dt's timezone
    If dt had crossed a DST border because of datetime arithmetic, its timezone will
    be changed to reflect the new DST timezone (for example, going from EST to EDT).
    The original time values from dt remain unchanged.

    An example input to this function would be.
    t = 2013/03/11:05:00:00 EST
    Since march 11 overlaps DST, this datetime object is really in EDT. The returned value would be
    t = 2013/03/11:05:00:00 EDT.

    Args:
        dt: An aware datetime object.

    Returns:
        An aware datetime object that has time value identical to dt. The only possible difference
        is that its timezone might have been converted into a DST timezone.
    """
    return dt.replace(tzinfo=convert_to_tz(dt, dt.tzinfo).tzinfo)


def add_timedelta(dt, td, within_tz=None, return_naive=False):
    """Adds a timedelta to a datetime. Can add timedeltas relative to a timezone.

    Give a naive or aware datetime dt, add a timedelta td to it and return it. If
    within_tz is specified, the datetime arithmetic happens with regard to the timezone.
    Proper measures are used to ensure that datetime arithmetic across a DST border
    is handled properly.

    Args:
        dt: A naive or aware datetime object. If it is naive, it is assumed to be UTC.
        td: A timedelta (or relativedelta) object to add to dt.
        within_tz: A pytz timezone object. If provided, dt will be converted to this
            timezone before datetime arithmetic and then converted back to its original
            timezone afterwards.
        return_naive: A boolean defaulting to False. If True, the result is returned
            as a naive datetime object with tzinfo equal to None.

    Returns:
        An aware datetime object that results from adding td to dt. The timezone of the
        returned datetime will be equivalent to the original timezone of dt (or its DST
        equivalent if a DST border was crossed). If return_naive is True, the returned
        value has no tzinfo object.

    Examples:
        import pytz
        import datetime
        import datetime_helpers

        # Do a basic timedelta addition to a naive UTC time and create an aware UTC time
        # two weeks in the future
        dt = datetime.datetime(2013, 3, 1)
        dt = datetime_helpers.add_timedelta(dt, datetime.timedelta(weeks=2))
        print dt
        2013-03-15 00:00:00+00:00

        # Do addition on an EST datetime where the arithmetic does not cross over DST
        dt = datetime_helpers.convert_to_tz(dt, pytz.timezone('US/Eastern'))
        print dt
        2013-03-14 20:00:00-04:00

        dt = datetime_helpers.add_timedelta(dt, datetime.timedelta(weeks=2, days=1))
        print dt
        2013-03-29 20:00:00-04:00

        # Do timedelta arithmetic such that it starts in DST and crosses over into no DST.
        # Note that the hours stay in tact and the timezone changes
        dt = datetime_helpers.add_timedelta(dt, datetime.timedelta(weeks=-4))
        print dt
        2013-03-01 20:00:00-05:00

        # Take a UTC time and do datetime arithmetic in regards to EST. Do the arithmetic
        # such that a DST border is crossed
        dt = datetime.datetime(2013, 3, 1, 5)
        # It should be midnight in EST
        print datetime_helpers.convert_to_tz(dt, pytz.timezone('US/Eastern'))
        2013-03-01 00:00:00-05:00

        # Do arithmetic on the UTC time with respect to EST.
        dt = datetime_helpers.add_timedelta(
            dt, datetime.timedelta(weeks=2), within_tz=pytz.timezone('US/Eastern'))
        # The hour (4) of the returned UTC time is different that the original (5).
        print dt
        2013-03-15 04:00:00+00:00

        However, the hours in EST still reflect midnight
        print datetime_helpers.convert_to_tz(dt, pytz.timezone('US/Eastern'))
        2013-03-15 00:00:00-04:00
    """
    # Make sure it is aware
    dt = attach_tz_if_none(dt, pytz.utc)
    # Localize it to time_zone if within_tz is specified
    loc_dt = convert_to_tz(dt, within_tz) if within_tz else dt
    # Add the time delta in the localized time zone, taking care of any DST border crossings
    loc_dt = dst_normalize(loc_dt + td)
    # Convert it back to the original timezone if within_tz was specified
    loc_dt = convert_to_tz(loc_dt, dt.tzinfo) if within_tz else loc_dt
    # Return it, stripping the timezone information if return_naive
    return remove_tz_if_return_naive(loc_dt, return_naive)


def floor(dt, floor, within_tz=None, return_naive=False):
    """Floors a datetime to the nearest time boundary.

    Perform a 'floor' on a datetime, where the floor variable can be:
    'year', 'month', 'day', 'hour', 'minute', 'second', or 'week'. This
    function will round the datetime down to the beginning of the start
    of the floor.

    Args:
        dt: A naive or aware datetime object. If it is naive, it is
            assumed to be UTC
        floor: The interval to be floored. Can be 'year', 'month',
            'week', 'day', 'hour', 'minute', or 'second'.
        within_tz: A pytz timezone object. If given, the floor will
            be performed with respect to the timezone.
        return_naive: A boolean specifying whether to return the
            datetime object as naive.

    Returns:
        An aware datetime object that results from flooring dt to floor. The timezone of the
        returned datetime will be equivalent to the original timezone of dt (or its DST
        equivalent if a DST border was crossed). If return_naive is True, the returned
        value has no tzinfo object.

    Raises:
        ValueError if floor is not a valid floor value.

    Examples:
        import datetime
        import pytz
        import datetime_helpers

        # Do basic floors in naive UTC time. Results are UTC aware
        print datetime_helpers.floor(datetime.datetime(2013, 3, 3, 5), 'year')
        2013-01-01 00:00:00+00:00

        print datetime_helpers.floor(datetime.datetime(2013, 3, 3, 5), 'month')
        2013-03-01 00:00:00+00:00

        # Weeks start on Monday, so the floor will be for the previous Monday
        print datetime_helpers.floor(datetime.datetime(2013, 3, 3, 5), 'week')
        2013-02-25 00:00:00+00:00

        print datetime_helpers.floor(datetime.datetime(2013, 3, 3, 5), 'day')
        2013-03-03 00:00:00+00:00

        # Use return_naive if you don't want to return aware datetimes
        print datetime_helpers.floor(
            datetime.datetime(2013, 3, 3, 5), 'day', return_naive=True)
        2013-03-03 00:00:00

        # Peform a floor in EST. The result is in EST
        dt = datetime_helpers.convert_to_tz(
            datetime.datetime(2013, 3, 4, 6), pytz.timezone('US/Eastern'))
        print dt
        2013-03-04 01:00:00-05:00

        print datetime_helpers.floor(dt, 'year')
        2013-01-01 00:00:00-05:00

        print datetime_helpers.floor(dt, 'day')
        2013-03-04 00:00:00-05:00

        # Now perform a floor that starts out of DST and ends up in DST. The
        # timezones before and after the floor will be different, but the
        # time values are correct
        dt = datetime_helpers.convert_to_tz(
            datetime.datetime(2013, 11, 28, 6), pytz.timezone('US/Eastern'))
        print dt
        2013-11-28 01:00:00-05:00

        print datetime_helpers.floor(dt, 'month')
        2013-11-01 00:00:00-04:00

        # Start with a naive UTC time and floor it with respect to EST
        dt = datetime.datetime(2013, 2, 1)
        # Since it is January 31 in EST, the resulting floored value
        # for a day will be the previous day. Also, the returned value is
        # in the original timezone of UTC
        print datetime_helpers.floor(dt, 'day', within_tz=pytz.timezone('US/Eastern'))
        2013-01-31 00:00:00+00:00

        # Similarly, EST values can be floored relative to CST values.
        dt = datetime_helpers.convert_to_tz(
            datetime.datetime(2013, 2, 1, 5), pytz.timezone('US/Eastern'))
        print dt
        2013-02-01 00:00:00-05:00

        # Since it is January 31 in CST, the resulting floored value
        # for a day will be the previous day. Also, the returned value is
        # in the original timezone of EST
        print datetime_helpers.floor(dt, 'day', within_tz=pytz.timezone('US/Central'))
        2013-01-31 00:00:00-05:00
    """
    # Make sure it is aware
    dt = attach_tz_if_none(dt, pytz.utc)
    # Localize it to time_zone if within_tz is specified
    loc_dt = convert_to_tz(dt, within_tz) if within_tz else dt

    # Floor the local time to its proper interval
    if floor == 'year':
        loc_dt = loc_dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    elif floor == 'month':
        loc_dt = loc_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif floor == 'day':
        loc_dt = loc_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    elif floor == 'hour':
        loc_dt = loc_dt.replace(minute=0, second=0, microsecond=0)
    elif floor == 'minute':
        loc_dt = loc_dt.replace(second=0, microsecond=0)
    elif floor == 'second':
        loc_dt = loc_dt.replace(microsecond=0)
    elif floor == 'week':
        # Floor a week to a day and then do proper arithmetic to get to the beginning of week
        loc_dt = loc_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        loc_dt -= datetime.timedelta(days=loc_dt.weekday())
    else:
        raise ValueError('{0} is not a valid floor value'.format(floor))

    # Set the timezone back to that of the original time. Do a DST normalization in case any
    # DST boundaries were crossed
    loc_dt = dst_normalize(loc_dt.replace(tzinfo=dt.tzinfo))

    # Return it, stripping the timezone information if return_naive
    return remove_tz_if_return_naive(loc_dt, return_naive)


def unix_time(dt, within_tz=None, return_ms=False):
    """Converts a datetime object to a unix timestamp.

    Converts a naive or aware datetime object to unix timestamp. If within_tz
    is present, the timestamp returned is relative to that time zone.

    Args:
        dt: A naive or aware datetime object. If it is naive,
            it is assumed to be UTC.
        within_tz: A pytz timezone object if the user wishes to
            return the unix time relative to another timezone.
        return_ms: A boolean specifying to return the value
            in milliseconds since the Unix epoch. Defaults to False.

    Returns:
        An integer timestamp since the Unix epoch. If return_ms is
        True, returns the timestamp in milliseconds.

    Examples:
        import datetime
        import pytz
        import datetime_helpers

        # Do a basic naive UTC conversion
        dt = datetime.datetime(2013, 4, 2)
        print datetime_helpers.unix_time(dt)
        1364860800

        # Convert a time in a different timezone
        dt = datetime_helpers.convert_to_tz(
            datetime.datetime(2013, 4, 2, 4), pytz.timezone('US/Eastern'))
        print dt
        2013-04-02 00:00:00-04:00

        print datetime_helpers.unix_time(dt)
        1364875200

        # Print millisecond returns
        print datetime_helpers.unix_time(dt, return_ms=True)
        1364875200000

        # Do a unix_time conversion with respect to another timezone. When
        # it is converted back to a datetime, the time values are correct.
        # The original timezone, however, needs to be added back
        dt = datetime.datetime(2013, 2, 1, 5)

        # Print its EST time for later reference
        print datetime_helpers.convert_to_tz(dt, pytz.timezone('US/Eastern'))
        2013-02-01 00:00:00-05:00

        unix_tz_dt = datetime_helpers.unix_time(
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
    """
    epoch = datetime.datetime.utcfromtimestamp(0)
    offset = convert_to_tz(dt, within_tz).utcoffset().total_seconds() if within_tz else 0
    # Convert the timezone to UTC for arithmetic and make it naive
    dt = convert_to_tz(dt, pytz.utc).replace(tzinfo=None)
    unix_time = (dt - epoch).total_seconds() + offset
    return int(unix_time * 1000 if return_ms else unix_time)
