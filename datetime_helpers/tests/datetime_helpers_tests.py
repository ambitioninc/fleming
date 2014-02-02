"""
Tests for datetime helpers.
"""
import datetime
import unittest

import pytz

import datetime_helpers


class TestAttachTzIfNone(unittest.TestCase):
    """
    Tests the attach_tz_if_none function. Verifies that a timezone is attached to
    a datetime if it doesn't have one. Otherwise, the time object should retain its timezone.
    """
    def test_no_tz_attach_utc(self):
        """
        Tests a datetime object that doesn't have a time zone and has utc attached.
        """
        naive_t = datetime.datetime(2014, 2, 1)
        # Time should not have a tzinfo object
        self.assertIsNone(naive_t.tzinfo)
        ret = datetime_helpers.attach_tz_if_none(naive_t, pytz.utc)
        # Time should now have a utc tzinfo object
        self.assertEquals(ret.tzinfo, pytz.utc)

    def test_no_tz_attach_eastern(self):
        """
        Tests a datetime object that doesn't have a time zone and has US/Eastern attached.
        """
        naive_t = datetime.datetime(2014, 2, 1)
        # Time should not have a tzinfo object
        self.assertIsNone(naive_t.tzinfo)
        ret = datetime_helpers.attach_tz_if_none(naive_t, pytz.timezone('US/Eastern'))
        # Time should now have a utc tzinfo object
        self.assertEquals(ret.tzinfo, pytz.timezone('US/Eastern'))

    def test_existing_tz_attach_utc(self):
        """
        Tests calling attach_tz_if_none on a time that already has a timezone. It should
        return the orignal time value.
        """
        aware_t = datetime.datetime(2014, 2, 1, tzinfo=pytz.timezone('US/Eastern'))
        # Try to attach UTC. It should not attach it
        ret = datetime_helpers.attach_tz_if_none(aware_t, pytz.utc)
        self.assertEquals(ret.tzinfo, pytz.timezone('US/Eastern'))


class TestConvertToTz(unittest.TestCase):
    """
    Tests the convert_to_tz function.
    """
    def test_convert_naive_utc_to_est(self):
        """
        Tests conversion of naive datetime (assumed to be UTC) to aware EST datetime.
        """
        naive_t = datetime.datetime(2013, 2, 1, 12)
        ret = datetime_helpers.convert_to_tz(naive_t, pytz.timezone('US/Eastern'))
        # In this time, eastern standard time is 5 hours before UTC
        self.assertEquals(ret, datetime.datetime(2013, 2, 1, 7, tzinfo=pytz.timezone('US/Eastern')))

    def test_aware_utc_to_est(self):
        """
        Tests an aware datetime that is UTC to EST.
        """
        aware_t = datetime.datetime(2013, 2, 1, 12, tzinfo=pytz.utc)
        ret = datetime_helpers.convert_to_tz(aware_t, pytz.timezone('US/Eastern'))
        # In this time, eastern standard time is 5 hours before UTC
        self.assertEquals(ret, datetime.datetime(2013, 2, 1, 7, tzinfo=pytz.timezone('US/Eastern')))

    def test_aware_est_to_cst(self):
        """
        Tests converting an aware datetime in EST to CST.
        """
        aware_t = datetime.datetime(2013, 2, 1, 12, tzinfo=pytz.timezone('US/Eastern'))
        ret = datetime_helpers.convert_to_tz(aware_t, pytz.timezone('US/Central'))
        # Central time zone is one hour behind eastern
        self.assertEquals(ret, datetime.datetime(2013, 2, 1, 11, tzinfo=pytz.timezone('US/Central')))


