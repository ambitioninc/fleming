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

    For example, let's say we have a UTC time of datetime(2013, 3, 7, 5) (which
    is midnight in EST). Since DST happens at March 10 for EST, any datetime arithmetic
    over 3 days within EST would result in a DST border being crossed. That is, if
    we add two weeks to the UTC datetime, it becomes datetime(2013, 3, 21, 5). This
    time is now 1 AM in EST, a potentially incorrect result depending on the application.

    If you store datetimes as UTC values, but still want to do datetime arithmetic in
    regards to a different timezone, you can use specify the within_tz value to be
    a different timezone. For example,

        add_timedelta(datetime(2013, 3, 21, 5), timedelta(weeks=2),
                      within_tz=timezone('US/Eastern'))

    returns datetime(2013, 3, 21, 4, tzinfo=pytz.utc), which is the proper UTC time for
    EST midnight on 2013, 3, 21.

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
    """
    epoch = datetime.datetime.utcfromtimestamp(0)
    offset = convert_to_tz(dt, within_tz).utcoffset().total_seconds() if within_tz else 0
    # Convert the timezone to UTC for arithmetic and make it naive
    dt = convert_to_tz(dt, pytz.utc).replace(tzinfo=None)
    unix_time = (dt - epoch).total_seconds() + offset
    return int(unix_time * 1000 if return_ms else unix_time)
