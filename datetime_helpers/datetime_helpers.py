"""
Provides helpers for manipulating datetime objects with respect to time zones.
"""
import datetime

import pytz


def attach_tz_if_none(t, tz):
    """
    Attachs the timezone tz to the time t if it has no timezone.
    """
    return tz.localize(t) if t.tzinfo is None else t


def convert_to_tz(t, tz):
    """
    Given a time t, convert it to time zone convert_tz.
    """
    t = attach_tz_if_none(t, pytz.utc)
    return tz.normalize(t)


def dst_normalize(t, tz):
    """
    Given a local time t, normalize its time zone and return the datetime object with the same year, month, day,
    hours, minutes, and seconds as it previously had before the conversion. This method is used when
    converting a datetime object in a timezone that may have had DST happen to it after arithmetic.

    An example input to this function would be.
    t = 2013/03/11:05:00:00 EST
    Since march 11 overlaps DST, this datetime object is really in EDT. The returned value would be
    t = 2013/03/11:05:00:00 EDT.
    Note that none of its actual time values changes other than its time zone.
    """
    localized_time = convert_to_tz(t, tz)
    return localized_time.replace(
        year=t.year, month=t.month, day=t.day, hour=t.hour, minute=t.minute, second=t.second,
        microsecond=t.microsecond)


def timedelta_tz(t, tz, td):
    """
    Given a time t (assumed to be in UTC), the time zone tz in which to perform the arithmetic, and a
    time delta td, add the time delta in the timezone of tz and return the delta in UTC. This allows time deltas to
    occur across dst transitions.
    """
    # Make sure it is aware in UTC
    t = attach_tz_if_none(t, pytz.utc)
    # Localize it to time_zone
    t = convert_to_tz(t, tz)
    # Add the time delta in the localized time zone
    t += td
    # Normalize the time delta depending on if it crosses a dst transition
    t = dst_normalize(t, tz)
    # Convert it back to UTC and return it
    return convert_to_tz(t, pytz.utc)


def datetime_floor(t, floor):
    """
    Perform a 'floor' on a datetime, where the floor variable can be:
    'year', 'month', 'day', 'hour', 'minute', 'second', or 'week'. This
    function will round the datetime down to the nearest floor.
    """
    if floor == 'year':
        return t.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    elif floor == 'month':
        return t.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif floor == 'day':
        return t.replace(hour=0, minute=0, second=0, microsecond=0)
    elif floor == 'hour':
        return t.replace(minute=0, second=0, microsecond=0)
    elif floor == 'minute':
        return t.replace(second=0, microsecond=0)
    elif floor == 'second':
        return t.replace(microsecond=0)
    elif floor == 'week':
        t = t.replace(hour=0, minute=0, second=0, microsecond=0)
        return t - datetime.timedelta(days=t.weekday())
    else:
        raise ValueError('Invalid value {0} for floor argument'.format(floor))


def datetime_floor_tz(t, tz, floor):
    """
    Floors a utc time in a different time zone. Returns a datetime object in UTC, but
    floored relative to tz.
    """
    return datetime_floor(convert_to_tz(t, tz), floor).replace(tzinfo=pytz.utc)


def unix_time(t):
    """
    Converts a datetime object to unix timestamp assuming utc
    :param dt: A datetime object
    :type dt: datetime.datetime
    :return: :int: unix timestamp in seconds
    """
    epoch = datetime.datetime.utcfromtimestamp(0)
    t = t.replace(tzinfo=None)
    delta = t - epoch
    return int(delta.total_seconds())


def unix_time_ms(t):
    """
    Converts a datetime object to unix timestamp (in milliseconds) assuming utc.
    """
    return unix_time(t) * 1000


def unix_time_tz(t, tz):
    """
    Converts a datetime object to unix timestamp (in seconds) for the given time zone.
    """
    loc_t = convert_to_tz(t, tz)
    return unix_time(t) + int(loc_t.utcoffset().total_seconds())


def unix_time_tz_ms(t, tz):
    """
    Converts a datetime object to unix timestamp (in milliseconds) for the given time zone.
    """
    return unix_time_tz(t, tz) * 1000