class TestDstNormalize(unittest.TestCase):
    """
    Tests the dst_normalize function.
    """
    def test_no_change_in_tz_naive(self):
        """
        Tests the case where the time zone does not change because of a daylight savings time transition.
        Tests a naive datetime being sent to the function (it is assumed to be utc if naive).
        """
        naive_t = datetime.datetime(2013, 4, 2)
        ret = datetime_helpers.dst_normalize(naive_t, pytz.utc)
        self.assertEquals(ret, datetime.datetime(2013, 4, 2, tzinfo=pytz.utc))

    def test_no_change_in_tz_aware(self):
        """
        Tests the case where the time given is already aware. Uses a timezone that will not change because
        of daylight savings time.
        """
        aware_t = datetime.datetime(2013, 4, 2, tzinfo=pytz.utc)
        ret = datetime_helpers.dst_normalize(aware_t, pytz.utc)
        self.assertEquals(ret, datetime.datetime(2013, 4, 2, tzinfo=pytz.utc))

    def test_change_in_tz_into_dst(self):
        """
        Tests doing datetime arithmetic on a datetime going across a dst border. The resulting
        value should have equivalent time fields, but the time zone should be updated to be
        in dst.
        """
        est = pytz.timezone('US/Eastern')
        aware_t = datetime.datetime(2013, 3, 7, tzinfo=est)
        aware_t = est.normalize(aware_t)
        # The time zone should not initially be in DST
        self.assertEquals(aware_t.tzinfo.dst(aware_t), datetime.timedelta(0))
        # After adding a week to it using a normal timedelta, it should be in dst now
        aware_t += datetime.timedelta(weeks=1)
        # However, because of datetime arithmetic, the timezone will not get updated properly
        self.assertEquals(aware_t.tzinfo.dst(aware_t), datetime.timedelta(0))
        # Do a DST normalization. The resulting time zone should be in DST, but none of the
        # time values in original time should have changed
        ret = datetime_helpers.dst_normalize(aware_t, pytz.timezone('US/Eastern'))
        # Verify the time zone of the returned is in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(hours=1))
        # Verify that all of the time values are correct (i.e. verify an extra hour wasn't added
        # because of the DST crossover
        self.assertEquals(ret, datetime.datetime(2013, 3, 14, tzinfo=ret.tzinfo))

    def test_change_in_tz_out_of_dst(self):
        """
        Tests doing datetime arithmetic on a datetime going across a dst border. The resulting
        value should have equivalent time fields, but the time zone should be updated to be
        out of dst (the original time is in dst).
        """
        est = pytz.timezone('US/Eastern')
        aware_t = datetime.datetime(2013, 11, 1, tzinfo=est)
        aware_t = est.normalize(aware_t)
        # Verify that our initial test time had an hour added to it because of normalization
        self.assertEquals(aware_t, datetime.datetime(2013, 11, 1, 1, tzinfo=aware_t.tzinfo))
        # The time zone should initially be in DST
        self.assertEquals(aware_t.tzinfo.dst(aware_t), datetime.timedelta(hours=1))
        # After adding a week to it using a normal timedelta, it should not be in dst now
        aware_t += datetime.timedelta(weeks=1)
        # However, because of datetime arithmetic, the timezone will not get updated properly
        self.assertEquals(aware_t.tzinfo.dst(aware_t), datetime.timedelta(hours=1))
        # Do a DST normalization. The resulting time zone should not be in DST, but none of the
        # time values in original time should have changed
        ret = datetime_helpers.dst_normalize(aware_t, pytz.timezone('US/Eastern'))
        # Verify the time zone of the returned is not in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        # Verify that all of the time values are correct (i.e. verify an extra hour wasn't added
        # because of the DST crossover
        self.assertEquals(ret, datetime.datetime(2013, 11, 8, 1, tzinfo=ret.tzinfo))

    def test_no_change_in_tz(self):
        """
        Tests datetime arithmetic when it does not cross dst boundaries. Previous and resulting
        datetimes should be identical.
        """
        est = pytz.timezone('US/Eastern')
        aware_t = datetime.datetime(2013, 1, 7, tzinfo=est)
        aware_t = est.normalize(aware_t)
        # The time zone should not initially be in DST
        self.assertEquals(aware_t.tzinfo.dst(aware_t), datetime.timedelta(0))
        # After adding a week to it using a normal timedelta, it should still not be in dst
        aware_t += datetime.timedelta(weeks=1)
        self.assertEquals(aware_t.tzinfo.dst(aware_t), datetime.timedelta(0))
        # Do a DST normalization. The resulting time zone should not be in DST, and none of the
        # time values in original time should have changed
        ret = datetime_helpers.dst_normalize(aware_t, pytz.timezone('US/Eastern'))
        # Verify the time zone of the returned is not in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        # Verify that all of the time values are correct
        self.assertEquals(ret, datetime.datetime(2013, 1, 14, tzinfo=ret.tzinfo))


