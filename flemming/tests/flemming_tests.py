"""
Tests for datetime helpers.
"""
import datetime
import unittest

import pytz

import flemming


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
        ret = flemming.attach_tz_if_none(naive_t, pytz.utc)
        # Time should now have a utc tzinfo object
        self.assertEquals(ret.tzinfo, pytz.utc)

    def test_no_tz_attach_eastern(self):
        """
        Tests a datetime object that doesn't have a time zone and has US/Eastern attached.
        """
        naive_t = datetime.datetime(2014, 2, 1)
        # Time should not have a tzinfo object
        self.assertIsNone(naive_t.tzinfo)
        ret = flemming.attach_tz_if_none(naive_t, pytz.timezone('US/Eastern'))
        # Time should now have a utc tzinfo object
        self.assertEquals(ret.tzinfo, pytz.timezone('US/Eastern'))

    def test_existing_tz_attach_utc(self):
        """
        Tests calling attach_tz_if_none on a time that already has a timezone. It should
        return the orignal time value.
        """
        aware_t = datetime.datetime(2014, 2, 1, tzinfo=pytz.timezone('US/Eastern'))
        # Try to attach UTC. It should not attach it
        ret = flemming.attach_tz_if_none(aware_t, pytz.utc)
        self.assertEquals(ret.tzinfo, pytz.timezone('US/Eastern'))


class TestRemoveTzIfReturnNaive(unittest.TestCase):
    """
    Tests the remove_tz_if_return_naive function.
    """
    def test_with_naive_dt_true(self):
        """
        Tests removing the tz of a datetime object with no timezone and
        return_naive set to True.
        """
        naive_t = datetime.datetime(2013, 2, 1, 12)
        ret = flemming.remove_tz_if_return_naive(naive_t, True)
        self.assertEquals(ret, datetime.datetime(2013, 2, 1, 12))

    def test_with_naive_dt_false(self):
        """
        Tests removing the tz of a datetime object with no timezone and
        return_naive set to False.
        """
        naive_t = datetime.datetime(2013, 2, 1, 12)
        ret = flemming.remove_tz_if_return_naive(naive_t, False)
        self.assertEquals(ret, datetime.datetime(2013, 2, 1, 12))

    def test_with_aware_dt_true(self):
        """
        Tests removing the tz of a datetime object with a timezone and
        return_naive set to True.
        """
        aware_t = datetime.datetime(2013, 2, 1, 12, tzinfo=pytz.utc)
        ret = flemming.remove_tz_if_return_naive(aware_t, True)
        self.assertEquals(ret, datetime.datetime(2013, 2, 1, 12))

    def test_with_aware_dt_false(self):
        """
        Tests removing the tz of a datetime object with a timezone and
        return_naive set to False.
        """
        aware_t = datetime.datetime(2013, 2, 1, 12, tzinfo=pytz.utc)
        ret = flemming.remove_tz_if_return_naive(aware_t, False)
        self.assertEquals(ret, datetime.datetime(2013, 2, 1, 12, tzinfo=pytz.utc))


