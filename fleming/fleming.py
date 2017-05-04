"""
Provides helpers for manipulating datetime objects with respect to time zones.

Authors:
    * Wes Kendall (https://github.com/wesleykendall)
    * Jeff McRiffey (https://github.com/jmcriffey)
    * Josh Marlow (https://github.com/joshmarlow)
"""
import datetime

from dateutil.relativedelta import relativedelta
import pytz


def convert_d_to_dt(dt):
    """
    Converts a date object to a datetime object.

    :type dt: date
    :param dt: The date to convert

    :rtype: datetime
    """
    if type(dt) is datetime.date:
        return datetime.datetime.combine(dt, datetime.datetime.min.time())
    else:
        return dt


def convert_return_back_to_d(dt, original_input):
    """
    Given the original input of a function and the datetime object it produced,
    convert it back to a date object if the original input was a date object.
    """
    if type(original_input) is datetime.date:
        return dt.date()
    else:
        return dt


def attach_tz_if_none(dt, tz):
    """
    Makes a naive timezone aware or returns it if it is already aware.

    Attaches the timezone tz to the datetime dt if dt has no tzinfo. If
    dt already has tzinfo set, return dt.

    :type dt: datetime
    :param dt: A naive or aware datetime object.

    :type tz: pytz timezone
    :param tz: The timezone to add to the datetime

    :rtype: datetime
    :returns: An aware datetime dt with tzinfo set to tz. If dt already had
        tzinfo set, dt is returned unchanged.
    """
    return tz.localize(dt) if dt.tzinfo is None else dt


def remove_tz_if_return_naive(dt, return_naive):
    """
    A helper function to strip tzinfo objects if return_naive is True.

    Returns a naive datetime object if return_naive is True.

    :type dt: datetime
    :param dt: The datetime

    :type return_naive: bool
    :param return_naive: Make datetime naive if True

    :rtype: datetime
    :returns: A naive dt if return_naive is True.
    """
    return dt.replace(tzinfo=None) if return_naive else dt


def convert_to_tz(dt, tz, return_naive=False):
    """
    Converts a time into another timezone.

    Given an aware or naive datetime dt, convert it to the timezone tz.

    :type dt: datetime
    :param dt: A naive or aware datetime object. If dt is naive, it has UTC
        set as its timezone.

    :type tz: pytz timezone
    :param tz: A pytz timezone object specifying the timezone to which dt
        should be converted.

    :type return_naive: bool
    :param return_naive: A boolean describing whether the return value
        should be a naive datetime object.

    :rtype: datetime
    :returns: An aware datetime object that was the result of converting dt
        into tz. If return_naive is True, the returned value has no
        tzinfo set.

    .. code-block:: python

        >>> import fleming
        >>> import datetime
        >>> import pytz

        >>> dt = datetime.datetime(2013, 2, 4)
        >>> print dt
        2013-02-04 00:00:00

        >>> # Convert naive UTC time to aware EST time
        >>> dt = fleming.convert_to_tz(dt, pytz.timezone('US/Eastern'))
        >>> print dt
        2013-02-03 19:00:00-05:00

        >>> # Convert aware EST time to aware CST time
        >>> dt = fleming.convert_to_tz(dt, pytz.timezone('US/Central'))
        >>> print dt
        2013-02-03 18:00:00-06:00

        >>> # Convert aware CST time back to naive UTC time
        >>> dt = fleming.convert_to_tz(dt, pytz.utc, return_naive=True)
        >>> print dt
        2013-02-04 00:00:00

    """
    return remove_tz_if_return_naive(
        tz.normalize(attach_tz_if_none(dt, pytz.utc)), return_naive)