class TestTimeDeltaTz(unittest.TestCase):
    """
    Tests the timedelta_tz function.
    """
    def test_utc_tz_naive(self):
        """
        Tests time delta arithmetic when the time zone is UTC and the
        input is a naive time
        """
        naive_t = datetime.datetime(2013, 4, 1)
        ret = datetime_helpers.timedelta_tz(naive_t, pytz.utc, datetime.timedelta(days=2))
        self.assertEquals(ret, datetime.datetime(2013, 4, 3, tzinfo=pytz.utc))

    def test_utc_tz_aware(self):
        """
        Tests time delta arithmetic when the time zone is UTC and input is aware.
        """
        aware_t = datetime.datetime(2013, 4, 1, tzinfo=pytz.utc)
        ret = datetime_helpers.timedelta_tz(
            aware_t, pytz.utc, datetime.timedelta(days=1, minutes=1, seconds=1, microseconds=1))
        self.assertEquals(
            ret, datetime.datetime(2013, 4, 2, 0, 1, 1, 1, tzinfo=pytz.utc))

    def test_est_no_dst_transition(self):
        """
        Tests timedelta arithmetic in EST when there is no DST transition.
        """
        aware_t = datetime.datetime(2013, 4, 1, tzinfo=pytz.utc)
        # Convert into EST when doing the time delta
        ret = datetime_helpers.timedelta_tz(aware_t, pytz.timezone('US/Eastern'), datetime.timedelta(days=1))
        # Return a time that is back in its original UTC form
        self.assertEquals(ret, datetime.datetime(2013, 4, 2, tzinfo=pytz.utc))

    def test_est_transition_into_dst(self):
        """
        Tests a time that will cross a DST boundary in EST.
        """
        # Start the time outside of DST in EST. This time is in UTC since the function
        # expects UTC times. Note that DST is Mar 10, 2013
        aware_t = datetime.datetime(2013, 3, 7)
        # Do a time delta of a week so that it will cross the DST border.
        ret = datetime_helpers.timedelta_tz(aware_t, pytz.timezone('US/Eastern'), datetime.timedelta(weeks=1))
        # The return value should be a week later, however the hour is one less in UTC since EST went
        # an hour ahead
        self.assertEquals(ret, datetime.datetime(2013, 3, 13, 23, tzinfo=pytz.utc))

    def test_est_transition_out_of_dst(self):
        """
        Tests a time that will cross a DST boundary in EST.
        """
        # Start the time in DST in EST. This time is in UTC since the function
        # expects UTC times. Note that DST ends on Nov 3, 2013
        aware_t = datetime.datetime(2013, 10, 31)
        # Do a time delta of a week so that it will cross the DST border.
        ret = datetime_helpers.timedelta_tz(aware_t, pytz.timezone('US/Eastern'), datetime.timedelta(weeks=1))
        # The return value should be a week later, however the hour is one more in UTC since EST went
        # an hour behind
        self.assertEquals(ret, datetime.datetime(2013, 11, 7, 1, tzinfo=pytz.utc))