class TestConvertToTz(unittest.TestCase):
    """
    Tests the convert_to_tz function.
    """
    def test_convert_naive_utc_to_est_return_aware(self):
        """
        Tests conversion of naive datetime (assumed to be UTC) to aware EST datetime
        where the return value is aware.
        """
        naive_t = datetime.datetime(2013, 2, 1, 12)
        ret = flemming.convert_to_tz(naive_t, pytz.timezone('US/Eastern'))
        # In this time, eastern standard time is 5 hours before UTC
        self.assertEquals(ret, datetime.datetime(2013, 2, 1, 7, tzinfo=pytz.timezone('US/Eastern')))

    def test_aware_utc_to_est_return_aware(self):
        """
        Tests an aware datetime that is UTC to EST where the return value is aware.
        """
        aware_t = datetime.datetime(2013, 2, 1, 12, tzinfo=pytz.utc)
        ret = flemming.convert_to_tz(aware_t, pytz.timezone('US/Eastern'))
        # In this time, eastern standard time is 5 hours before UTC
        self.assertEquals(ret, datetime.datetime(2013, 2, 1, 7, tzinfo=pytz.timezone('US/Eastern')))

    def test_aware_est_to_cst_return_aware(self):
        """
        Tests converting an aware datetime in EST to CST where the return value is aware.
        """
        aware_t = datetime.datetime(2013, 2, 1, 12, tzinfo=pytz.timezone('US/Eastern'))
        ret = flemming.convert_to_tz(aware_t, pytz.timezone('US/Central'))
        # Central time zone is one hour behind eastern
        self.assertEquals(ret, datetime.datetime(2013, 2, 1, 11, tzinfo=pytz.timezone('US/Central')))

    def test_convert_naive_utc_to_est_return_naive(self):
        """
        Tests conversion of naive datetime (assumed to be UTC) to aware EST datetime where the
        return value is naive.
        """
        naive_t = datetime.datetime(2013, 2, 1, 12)
        ret = flemming.convert_to_tz(naive_t, pytz.timezone('US/Eastern'), return_naive=True)
        # In this time, eastern standard time is 5 hours before UTC
        self.assertEquals(ret, datetime.datetime(2013, 2, 1, 7))

    def test_aware_utc_to_est_return_naive(self):
        """
        Tests an aware datetime that is UTC to EST where the return value is naive.
        """
        aware_t = datetime.datetime(2013, 2, 1, 12, tzinfo=pytz.utc)
        ret = flemming.convert_to_tz(aware_t, pytz.timezone('US/Eastern'), return_naive=True)
        # In this time, eastern standard time is 5 hours before UTC
        self.assertEquals(ret, datetime.datetime(2013, 2, 1, 7))

    def test_aware_est_to_cst_return_naive(self):
        """
        Tests converting an aware datetime in EST to CST where the return value is naive.
        """
        aware_t = datetime.datetime(2013, 2, 1, 12, tzinfo=pytz.timezone('US/Eastern'))
        ret = flemming.convert_to_tz(aware_t, pytz.timezone('US/Central'), return_naive=True)
        # Central time zone is one hour behind eastern
        self.assertEquals(ret, datetime.datetime(2013, 2, 1, 11))


class TestDstNormalize(unittest.TestCase):
    """
    Tests the dst_normalize function. Note that this function is an internal function and expects
    aware datetimes to be passed to it (as compared to the user-facing functions that can have
    naive datetimes passed as arguments). We only test the case of passing aware datetimes.
    """
    def test_no_change_in_tz_aware(self):
        """
        Tests the case where the time given is already aware. Uses a timezone that will not change because
        of daylight savings time.
        """
        aware_t = datetime.datetime(2013, 4, 2, tzinfo=pytz.utc)
        ret = flemming.dst_normalize(aware_t)
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
        ret = flemming.dst_normalize(aware_t)
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
        ret = flemming.dst_normalize(aware_t)
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
        ret = flemming.dst_normalize(aware_t)
        # Verify the time zone of the returned is not in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        # Verify that all of the time values are correct
        self.assertEquals(ret, datetime.datetime(2013, 1, 14, tzinfo=ret.tzinfo))