def dst_normalize(dt):
    """
    Normalizes a datetime that crossed a DST border to its new DST timezone.

    Given an aware datetime object dt, call pytz's normalize function on dt's timezone
    If dt had crossed a DST border because of datetime arithmetic, its timezone will
    be changed to reflect the new DST timezone (for example, going from EST to EDT).
    The original time values from dt remain unchanged.

    An example input to this function would be.
    t = 2013/03/11:05:00:00 EST
    Since march 11 overlaps DST, this datetime object is really in EDT. The returned value would be
    t = 2013/03/11:05:00:00 EDT.

    :type dt: datetime
    :param dt: The aware datetime object.

    :rtype: datetime
    :returns: An aware datetime object that has time value identical to dt. The
        only possible difference is that its timezone might have been converted
        into a DST timezone.
    """
    return dt.replace(tzinfo=convert_to_tz(dt, dt.tzinfo).tzinfo)


def add_timedelta(dt, td, within_tz=None):
    """
    Adds a timedelta to a datetime. Can add timedeltas relative to a timezone.

    Given a naive or aware datetime dt, add a timedelta td to it and return it.
    If within_tz is specified, the datetime arithmetic happens with regard to
    the timezone. Proper measures are used to ensure that datetime arithmetic
    across a DST border is handled properly.

    :type dt: datetime
    :param dt: A naive or aware datetime object. If it is naive, it is assumed
        to be UTC.

    :type td: timedelta
    :param td: A timedelta (or relativedelta) object to add to dt.

    :type within_tz: pytz timezone
    :param within_tz: A pytz timezone object. If provided, dt will be converted
        to this timezone before datetime arithmetic and then converted back to
        its original timezone afterwards.

    :rtype: datetime
    :returns: A datetime object that results from adding td to dt. The timezone
        of the returned datetime will be equivalent to the original timezone of
        dt (or its DST equivalent if a DST border was crossed). If the original
        time was naive, the returned value is naive.

    .. code-block:: python

        >>> import pytz
        >>> import datetime
        >>> import fleming

        >>> # Do a basic timedelta addition to a naive UTC time and create a naive UTC time
        >>> # two weeks in the future
        >>> dt = datetime.datetime(2013, 3, 1)
        >>> dt = fleming.add_timedelta(dt, datetime.timedelta(weeks=2))
        >>> print dt
        2013-03-15 00:00:00

        >>> # Do addition on an EST datetime where the arithmetic does not cross over DST
        >>> dt = fleming.convert_to_tz(dt, pytz.timezone('US/Eastern'))
        >>> print dt
        2013-03-14 20:00:00-04:00

        >>> dt = fleming.add_timedelta(dt, datetime.timedelta(weeks=2, days=1))
        >>> print dt
        2013-03-29 20:00:00-04:00

        >>> # Do timedelta arithmetic such that it starts in DST and crosses over into no DST.
        >>> # Note that the hours stay in tact and the timezone changes
        >>> dt = fleming.add_timedelta(dt, datetime.timedelta(weeks=-4))
        >>> print dt
        2013-03-01 20:00:00-05:00

        >>> # Take an aware UTC time and do datetime arithmetic in regards to EST. Do the arithmetic
        >>> # such that a DST border is crossed
        >>> dt = datetime.datetime(2013, 3, 1, 5, tzinfo=pytz.utc)
        >>> # It should be midnight in EST
        >>> print fleming.convert_to_tz(dt, pytz.timezone('US/Eastern'))
        2013-03-01 00:00:00-05:00

        >>> # Do arithmetic on the UTC time with respect to EST.
        >>> dt = fleming.add_timedelta(
        ...     dt, datetime.timedelta(weeks=2), within_tz=pytz.timezone('US/Eastern')
        ... )
        ...
        >>> # The hour (4) of the returned UTC time is different that the original (5).
        >>> print dt
        2013-03-15 04:00:00+00:00

        >>> # However, the hours in EST still reflect midnight
        >>> print fleming.convert_to_tz(dt, pytz.timezone('US/Eastern'))
        2013-03-15 00:00:00-04:00

    """
    c_dt = convert_d_to_dt(dt)

    # Return a naive datetime object if the input is naive
    return_naive = c_dt.tzinfo is None
    # Make sure it is aware
    c_dt = attach_tz_if_none(c_dt, pytz.utc)
    # Localize it to time_zone if within_tz is specified
    loc_dt = convert_to_tz(c_dt, within_tz) if within_tz else c_dt
    # Add the time delta in the localized time zone, taking care of any DST border crossings
    loc_dt = dst_normalize(loc_dt + td)
    # Convert it back to the original timezone if within_tz was specified
    loc_dt = convert_to_tz(loc_dt, c_dt.tzinfo) if within_tz else loc_dt
    # Return it, stripping the timezone information if return_naive
    return convert_return_back_to_d(remove_tz_if_return_naive(loc_dt, return_naive), dt)