class TestDatetimeFloor(unittest.TestCase):
    """
    Tests the datetime_floor function.
    """
    def test_datetime_floor_year(self):
        """
        Tests flooring a datetime to a year.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = datetime_helpers.datetime_floor(t, 'year')
        self.assertEquals(t, datetime.datetime(2013, 1, 1))

    def test_datetime_floor_month(self):
        """
        Tests flooring a datetime to a month.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = datetime_helpers.datetime_floor(t, 'month')
        self.assertEquals(t, datetime.datetime(2013, 3, 1))

    def test_datetime_floor_week_stays_in_month(self):
        """
        Tests flooring a datetime to a week where the month value remains the same.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = datetime_helpers.datetime_floor(t, 'week')
        self.assertEquals(t, datetime.datetime(2013, 3, 4))

    def test_datetime_floor_week_goes_to_prev_month(self):
        """
        Tests flooring a datetime to a week where the month value goes backwards.
        """
        t = datetime.datetime(2013, 3, 1, 12, 23, 4, 40)
        t = datetime_helpers.datetime_floor(t, 'week')
        self.assertEquals(t, datetime.datetime(2013, 2, 25))

    def test_datetime_floor_day(self):
        """
        Tests flooring a datetime to a day.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = datetime_helpers.datetime_floor(t, 'day')
        self.assertEquals(t, datetime.datetime(2013, 3, 4))

    def test_datetime_floor_hour(self):
        """
        Tests flooring a datetime to an hour.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = datetime_helpers.datetime_floor(t, 'hour')
        self.assertEquals(t, datetime.datetime(2013, 3, 4, 12))

    def test_datetime_floor_minute(self):
        """
        Tests flooring a datetime to a minute.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = datetime_helpers.datetime_floor(t, 'minute')
        self.assertEquals(t, datetime.datetime(2013, 3, 4, 12, 23))

    def test_datetime_floor_second(self):
        """
        Tests flooring a datetime to a minute.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = datetime_helpers.datetime_floor(t, 'second')
        self.assertEquals(t, datetime.datetime(2013, 3, 4, 12, 23, 4))

    def test_datetime_floor_invalid(self):
        """
        Tests an invalid floor to datetime_floor.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        with self.assertRaises(ValueError):
            datetime_helpers.datetime_floor(t, 'invalid')


class TestDatetimeFloorTz(unittest.TestCase):
    """
    Tests the datetime_floor_tz.
    """
    def test_datetime_floor_day_est_floor_to_prev_day(self):
        """
        Tests that doing a datetime floor for a day in est that results in a floored
        value for the previous day.
        """
        utc_t = datetime.datetime(2013, 4, 1)
        # Although the utc time is in April 1, it is still March 31 in EST
        ret = datetime_helpers.datetime_floor_tz(utc_t, pytz.timezone('US/Eastern'), 'day')
        self.assertEquals(ret, datetime.datetime(2013, 3, 31, tzinfo=pytz.utc))

    def test_datetime_floor_day_est_floor_to_same_day(self):
        """
        Tests that doing a datetime floor for a day in est that results in a floored
        value for the same day.
        """
        utc_t = datetime.datetime(2013, 4, 6, 5)
        ret = datetime_helpers.datetime_floor_tz(utc_t, pytz.timezone('US/Eastern'), 'day')
        self.assertEquals(ret, datetime.datetime(2013, 4, 6, tzinfo=pytz.utc))


class TestUnixTime(unittest.TestCase):
    """
    Tests the unix_time function.
    """
    def test_unix_time_epoch(self):
        """
        Tests the unix_time function when the epoch is given.
        """
        t = datetime.datetime(1970, 1, 1)
        ret = datetime_helpers.unix_time(t)
        self.assertEquals(ret, 0)

    def test_unix_time_arbitrary_one(self):
        """
        Tests unix_time with an arbitrary time.
        datetime(2013, 4, 1, 2) was confirmed to be equal to
        1364781600 by epochconverter.com.
        """
        t = datetime.datetime(2013, 4, 1, 2)
        ret = datetime_helpers.unix_time(t)
        self.assertEquals(ret, 1364781600)

    def test_unix_time_arbitrary_two(self):
        """
        Tests unix_time with an arbitrary time.
        datetime(2013, 12, 1, 2) was confirmed to be equal to
        1385863200 by epochconverter.com.
        """
        t = datetime.datetime(2013, 12, 1, 2)
        ret = datetime_helpers.unix_time(t)
        self.assertEquals(ret, 1385863200)