class TestAddTimedelta(unittest.TestCase):
    """
    Tests the add_timedelta function.
    """
    def test_naive_within_no_tz_return_aware(self):
        """
        Tests time delta arithmetic when the original time is naive and timezone
        arithmetic happens within original timezone. The returned value is
        also aware
        """
        naive_t = datetime.datetime(2013, 4, 1)
        ret = flemming.add_timedelta(naive_t, datetime.timedelta(days=2))
        self.assertEquals(ret, datetime.datetime(2013, 4, 3, tzinfo=pytz.utc))

    def test_naive_within_no_tz_return_naive(self):
        """
        Tests time delta arithmetic when the original time is naive and timezone
        arithmetic happens within original timezone. The returned value is
        also naive.
        """
        naive_t = datetime.datetime(2013, 4, 1)
        ret = flemming.add_timedelta(naive_t, datetime.timedelta(days=2), return_naive=True)
        self.assertEquals(ret, datetime.datetime(2013, 4, 3))

    def test_aware_within_no_tz_return_aware(self):
        """
        Tests time delta arithmetic when the input is aware and there is no within_tz. Returned
        values are aware.
        """
        aware_t = datetime.datetime(2013, 4, 1, tzinfo=pytz.utc)
        ret = flemming.add_timedelta(
            aware_t, datetime.timedelta(days=1, minutes=1, seconds=1, microseconds=1))
        self.assertEquals(ret, datetime.datetime(2013, 4, 2, 0, 1, 1, 1, tzinfo=pytz.utc))

    def test_aware_within_no_tz_return_naive(self):
        """
        Tests time delta arithmetic when the input is aware and there is no within_tz. Returned
        values are naive.
        """
        aware_t = datetime.datetime(2013, 4, 1, tzinfo=pytz.utc)
        ret = flemming.add_timedelta(
            aware_t, datetime.timedelta(days=1, minutes=1, seconds=1, microseconds=1),
            return_naive=True)
        self.assertEquals(ret, datetime.datetime(2013, 4, 2, 0, 1, 1, 1))

    def test_aware_within_no_tz_return_aware_dst_cross(self):
        """
        Tests time delta arithmetic when the input is aware and there is no within_tz. Returned
        values are aware. Tests the case where arithmetic happens across a dst transition.
        """
        # Create an aware datetime that is not in DST
        aware_t = flemming.convert_to_tz(datetime.datetime(2013, 3, 1, 5), pytz.timezone('US/Eastern'))
        # Assert that it isn't in DST
        self.assertEquals(aware_t.tzinfo.dst(aware_t), datetime.timedelta(0))
        # Assert the values are midnight for EST
        self.assertEquals(aware_t, datetime.datetime(2013, 3, 1, tzinfo=pytz.timezone('US/Eastern')))

        # Add a timedelta across the DST transition (Mar 10)
        ret = flemming.add_timedelta(aware_t, datetime.timedelta(weeks=2))
        # Verify the time zone is now in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(hours=1))
        # Verify the time is midnight two weeks later
        self.assertEquals(ret, datetime.datetime(2013, 3, 15, tzinfo=ret.tzinfo))

    def test_aware_within_no_tz_return_naive_dst_cross(self):
        """
        Tests time delta arithmetic when the input is aware and there is no within_tz. Returned
        values are naive. Tests the case where arithmetic happens across a dst transition.
        """
        # Create an aware datetime that is not in DST
        aware_t = flemming.convert_to_tz(datetime.datetime(2013, 3, 1, 5), pytz.timezone('US/Eastern'))
        # Assert that it isn't in DST
        self.assertEquals(aware_t.tzinfo.dst(aware_t), datetime.timedelta(0))
        # Assert the values are midnight for EST
        self.assertEquals(aware_t, datetime.datetime(2013, 3, 1, tzinfo=pytz.timezone('US/Eastern')))

        # Add a timedelta across the DST transition (Mar 10)
        ret = flemming.add_timedelta(aware_t, datetime.timedelta(weeks=2), return_naive=True)
        # Verify the time is midnight two weeks later and is naive
        self.assertEquals(ret, datetime.datetime(2013, 3, 15))

    def test_naive_within_tz_return_aware_dst_cross(self):
        """
        Tests time delta arithmetic when the input is naive and there is arithmetic within another timezone.
        Returned values are aware. Tests the case where arithmetic happens across a dst transition.
        """
        # Create a naive datetime assumed to be in UTC
        naive_t = datetime.datetime(2013, 3, 1, 5)

        # Add a timedelta across the DST transition for EST (Mar 10)
        ret = flemming.add_timedelta(
            naive_t, datetime.timedelta(weeks=2), within_tz=pytz.timezone('US/Eastern'))
        # Verify the time is midnight two weeks later in UTC. Note that the original hour has changed
        # since we crossed the DST boundary in EST
        self.assertEquals(ret, datetime.datetime(2013, 3, 15, 4, tzinfo=pytz.utc))

    def test_naive_within_tz_return_naive_dst_cross(self):
        """
        Tests time delta arithmetic when the input is naive and there is arithmetic within another timezone.
        Returned values are naive. Tests the case where arithmetic happens across a dst transition.
        """
        # Create a naive datetime assumed to be in UTC
        naive_t = datetime.datetime(2013, 3, 1, 5)

        # Add a timedelta across the DST transition for EST (Mar 10)
        ret = flemming.add_timedelta(
            naive_t, datetime.timedelta(weeks=2), within_tz=pytz.timezone('US/Eastern'), return_naive=True)
        # Verify the time is midnight two weeks later in UTC. Note that the original hour has changed
        # since we crossed the DST boundary in EST
        self.assertEquals(ret, datetime.datetime(2013, 3, 15, 4))

    def test_aware_within_tz_return_aware_dst_cross(self):
        """
        Tests time delta arithmetic when the input is aware and there is arithmetic within another timezone.
        Returned values are aware. Tests the case where arithmetic happens across a dst transition.
        """
        # Create an aware datetime that is not in DST for EST
        aware_t = flemming.convert_to_tz(datetime.datetime(2013, 3, 1, 5), pytz.utc)

        # Add a timedelta across the DST transition (Mar 10) within EST
        ret = flemming.add_timedelta(
            aware_t, datetime.timedelta(weeks=2), within_tz=pytz.timezone('US/Eastern'))
        # Verify the time is midnight two weeks later in UTC. Note that the hour changes since it happened
        # across an EST DST boundary
        self.assertEquals(ret, datetime.datetime(2013, 3, 15, 4, tzinfo=pytz.utc))

    def test_aware_within_tz_return_naive_dst_cross(self):
        """
        Tests time delta arithmetic when the input is aware and there is arithmetic within another timezone.
        Returned values are naive. Tests the case where arithmetic happens across a dst transition.
        """
        # Create an aware datetime that is not in DST for EST
        aware_t = flemming.convert_to_tz(datetime.datetime(2013, 3, 1, 5), pytz.utc)

        # Add a timedelta across the DST transition (Mar 10) within EST
        ret = flemming.add_timedelta(
            aware_t, datetime.timedelta(weeks=2), within_tz=pytz.timezone('US/Eastern'), return_naive=True)
        # Verify the time is midnight two weeks later in UTC. Note that the hour changes since it happened
        # across an EST DST boundary
        self.assertEquals(ret, datetime.datetime(2013, 3, 15, 4))

    def test_aware_est_within_cst_return_aware_dst_cross(self):
        """
        Tests time delta arithmetic when the input is aware and there is arithmetic within another timezone.
        Returned values are aware. Tests the case where arithmetic happens across a dst transition.
        """
        # Create an aware datetime that is not in DST
        aware_t = flemming.convert_to_tz(datetime.datetime(2013, 3, 1, 5), pytz.timezone('US/Eastern'))
        # Assert that it isn't in DST
        self.assertEquals(aware_t.tzinfo.dst(aware_t), datetime.timedelta(0))
        # Assert the values are midnight for EST
        self.assertEquals(aware_t, datetime.datetime(2013, 3, 1, tzinfo=pytz.timezone('US/Eastern')))

        # Add a timedelta across the DST transition (Mar 10) within CST
        ret = flemming.add_timedelta(
            aware_t, datetime.timedelta(weeks=2), within_tz=pytz.timezone('US/Central'))

        # Assert that it is in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(hours=1))
        # Verify the time is midnight two weeks later in EST. Note that the timezone changes since it happened
        # across a DST boundary
        self.assertEquals(ret, datetime.datetime(2013, 3, 15, tzinfo=ret.tzinfo))

    def test_aware_est_within_cst_return_naive_dst_cross(self):
        """
        Tests time delta arithmetic when the input is aware and there is arithmetic within another timezone.
        Returned values are naive. Tests the case where arithmetic happens across a dst transition.
        """
        # Create an aware datetime that is not in DST
        aware_t = flemming.convert_to_tz(datetime.datetime(2013, 3, 1, 5), pytz.timezone('US/Eastern'))
        # Assert that it isn't in DST
        self.assertEquals(aware_t.tzinfo.dst(aware_t), datetime.timedelta(0))
        # Assert the values are midnight for EST
        self.assertEquals(aware_t, datetime.datetime(2013, 3, 1, tzinfo=pytz.timezone('US/Eastern')))

        # Add a timedelta across the DST transition (Mar 10) within CST
        ret = flemming.add_timedelta(
            aware_t, datetime.timedelta(weeks=2), within_tz=pytz.timezone('US/Central'), return_naive=True)

        # Verify the time is midnight two weeks later in EST
        self.assertEquals(ret, datetime.datetime(2013, 3, 15))