def floor(
        dt, within_tz=None, year=None, month=None, week=None, day=None, hour=None, minute=None,
        second=None, microsecond=None, extra_td_if_floor=None):
    """
    Floors a datetime to the nearest time boundary.

    Perform a floor on a datetime, rounding the datetime to its nearest provided interval.
    Available intervals are year, month, week, day, hour, minute, second, and microsecond.

    For example, to round to the nearest month, provide month=1 as input. Give a value
    like 3 to the month argument and it will round to the nearest trimonth in a year
    (i.e. the nearest quarter). Values for other intervals operate in the same way, such
    as rounding down to the nearest day in a month (or nearest triday).

    The only paramter to this function which is not like the others is the week parameter.
    The week parameter rounds the time down to its nearest Monday. In contrast to other
    intervals, week can only be 1 since it has no larger time interval from which to
    start a tri or quadweek for example.

    Also, if the week parameter is provided, the year and month arguments are also
    not used in the floor calculation.

    Note that multiple combinations of attributes can be used where they make sense,
    such as flooring to the nearest trimonth and triday (month=3, day=3).

    :type dt: datetime
    :param dt: A naive or aware datetime object. If it is naive, it is
        assumed to be UTC

    :type within_tz: pytz timezone
    :param within_tz: A pytz timezone object. If given, the floor will
        be performed with respect to the timezone.

    :type year: int
    :param year: Specifies the yearly interval to round down to. Defaults to None.

    :type month: int
    :param month: Specifies the monthly interval (inside of a year) to round
        down to. Defaults to None.

    :type week: int
    :param week: Specifies to round to the beginning of the previous week.
        Defaults to None and only accepts a possible value of 1.

    :type day: int
    :param day: Specifies the daily interval to round down to (inside of a
        month). Defaults to None.

    :type hour: int
    :param hour: Specifies the hourly interval to round down to (inside of a
        day). Defaults to None.

    :type minute: int
    :param minute: Specifies the minute interval to round down to (inside of an
        hour). Defaults to None.

    :type second: int
    :param second: Specifies the second interval to round down to (inside of a
        minute). Defaults to None.

    :type microsecond: int
    :param microsecond: Specifies the microsecond interval to round down to
        (inside of a second). Defaults to None.

    :type extra_td_if_floor: timedelta
    :param extra_td_if_floor: Only used by the ceil function. Specifies an
        extra timedelta to be added to the result if a floor has occurred.

    :rtype: datetime
    :returns: A datetime object that results from flooring dt to the interval.
        The timezone of the returned datetime will be equivalent to the
        original timezone of dt (or its DST equivalent if a DST border was
        crossed). If the input time was naive, it returns a naive datetime
        object.

    :raises: ValueError if the interval is an invalid value.

    .. code-block:: python

        >>> import datetime
        >>> import pytz
        >>> import fleming

        >>> # Do basic floors in naive UTC time. Results are naive UTC.
        >>> print fleming.floor(datetime.datetime(2013, 3, 3, 5), year=1)
        2013-01-01 00:00:00

        >>> print fleming.floor(datetime.datetime(2013, 3, 3, 5), month=1)
        2013-03-01 00:00:00

        >>> # Weeks start on Monday, so the floor will be for the previous Monday
        >>> print fleming.floor(datetime.datetime(2013, 3, 3, 5), week=1)
        2013-02-25 00:00:00

        >>> print fleming.floor(datetime.datetime(2013, 3, 3, 5), day=1)
        2013-03-03 00:00:00

        >>> # Pass an aware datetime and return an aware datetime
        >>> print fleming.floor(
        ...     datetime.datetime(2013, 3, 3, 5, tzinfo=pytz.utc), day=1)
        2013-03-03 00:00:00+00:00

        >>> # Perform a floor in EST. The result is in EST
        >>> dt = fleming.convert_to_tz(
        ...    datetime.datetime(2013, 3, 4, 6), pytz.timezone('US/Eastern'))
        >>> print dt
        2013-03-04 01:00:00-05:00

        >>> print fleming.floor(dt, year=1)
        2013-01-01 00:00:00-05:00

        >>> print fleming.floor(dt, day=1)
        2013-03-04 00:00:00-05:00

        >>> # Now perform a floor that starts out of DST and ends up in DST. The
        >>> # timezones before and after the floor will be different, but the
        >>> # time values are correct
        >>> dt = fleming.convert_to_tz(
        ...    datetime.datetime(2013, 11, 28, 6), pytz.timezone('US/Eastern'))
        ...
        >>> print dt
        2013-11-28 01:00:00-05:00

        >>> print fleming.floor(dt, month=1)
        2013-11-01 00:00:00-04:00

        >>> # Start with a naive UTC time and floor it with respect to EST
        >>> dt = datetime.datetime(2013, 2, 1)
        >>> # Since it is January 31 in EST, the resulting floored value
        >>> # for a day will be the previous day. Also, the returned value is
        >>> # in the original naive timezone of UTC
        >>> print fleming.floor(dt, day=1, within_tz=pytz.timezone('US/Eastern'))
        2013-01-31 00:00:00

        >>> # Similarly, EST values can be floored relative to CST values.
        >>> dt = fleming.convert_to_tz(
        ...    datetime.datetime(2013, 2, 1, 5), pytz.timezone('US/Eastern'))
        >>> print dt
        2013-02-01 00:00:00-05:00

        >>> # Since it is January 31 in CST, the resulting floored value
        >>> # for a day will be the previous day. Also, the returned value is
        >>> # in the original timezone of EST
        >>> print fleming.floor(dt, day=1, within_tz=pytz.timezone('US/Central'))
        2013-01-31 00:00:00-05:00

        >>> # Get the starting of a quarter by using month=3
        >>> print fleming.floor(datetime.datetime(2013, 2, 4), month=3)
        2013-01-01 00:00:00

    """
    # Create a mapping of interval arguments
    interval_value_map = {
        'year': year,
        'month': month,
        'week': week,
        'day': day,
        'hour': hour,
        'minute': minute,
        'second': second,
        'microsecond': microsecond
    }

    # transform any input date objects to datetime objects
    c_dt = convert_d_to_dt(dt)

    # Return naive datetimes if the input is naive
    return_naive = c_dt.tzinfo is None

    # Make sure it is aware
    c_dt = attach_tz_if_none(c_dt, pytz.utc)

    # Localize it to time_zone if within_tz is specified
    loc_dt = convert_to_tz(c_dt, within_tz) if within_tz else c_dt

    # Keep a copy of the original value for later use
    orig_dt = loc_dt

    # Make a mapping of intervals to their starting value. Some intervals start at 1 (such as day and month)
    # for datetime objects.
    interval_starts = (
        ('year', 0), ('month', 1), ('day', 1), ('hour', 0), ('minute', 0), ('second', 0), ('microsecond', 0)
    )

    # Initialize the index of the biggest_interval from which to start the floor
    biggest_interval_i = 0

    # Marks if a non-None floor has been seen
    floor_seen = False

    # Week is a special case for our function, and floor only supports doing intervals of 1 for a week.
    # Check for this and do the weekly part of the floor here before doing any residual smaller time
    # intervals
    if week is not None:
        # The biggest interval from which to start the floor becomes an hour
        biggest_interval_i = 3
        # Even though we haven't started our main floor loop, a non-None floor value ('week') has been seen
        floor_seen = True
        if week != 1:
            raise ValueError('week argument can only be 1 or None')
        else:
            # Make the time be the starting of a week (Monday)
            loc_dt -= datetime.timedelta(days=loc_dt.weekday())

    # initialize a dict to hold new time state
    new_kwargs = dict(
        year=loc_dt.year,
        month=loc_dt.month,
        day=loc_dt.day,
        hour=loc_dt.hour,
        minute=loc_dt.minute,
        second=loc_dt.second,
        microsecond=loc_dt.microsecond,
    )

    # Starting at the largest time interval, do the following:
    # - if a non-None floor value has not been seen and the floor value is None, populate the result
    #   time with the value from the input
    # - if a non-None floor value is found, do modulus arithmetic to find out its resulting value.
    # - if a non-None floor has been seen and the floor valye is None, populate the result with the
    #   first time for an floor interval
    for interval, start in interval_starts[biggest_interval_i:]:
        if interval_value_map[interval] is None and floor_seen:
            new_kwargs[interval] = start
        elif interval_value_map[interval] is not None:
            floor_seen = True
            interval_val = new_kwargs[interval]
            new_kwargs[interval] = interval_val - ((interval_val - start) % interval_value_map[interval])

    # transfer time state to datetime object
    loc_dt = loc_dt.replace(**new_kwargs)

    # Add any additional deltas within the proper timezone. This is currently only used by the ceil
    # function and is not user facing. Only add the extra td if the floored result is different than
    # the original.
    if extra_td_if_floor is not None and orig_dt != loc_dt:
        loc_dt += extra_td_if_floor

    # Set the timezone back to that of the original time. Do a DST normalization in case any
    # DST boundaries were crossed
    loc_dt = dst_normalize(loc_dt.replace(tzinfo=c_dt.tzinfo))

    # Return it, stripping the timezone information if return_naive
    return convert_return_back_to_d(remove_tz_if_return_naive(loc_dt, return_naive), dt)