class TestUnixTimeMs(unittest.TestCase):
    """
    Tests the unix_time_ms function.
    """
    def test_unix_time_ms_epoch(self):
        """
        Tests the unix_time_ms function when the epoch is given.
        """
        t = datetime.datetime(1970, 1, 1)
        ret = datetime_helpers.unix_time_ms(t)
        self.assertEquals(ret, 0)

    def test_unix_time_ms_arbitrary_one(self):
        """
        Tests unix_time_ms with an arbitrary time.
        datetime(2013, 12, 1, 2) was confirmed to be equal to
        1385863200 by epochconverter.com. Mutliple that by
        1000 and you have milliseconds
        """
        t = datetime.datetime(2013, 12, 1, 2)
        ret = datetime_helpers.unix_time_ms(t)
        self.assertEquals(ret, 1385863200 * 1000)


class TestUnixTimeTz(unittest.TestCase):
    """
    Tests the unix_time_tz function.
    """
    def test_unix_time_tz_epoch_est(self):
        """
        Tests the unix_time_tz function when the epoch is given in EST.
        """
        t = datetime.datetime(1970, 1, 1, 5)
        ret = datetime_helpers.unix_time_tz(t, pytz.timezone('US/Eastern'))
        self.assertEquals(ret, 0)

    def test_unix_time_tz_arbitrary_dst(self):
        """
        Tests unix_time_tz with an arbitrary time.
        datetime(2013, 4, 1, 2, 6) was confirmed to be equal to
        1364796000 by epochconverter.com in the Eastern timezone.
        This time is also in EST and has a four hour offset (from the utc time
        of 2013, 4, 1, 2)
        """
        t = datetime.datetime(2013, 4, 1, 6)
        ret = datetime_helpers.unix_time_tz(t, pytz.timezone('US/Eastern'))
        self.assertEquals(ret, 1364781600)

    def test_unix_time_tz_arbitrary_no_dst(self):
        """
        Tests unix_time_tz with an arbitrary time.
        datetime(2013, 12, 1, 7) was confirmed to be equal to
        1385863200 by epochconverter.com in the Eastern timezone.
        This time is also in EST and has a five hour offset (from the utc time
        of 2013, 12, 1, 2)
        """
        t = datetime.datetime(2013, 12, 1, 7)
        ret = datetime_helpers.unix_time_tz(t, pytz.timezone('US/Eastern'))
        self.assertEquals(ret, 1385863200)


class TestUnixTimeTzMs(unittest.TestCase):
    """
    Tests the unix_time_tz_ms function.
    """
    def test_unix_time_tz_ms_epoch_est(self):
        """
        Tests the unix_time_tz_ms function when the epoch is given in EST.
        """
        t = datetime.datetime(1970, 1, 1, 5)
        ret = datetime_helpers.unix_time_tz_ms(t, pytz.timezone('US/Eastern'))
        self.assertEquals(ret, 0)

    def test_unix_time_tz_ms_arbitrary_dst(self):
        """
        Tests unix_time_tz_ms with an arbitrary time.
        datetime(2013, 4, 1, 2, 6) was confirmed to be equal to
        1364796000 by epochconverter.com in the Eastern timezone.
        This time is also in EST and has a four hour offset (from the utc time
        of 2013, 4, 1, 2)
        """
        t = datetime.datetime(2013, 4, 1, 6)
        ret = datetime_helpers.unix_time_tz_ms(t, pytz.timezone('US/Eastern'))
        self.assertEquals(ret, 1364781600 * 1000)

    def test_unix_time_tz_ms_arbitrary_no_dst(self):
        """
        Tests unix_time with an arbitrary time.
        datetime(2013, 12, 1, 7) was confirmed to be equal to
        1385863200 by epochconverter.com in the Eastern timezone.
        This time is also in EST and has a five hour offset (from the utc time
        of 2013, 12, 1, 2)
        """
        t = datetime.datetime(2013, 12, 1, 7)
        ret = datetime_helpers.unix_time_tz_ms(t, pytz.timezone('US/Eastern'))
        self.assertEquals(ret, 1385863200 * 1000)