class TestFloor(unittest.TestCase):
    """
    Tests the floor function.
    """
    def test_naive_floor_year(self):
        """
        Tests flooring a naive datetime to a year and returning an aware datetime.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = flemming.floor(t, 'year')
        self.assertEquals(t, datetime.datetime(2013, 1, 1, tzinfo=pytz.utc))

    def test_naive_floor_month(self):
        """
        Tests flooring a naive datetime to a month and returning an aware datetime.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = flemming.floor(t, 'month')
        self.assertEquals(t, datetime.datetime(2013, 3, 1, tzinfo=pytz.utc))

    def test_naive_floor_week_stays_in_month(self):
        """
        Tests flooring a naive datetime to a week where the month value remains the same.
        Returns an aware datetime.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = flemming.floor(t, 'week')
        self.assertEquals(t, datetime.datetime(2013, 3, 4, tzinfo=pytz.utc))

    def test_naive_floor_week_goes_to_prev_month(self):
        """
        Tests flooring a naive datetime to a week where the month value goes backwards.
        Return value is aware.
        """
        t = datetime.datetime(2013, 3, 1, 12, 23, 4, 40)
        t = flemming.floor(t, 'week')
        self.assertEquals(t, datetime.datetime(2013, 2, 25, tzinfo=pytz.utc))

    def test_naive_floor_day(self):
        """
        Tests flooring a naive datetime to a day. Return value is aware.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = flemming.floor(t, 'day')
        self.assertEquals(t, datetime.datetime(2013, 3, 4, tzinfo=pytz.utc))

    def test_naive_floor_day_return_naive(self):
        """
        Tests flooring a naive datetime to a day. Return value is naive.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = flemming.floor(t, 'day', return_naive=True)
        self.assertEquals(t, datetime.datetime(2013, 3, 4))

    def test_naive_floor_hour(self):
        """
        Tests flooring a naive datetime to an hour. Return value is aware
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = flemming.floor(t, 'hour')
        self.assertEquals(t, datetime.datetime(2013, 3, 4, 12, tzinfo=pytz.utc))

    def test_naive_floor_minute(self):
        """
        Tests flooring a naive datetime to a minute. Return value is aware.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = flemming.floor(t, 'minute')
        self.assertEquals(t, datetime.datetime(2013, 3, 4, 12, 23, tzinfo=pytz.utc))

    def test_naive_floor_second(self):
        """
        Tests flooring a naive datetime to a minute. Return value is aware
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = flemming.floor(t, 'second')
        self.assertEquals(t, datetime.datetime(2013, 3, 4, 12, 23, 4, tzinfo=pytz.utc))

    def test_floor_invalid(self):
        """
        Tests an invalid floor value.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        with self.assertRaises(ValueError):
            flemming.floor(t, 'invalid')

    def test_aware_floor_year(self):
        """
        Tests flooring an aware datetime to a year and returning an aware datetime.
        """
        t = flemming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = flemming.floor(t, 'year')
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 1, 1, tzinfo=t.tzinfo))

    def test_aware_floor_month(self):
        """
        Tests flooring an aware datetime to a month and returning an aware datetime.
        """
        t = flemming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = flemming.floor(t, 'month')
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 3, 1, tzinfo=t.tzinfo))

    def test_aware_floor_week_stays_in_month(self):
        """
        Tests flooring an aware datetime to a week where the month value remains the same.
        Returns an aware datetime.
        """
        t = flemming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = flemming.floor(t, 'week')
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 3, 4, tzinfo=t.tzinfo))

    def test_aware_floor_week_goes_to_prev_month(self):
        """
        Tests flooring an aware datetime to a week where the month value goes backwards.
        Return value is aware.
        """
        t = flemming.convert_to_tz(
            datetime.datetime(2013, 3, 1, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = flemming.floor(t, 'week')
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 2, 25, tzinfo=t.tzinfo))

    def test_aware_floor_day(self):
        """
        Tests flooring an aware datetime to a day. Return value is aware.
        """
        t = flemming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = flemming.floor(t, 'day')
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 3, 4, tzinfo=t.tzinfo))

    def test_aware_floor_day_return_naive(self):
        """
        Tests flooring an aware datetime to a day. Return value is naive.
        """
        t = flemming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = flemming.floor(t, 'day', return_naive=True)
        self.assertEquals(ret, datetime.datetime(2013, 3, 4))

    def test_aware_floor_hour(self):
        """
        Tests flooring an aware datetime to an hour. Return value is aware
        """
        t = flemming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = flemming.floor(t, 'hour')
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 3, 4, t.hour, tzinfo=t.tzinfo))

    def test_aware_floor_minute(self):
        """
        Tests flooring an aware datetime to a minute. Return value is aware.
        """
        t = flemming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = flemming.floor(t, 'minute')
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 3, 4, t.hour, 23, tzinfo=t.tzinfo))

    def test_aware_floor_second(self):
        """
        Tests flooring an aware datetime to a minute. Return value is aware
        """
        t = flemming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = flemming.floor(t, 'second')
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 3, 4, t.hour, 23, 4, tzinfo=t.tzinfo))

    def test_aware_floor_year_out_of_dst(self):
        """
        Tests flooring an aware datetime to a year and returning an aware datetime.
        Floor starts in DST and goes out of DST.
        """
        t = flemming.convert_to_tz(
            datetime.datetime(2013, 3, 14, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(hours=1))
        ret = flemming.floor(t, 'year')
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 1, 1, tzinfo=ret.tzinfo))

    def test_aware_floor_month_out_of_dst(self):
        """
        Tests flooring an aware datetime to a month and returning an aware datetime.
        Floor starts in DST and goes out of DST.
        """
        t = flemming.convert_to_tz(
            datetime.datetime(2013, 3, 14, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(hours=1))
        ret = flemming.floor(t, 'month')
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 3, 1, tzinfo=ret.tzinfo))

    def test_aware_floor_month_into_dst(self):
        """
        Tests flooring an aware datetime to a month and returning an aware datetime.
        Floor starts out of DST and goes into DST.
        """
        t = flemming.convert_to_tz(
            datetime.datetime(2013, 11, 14, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(hours=0))
        ret = flemming.floor(t, 'month')
        # Resulting time zone should be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(hours=1))
        self.assertEquals(ret, datetime.datetime(2013, 11, 1, tzinfo=ret.tzinfo))

    def test_naive_floor_within_tz_day(self):
        """
        Tests the flooring of a naive datetime to a day within another timezone.
        """
        t = datetime.datetime(2013, 4, 1)
        # t is in midnight UTC, but it is still in the previous day for EST.
        ret = flemming.floor(t, 'day', within_tz=pytz.timezone('US/Eastern'))
        # The return value should be for the last day of the previous month, and the
        # timezone should still be in UTC
        self.assertEquals(ret, datetime.datetime(2013, 3, 31, tzinfo=pytz.utc))

    def test_naive_floor_within_tz_day_return_naive(self):
        """
        Tests the flooring of a naive datetime to a day within another timezone.
        Returned value is naive.
        """
        t = datetime.datetime(2013, 4, 1)
        # t is in midnight UTC, but it is still in the previous day for EST.
        ret = flemming.floor(t, 'day', within_tz=pytz.timezone('US/Eastern'), return_naive=True)
        # The return value should be for the last day of the previous month, and the
        # timezone should still be in UTC
        self.assertEquals(ret, datetime.datetime(2013, 3, 31))

    def test_est_floor_within_cst_day(self):
        """
        Tests flooring of an EST time with respect to CST. Returns an aware datetime in EST.
        """
        t = flemming.convert_to_tz(
            datetime.datetime(2013, 4, 1, 4), pytz.timezone('US/Eastern'))
        # Verify it is midnight for eastern time
        self.assertEquals(t.hour, 0)

        # Floor the time to a day with respect to CST. Since CST is an hour behind, the day
        # should be minus one
        ret = flemming.floor(t, 'day', within_tz=pytz.timezone('US/Central'))
        self.assertEquals(ret, datetime.datetime(2013, 3, 31, tzinfo=t.tzinfo))

    def test_utc_floor_within_est_week(self):
        """
        Tests the case where it is the starting of a week in UTC but the floor is
        performed relative to EST, meaning the result should be for the previous week.
        """
        t = datetime.datetime(2013, 4, 8, tzinfo=pytz.utc)
        ret = flemming.floor(t, 'week', within_tz=pytz.timezone('US/Eastern'))
        # The time should be a week earlier in UTC
        self.assertEquals(ret, datetime.datetime(2013, 4, 1, tzinfo=pytz.utc))

    def test_est_floor_within_utc_week(self):
        """
        Tests the case where it is the starting of a week in EST and the floor is
        performed relative to UTC, meaning the result should be for the next week.
        """
        t = flemming.convert_to_tz(
            datetime.datetime(2013, 11, 4, 4), pytz.timezone('US/Eastern'))
        # Affirm that the time is 11 PM in EST
        self.assertEquals(t.day, 3)
        self.assertEquals(t.hour, 23)
        ret = flemming.floor(t, 'week', within_tz=pytz.utc)
        # The time should be a week later in EST since UTC was a week ahead
        self.assertEquals(ret, datetime.datetime(2013, 11, 4, tzinfo=t.tzinfo))


class TestUnixTime(unittest.TestCase):
    """
    Tests the unix_time function.
    """
    def test_unix_time_epoch(self):
        """
        Tests the unix_time function when the epoch is given.
        """
        t = datetime.datetime(1970, 1, 1)
        ret = flemming.unix_time(t)
        self.assertEquals(ret, 0)

    def test_unix_time_arbitrary_one(self):
        """
        Tests unix_time with an arbitrary time.
        datetime(2013, 4, 1, 2) was confirmed to be equal to
        1364781600 by epochconverter.com.
        """
        t = datetime.datetime(2013, 4, 1, 2)
        ret = flemming.unix_time(t)
        self.assertEquals(ret, 1364781600)

    def test_unix_time_arbitrary_two(self):
        """
        Tests unix_time with an arbitrary time.
        datetime(2013, 12, 1, 2) was confirmed to be equal to
        1385863200 by epochconverter.com.
        """
        t = datetime.datetime(2013, 12, 1, 2)
        ret = flemming.unix_time(t)
        self.assertEquals(ret, 1385863200)

    def test_unix_time_return_ms(self):
        """
        Tests unix_time when returning milliseconds. Uses the
        same values from test_unix_time_arbitrary_two.
        """
        t = datetime.datetime(2013, 12, 1, 2)
        ret = flemming.unix_time(t, return_ms=True)
        self.assertEquals(ret, 1385863200 * 1000)

    def test_unix_time_aware_arbitrary(self):
        """
        Tests unix time for an aware time.
        datetime(2013, 12, 1, 2) in EST was confirmed to be
        equal to 1385881200 by epochconverter.com.
        """
        t = flemming.convert_to_tz(
            datetime.datetime(2013, 12, 1, 7), pytz.timezone('US/Eastern'))
        self.assertEquals(t.hour, 2)
        ret = flemming.unix_time(t)
        self.assertEquals(ret, 1385881200)

    def test_unix_time_aware_arbitrary_ms(self):
        """
        Tests unix time for an aware time.
        datetime(2013, 12, 1, 2) in EST was confirmed to be
        equal to 1385881200 by epochconverter.com. Return value is
        in milliseconds.
        """
        t = flemming.convert_to_tz(
            datetime.datetime(2013, 12, 1, 7), pytz.timezone('US/Eastern'))
        self.assertEquals(t.hour, 2)
        ret = flemming.unix_time(t, return_ms=True)
        self.assertEquals(ret, 1385881200 * 1000)

    def test_unix_time_naive_within_tz(self):
        """
        Tests that a naive UTC time is converted relative to an EST tz.
        This means that when converting the time back, the time values are
        correct for the EST time zone.
        """
        t = datetime.datetime(2013, 12, 1, 5)
        ret = flemming.unix_time(t, within_tz=pytz.timezone('US/Eastern'))
        self.assertEquals(ret, 1385856000)
        # Convert it back to a datetime objects. The values should be for midnight
        # since it was an EST time
        t = datetime.datetime.fromtimestamp(ret)
        self.assertEquals(t.hour, 0)
        self.assertEquals(t.day, 1)

    def test_unix_time_aware_within_tz(self):
        """
        Tests that an aware UTC time is converted relative to an EST tz.
        This means that when converting the time back, the time values are
        correct for the EST time zone.
        """
        t = datetime.datetime(2013, 12, 1, 5, tzinfo=pytz.utc)
        ret = flemming.unix_time(t, within_tz=pytz.timezone('US/Eastern'))
        self.assertEquals(ret, 1385856000)
        # Convert it back to a datetime objects. The values should be for midnight
        # since it was an EST time
        t = datetime.datetime.fromtimestamp(ret)
        self.assertEquals(t.hour, 0)
        self.assertEquals(t.day, 1)

    def test_unix_time_aware_within_tz_return_ms(self):
        """
        Tests that an aware UTC time is converted relative to an EST tz.
        This means that when converting the time back, the time values are
        correct for the EST time zone. Return is in milliseconds
        """
        t = datetime.datetime(2013, 12, 1, 5, tzinfo=pytz.utc)
        ret = flemming.unix_time(t, within_tz=pytz.timezone('US/Eastern'), return_ms=True)
        self.assertEquals(ret, 1385856000 * 1000)
        # Convert it back to a datetime objects. The values should be for midnight
        # since it was an EST time
        t = datetime.datetime.fromtimestamp(ret / 1000)
        self.assertEquals(t.hour, 0)
        self.assertEquals(t.day, 1)