def ceil(
        dt, within_tz=None, year=None, month=None, week=None, day=None, hour=None, minute=None,
        second=None, microsecond=None):
    """
    Ceils a datetime to the nearest (above) time interval.

    Perform a ceil on a datetime to the next closest interval in the future. For example,
    if month=1, this function will round up the time to the next month in the future.
    Larger numbers can be used, such as month=3, to round up to the beginning of the next
    quarter.

    Note that this function allows combinations of interval variables (such as month=2 and day=2
    to round up to the next duomonth of the year and next duoday of the month), but the smaller intervals are always
    not important since they will always be at the beginning of the larger interval.

    :type dt: datetime
    :param dt: A naive or aware datetime object. If it is naive, it is assumed
        to be UTC

    :type within_tz: pytz timezone
    :param within_tz: A pytz timezone object. If given, the ceil will be
        performed with respect to the timezone.

    :type year: int
    :param year: Specifies the yearly interval to round up to. Defaults to None.

    :type month: int
    :param month: Specifies the monthly interval (inside of a year) to round up
        to. Defaults to None.

    :type week: int
    :param week: Specifies to round up to the beginning of the next week.
        Defaults to None and only accepts a possible value of 1.

    :type day: int
    :param day: Specifies the daily interval to round up to (inside of a
        month). Defaults to None.

    :type hour: int
    :param hour: Specifies the hourly interval to round up to (inside of a
        day). Defaults to None.

    :type minute: int
    :param minute: Specifies the minute interval to round up to (inside of an
        hour). Defaults to None.

    :type second: int
    :param second: Specifies the second interval to round up to (inside of a
        minute). Defaults to None.

    :type microsecond: int
    :param microsecond: Specfies the microsecond interval to round up to
        (inside of a second). Defaults to None.

    :returns: A datetime object that results from ceiling dt to the next
        interval. The timezone of the returned datetime will be equivalent to
        the original timezone of dt (or its DST equivalent if a DST border was
        crossed). If the original datetime object was naive, the returned
        object is naive.

    :raises: ValueError if the interval is not a valid value.

    .. code-block:: python

        >>> import datetime
        >>> import pytz
        >>> import fleming

        >>> # Do basic ceils in naive UTC time. Results are naive UTC
        >>> print fleming.ceil(datetime.datetime(2013, 3, 3, 5), year=1)
        2014-01-01 00:00:00

        >>> print fleming.ceil(datetime.datetime(2013, 3, 3, 5), month=1)
        2013-04-01 00:00:00

        >>> # Weeks start on Monday, so the floor will be for the next Monday
        >>> print fleming.ceil(datetime.datetime(2013, 3, 3, 5), week=1)
        2013-03-04 00:00:00

        >>> print fleming.ceil(datetime.datetime(2013, 3, 3, 5), day=1)
        2013-03-04 00:00:00

        >>> # Use aware datetimes to return aware datetimes
        >>> print fleming.ceil(
        ...    datetime.datetime(2013, 3, 3, 5, tzinfo=pytz.utc), day=1)
        2013-03-04 00:00:00+00:00

        >>> # Peform a ceil in CST. The result is in Pacfic time
        >>> dt = fleming.convert_to_tz(
        ...    datetime.datetime(2013, 3, 4, 7), pytz.timezone('US/Pacific'))
        >>> print dt
        2013-03-03 23:00:00-08:00

        >>> print fleming.ceil(dt, year=1)
        2014-01-01 00:00:00-08:00

        >>> print fleming.ceil(dt, day=1)
        2013-03-04 00:00:00-08:00

        >>> # Do a ceil with respect to EST. Since it is March 4 in EST, the
        >>> # returned value is March 5 in Pacific time
        >>> print fleming.ceil(dt, day=1, within_tz=pytz.timezone('US/Eastern'))
        2013-03-05 00:00:00-08:00

        >>> # Note that doing a ceiling on a time that is already on the boundary
        >>> # returns the original time
        >>> print fleming.ceil(datetime.datetime(2013, 4, 1), month=1)
        2013-04-01 00:00:00

    """
    c_dt = convert_d_to_dt(dt)

    # Return a naive time if the input was naive
    return_naive = c_dt.tzinfo is None
    # Make sure it is aware
    c_dt = attach_tz_if_none(c_dt, pytz.utc)

    # Get the largest interval provided
    intervals = ('year', 'month', 'week', 'day', 'hour', 'minute', 'second', 'microsecond')
    largest_interval = None
    for interval in intervals:
        if locals()[interval] is not None:
            largest_interval = interval
            break

    if largest_interval is not None:
        # Make a timedelta for the beginning of the next interval and add it when flooring
        td = relativedelta(**{'{0}s'.format(largest_interval): locals()[largest_interval]})
        # Floor to the largest interval while adding the additional next largest interval
        c_dt = floor(c_dt, within_tz=within_tz, extra_td_if_floor=td, **{largest_interval: locals()[largest_interval]})

    # Return it, stripping the timezone information if return_naive
    return convert_return_back_to_d(remove_tz_if_return_naive(c_dt, return_naive), dt)


def intervals(
        start_dt, td, within_tz=None, stop_dt=None, is_stop_dt_inclusive=False, count=None):
    """
    Returns a range of datetime objects with a timedelta interval.

    Returns a range of datetime objects starting from start_dt and going in increments of
    timedelta td. If stop_dt is specified, the intervals go to stop_dt (and include
    stop_dt in the return if is_stop_dt_inclusive=True). If stop_dt is None, the
    count variable is used to control how many iterations are in the time intervals.  If
    stop_dt is None and count is None, a generator will be returned that can yield any
    number of datetime objects.

    :type start_dt: datetime
    :param start_dt: A naive or aware datetime object from which to start the
        time intervals. If it is naive, it is assumed to be UTC.

    :type td: timedelta
    :param td: A timedelta object describing the time interval in the intervals.

    :type within_tz: pytz timezone
    :param within_tz: A pytz timezone object. If provided, the intervals will
        be computed with respect to this timezone.

    :type stop_dt: datetime
    :param stop_dt: A naive or aware datetime object that specifies the end of
        the intervals. Defaults to being exclusive in the intervals. If naive,
        it is assumed to be in UTC.

    :type is_stop_dt_inclusive: bool
    :param is_stop_dt_inclusive: True if the stop_dt should be included in the
        time intervals. Defaults to False.

    :type count: int
    :param count: If set, an integer specifying a count of intervals to use if
        stop_dt is None.

        If stop_dt is None and count is None, a generator will be returned that
        can yield any number of datetime objects.

    :returns: A generator of datetime objects. The datetime objects are in the
        original timezone of the start_dt (or its DST equivalent if a border
        is crossed). If the input is naive, the returned intervals are naive.

    .. code-block:: python

        >>> import datetime
        >>> import pytz
        >>> import fleming

        >>> # Using a naive UTC time, get intervals of time for every day.
        >>> for dt in fleming.intervals(datetime.datetime(2013, 2, 3), datetime.timedelta(days=1), count=5):
        ...     print dt
        2013-02-03 00:00:00
        2013-02-04 00:00:00
        2013-02-05 00:00:00
        2013-02-06 00:00:00
        2013-02-07 00:00:00

        >>> # Use an EST time. Do intervals of a day. Cross the DST time border on March 10th.
        >>> est_dt = fleming.convert_to_tz(datetime.datetime(2013, 3, 9, 5), pytz.timezone('US/Eastern'))
        >>> for dt in fleming.intervals(est_dt, datetime.timedelta(days=1), count=5):
        ...     print dt
        2013-03-09 00:00:00-05:00
        2013-03-10 00:00:00-05:00
        2013-03-11 00:00:00-04:00
        2013-03-12 00:00:00-04:00
        2013-03-13 00:00:00-04:00

        >>> # Similarly, we can iterate through UTC times while doing the date range with respect to EST. Note
        >>> # that the UTC hour changes as the DST border is crossed on March 10th.
        >>> for dt in fleming.intervals(
        ...        datetime.datetime(2013, 3, 9, 5),
        ...        datetime.timedelta(days=1),
        ...        within_tz=pytz.timezone('US/Eastern'),
        ...        count=5):
        ...     print dt
        2013-03-09 05:00:00
        2013-03-10 05:00:00
        2013-03-11 04:00:00
        2013-03-12 04:00:00
        2013-03-13 04:00:00

        >>> # If we don't specify a count or stop time, we can iterate indefinitely.
        >>> for dt in fleming.intervals(datetime.datetime(2013, 1, 1), datetime.timedelta(days=1)):
        ...    print dt
        2013-01-01 00:00:00
        2013-01-02 00:00:00
        2013-01-03 00:00:00
        ....
        2013-05-05 00:00:00
        ....
        to the end of time...

        >>> # Use a stop time. Note that the stop time is exclusive
        >>> for dt in fleming.intervals(
        ...        datetime.datetime(2013, 3, 9),
        ...        datetime.timedelta(weeks=1),
        ...        stop_dt=datetime.datetime(2013, 3, 23)):
        ...    print dt
        2013-03-09 00:00:00
        2013-03-16 00:00:00

        >>> # Make the previous range inclusive
        >>> for dt in fleming.intervals(
        ...        datetime.datetime(2013, 3, 9), datetime.timedelta(weeks=1), stop_dt=datetime.datetime(2013, 3, 23),
        ...        is_stop_dt_inclusive=True):
        ...    print dt
        2013-03-09 00:00:00
        2013-03-16 00:00:00
        2013-03-23 00:00:00

        >>> # Arbitrary timedeltas can be used for any sort of time range
        >>> for dt in fleming.intervals(
        ...        datetime.datetime(2013, 3, 9), datetime.timedelta(days=1, hours=2, minutes=1), count=5):
        ...    print dt
        2013-03-09 00:00:00
        2013-03-10 02:01:00
        2013-03-11 04:02:00
        2013-03-12 06:03:00
        2013-03-13 08:04:00

    """
    c_start_dt = convert_d_to_dt(start_dt)
    c_stop_dt = convert_d_to_dt(stop_dt) if stop_dt is not None else None

    # Return naive datetimes if the input is naive
    return_naive = c_start_dt.tzinfo is None
    # Make sure start_dt is aware
    c_start_dt = attach_tz_if_none(c_start_dt, pytz.utc)

    # Make sure the stop_dt is aware
    c_stop_dt = attach_tz_if_none(c_stop_dt, pytz.utc) if c_stop_dt is not None else None

    # Set initial time and loop iteration values
    time_iter = c_start_dt
    loop_counter = 0

    while True:
        # Break when the end criterion has been met
        if ((c_stop_dt is None and count is not None and loop_counter >= count) or
                (c_stop_dt is not None and is_stop_dt_inclusive and time_iter > c_stop_dt) or
                (c_stop_dt is not None and not is_stop_dt_inclusive and time_iter >= c_stop_dt)):
            break

        yield convert_return_back_to_d(remove_tz_if_return_naive(time_iter, return_naive), start_dt)

        # Increment the time iteration and the loop counter
        time_iter = add_timedelta(time_iter, td, within_tz=within_tz)
        loop_counter += 1


def unix_time(dt, within_tz=None, return_ms=False):
    """
    Converts a datetime object to a unix timestamp.

    Converts a naive or aware datetime object to unix timestamp. If within_tz
    is present, the timestamp returned is relative to that time zone.

    :type dt: datetime
    :param dt: A naive or aware datetime object. If it is naive, it is assumed
        to be UTC.

    :type within_tz: pytz timezone
    :param within_tz: A pytz timezone object if the user wishes to return the
        unix time relative to another timezone.

    :type return_ms: bool
    :param return_ms: A boolean specifying to return the value in milliseconds
        since the Unix epoch. Defaults to False.

    :rtype: int or float
    :returns: An integer timestamp since the Unix epoch. If return_ms is True,
        returns the timestamp in milliseconds.

    .. code-block:: python

        >>> import datetime
        >>> import pytz
        >>> import fleming

        >>> # Do a basic naive UTC conversion
        >>> dt = datetime.datetime(2013, 4, 2)
        >>> print fleming.unix_time(dt)
        1364860800

        >>> # Convert a time in a different timezone
        >>> dt = fleming.convert_to_tz(
        ...    datetime.datetime(2013, 4, 2, 4), pytz.timezone('US/Eastern'))
        >>> print dt
        2013-04-02 00:00:00-04:00

        >>> print fleming.unix_time(dt)
        1364875200

        >>> # Print millisecond returns
        >>> print fleming.unix_time(dt, return_ms=True)
        1364875200000

        >>> # Do a unix_time conversion with respect to another timezone. When
        >>> # it is converted back to a datetime, the time values are correct.
        >>> # The original timezone, however, needs to be added back
        >>> dt = datetime.datetime(2013, 2, 1, 5)

        >>> # Print its EST time for later reference
        >>> print fleming.convert_to_tz(dt, pytz.timezone('US/Eastern'))
        2013-02-01 00:00:00-05:00

        >>> unix_tz_dt = fleming.unix_time(
        ...    dt, within_tz=pytz.timezone('US/Eastern'))
        >>> print unix_tz_dt
        1359676800

        >>> # The datetime should match the original UTC time converted in
        >>> # the timezone of the within_tz parameter. Tz information is
        >>> # originally lost when converting to unix time, so replace the
        >>> # tzinfo object here
        >>> dt = datetime.datetime.fromtimestamp(unix_tz_dt).replace(
        ...    tzinfo=pytz.timezone('US/Eastern'))
        >>> print dt
        2013-02-01 00:00:00-05:00

    """
    # Convert any date input to datetime objects
    c_dt = convert_d_to_dt(dt)

    epoch = datetime.datetime.utcfromtimestamp(0)
    offset = convert_to_tz(c_dt, within_tz).utcoffset().total_seconds() if within_tz else 0
    # Convert the timezone to UTC for arithmetic and make it naive
    c_dt = convert_to_tz(c_dt, pytz.utc).replace(tzinfo=None)
    unix_timestamp = (c_dt - epoch).total_seconds() + offset
    return int(unix_timestamp * 1000 if return_ms else unix_timestamp)
