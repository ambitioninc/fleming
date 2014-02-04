"""
Tests for datetime helpers.
"""
import datetime
import unittest

import pytz

from fleming import fleming


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
        ret = fleming.attach_tz_if_none(naive_t, pytz.utc)
        # Time should now have a utc tzinfo object
        self.assertEquals(ret.tzinfo, pytz.utc)

    def test_no_tz_attach_eastern(self):
        """
        Tests a datetime object that doesn't have a time zone and has US/Eastern attached.
        """
        naive_t = datetime.datetime(2014, 2, 1)
        # Time should not have a tzinfo object
        self.assertIsNone(naive_t.tzinfo)
        ret = fleming.attach_tz_if_none(naive_t, pytz.timezone('US/Eastern'))
        # Time should now have a utc tzinfo object
        self.assertEquals(ret.tzinfo, pytz.timezone('US/Eastern'))

    def test_existing_tz_attach_utc(self):
        """
        Tests calling attach_tz_if_none on a time that already has a timezone. It should
        return the orignal time value.
        """
        aware_t = datetime.datetime(2014, 2, 1, tzinfo=pytz.timezone('US/Eastern'))
        # Try to attach UTC. It should not attach it
        ret = fleming.attach_tz_if_none(aware_t, pytz.utc)
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
        ret = fleming.remove_tz_if_return_naive(naive_t, True)
        self.assertEquals(ret, datetime.datetime(2013, 2, 1, 12))

    def test_with_naive_dt_false(self):
        """
        Tests removing the tz of a datetime object with no timezone and
        return_naive set to False.
        """
        naive_t = datetime.datetime(2013, 2, 1, 12)
        ret = fleming.remove_tz_if_return_naive(naive_t, False)
        self.assertEquals(ret, datetime.datetime(2013, 2, 1, 12))

    def test_with_aware_dt_true(self):
        """
        Tests removing the tz of a datetime object with a timezone and
        return_naive set to True.
        """
        aware_t = datetime.datetime(2013, 2, 1, 12, tzinfo=pytz.utc)
        ret = fleming.remove_tz_if_return_naive(aware_t, True)
        self.assertEquals(ret, datetime.datetime(2013, 2, 1, 12))

    def test_with_aware_dt_false(self):
        """
        Tests removing the tz of a datetime object with a timezone and
        return_naive set to False.
        """
        aware_t = datetime.datetime(2013, 2, 1, 12, tzinfo=pytz.utc)
        ret = fleming.remove_tz_if_return_naive(aware_t, False)
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
        ret = fleming.convert_to_tz(naive_t, pytz.timezone('US/Eastern'))
        # In this time, eastern standard time is 5 hours before UTC
        self.assertEquals(ret, datetime.datetime(2013, 2, 1, 7, tzinfo=pytz.timezone('US/Eastern')))

    def test_aware_utc_to_est_return_aware(self):
        """
        Tests an aware datetime that is UTC to EST where the return value is aware.
        """
        aware_t = datetime.datetime(2013, 2, 1, 12, tzinfo=pytz.utc)
        ret = fleming.convert_to_tz(aware_t, pytz.timezone('US/Eastern'))
        # In this time, eastern standard time is 5 hours before UTC
        self.assertEquals(ret, datetime.datetime(2013, 2, 1, 7, tzinfo=pytz.timezone('US/Eastern')))

    def test_aware_est_to_cst_return_aware(self):
        """
        Tests converting an aware datetime in EST to CST where the return value is aware.
        """
        aware_t = datetime.datetime(2013, 2, 1, 12, tzinfo=pytz.timezone('US/Eastern'))
        ret = fleming.convert_to_tz(aware_t, pytz.timezone('US/Central'))
        # Central time zone is one hour behind eastern
        self.assertEquals(ret, datetime.datetime(2013, 2, 1, 11, tzinfo=pytz.timezone('US/Central')))

    def test_convert_naive_utc_to_est_return_naive(self):
        """
        Tests conversion of naive datetime (assumed to be UTC) to aware EST datetime where the
        return value is naive.
        """
        naive_t = datetime.datetime(2013, 2, 1, 12)
        ret = fleming.convert_to_tz(naive_t, pytz.timezone('US/Eastern'), return_naive=True)
        # In this time, eastern standard time is 5 hours before UTC
        self.assertEquals(ret, datetime.datetime(2013, 2, 1, 7))

    def test_aware_utc_to_est_return_naive(self):
        """
        Tests an aware datetime that is UTC to EST where the return value is naive.
        """
        aware_t = datetime.datetime(2013, 2, 1, 12, tzinfo=pytz.utc)
        ret = fleming.convert_to_tz(aware_t, pytz.timezone('US/Eastern'), return_naive=True)
        # In this time, eastern standard time is 5 hours before UTC
        self.assertEquals(ret, datetime.datetime(2013, 2, 1, 7))

    def test_aware_est_to_cst_return_naive(self):
        """
        Tests converting an aware datetime in EST to CST where the return value is naive.
        """
        aware_t = datetime.datetime(2013, 2, 1, 12, tzinfo=pytz.timezone('US/Eastern'))
        ret = fleming.convert_to_tz(aware_t, pytz.timezone('US/Central'), return_naive=True)
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
        ret = fleming.dst_normalize(aware_t)
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
        ret = fleming.dst_normalize(aware_t)
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
        ret = fleming.dst_normalize(aware_t)
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
        ret = fleming.dst_normalize(aware_t)
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
        ret = fleming.add_timedelta(naive_t, datetime.timedelta(days=2))
        self.assertEquals(ret, datetime.datetime(2013, 4, 3, tzinfo=pytz.utc))

    def test_naive_within_no_tz_return_naive(self):
        """
        Tests time delta arithmetic when the original time is naive and timezone
        arithmetic happens within original timezone. The returned value is
        also naive.
        """
        naive_t = datetime.datetime(2013, 4, 1)
        ret = fleming.add_timedelta(naive_t, datetime.timedelta(days=2), return_naive=True)
        self.assertEquals(ret, datetime.datetime(2013, 4, 3))

    def test_aware_within_no_tz_return_aware(self):
        """
        Tests time delta arithmetic when the input is aware and there is no within_tz. Returned
        values are aware.
        """
        aware_t = datetime.datetime(2013, 4, 1, tzinfo=pytz.utc)
        ret = fleming.add_timedelta(
            aware_t, datetime.timedelta(days=1, minutes=1, seconds=1, microseconds=1))
        self.assertEquals(ret, datetime.datetime(2013, 4, 2, 0, 1, 1, 1, tzinfo=pytz.utc))

    def test_aware_within_no_tz_return_naive(self):
        """
        Tests time delta arithmetic when the input is aware and there is no within_tz. Returned
        values are naive.
        """
        aware_t = datetime.datetime(2013, 4, 1, tzinfo=pytz.utc)
        ret = fleming.add_timedelta(
            aware_t, datetime.timedelta(days=1, minutes=1, seconds=1, microseconds=1),
            return_naive=True)
        self.assertEquals(ret, datetime.datetime(2013, 4, 2, 0, 1, 1, 1))

    def test_aware_within_no_tz_return_aware_dst_cross(self):
        """
        Tests time delta arithmetic when the input is aware and there is no within_tz. Returned
        values are aware. Tests the case where arithmetic happens across a dst transition.
        """
        # Create an aware datetime that is not in DST
        aware_t = fleming.convert_to_tz(datetime.datetime(2013, 3, 1, 5), pytz.timezone('US/Eastern'))
        # Assert that it isn't in DST
        self.assertEquals(aware_t.tzinfo.dst(aware_t), datetime.timedelta(0))
        # Assert the values are midnight for EST
        self.assertEquals(aware_t, datetime.datetime(2013, 3, 1, tzinfo=pytz.timezone('US/Eastern')))

        # Add a timedelta across the DST transition (Mar 10)
        ret = fleming.add_timedelta(aware_t, datetime.timedelta(weeks=2))
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
        aware_t = fleming.convert_to_tz(datetime.datetime(2013, 3, 1, 5), pytz.timezone('US/Eastern'))
        # Assert that it isn't in DST
        self.assertEquals(aware_t.tzinfo.dst(aware_t), datetime.timedelta(0))
        # Assert the values are midnight for EST
        self.assertEquals(aware_t, datetime.datetime(2013, 3, 1, tzinfo=pytz.timezone('US/Eastern')))

        # Add a timedelta across the DST transition (Mar 10)
        ret = fleming.add_timedelta(aware_t, datetime.timedelta(weeks=2), return_naive=True)
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
        ret = fleming.add_timedelta(
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
        ret = fleming.add_timedelta(
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
        aware_t = fleming.convert_to_tz(datetime.datetime(2013, 3, 1, 5), pytz.utc)

        # Add a timedelta across the DST transition (Mar 10) within EST
        ret = fleming.add_timedelta(
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
        aware_t = fleming.convert_to_tz(datetime.datetime(2013, 3, 1, 5), pytz.utc)

        # Add a timedelta across the DST transition (Mar 10) within EST
        ret = fleming.add_timedelta(
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
        aware_t = fleming.convert_to_tz(datetime.datetime(2013, 3, 1, 5), pytz.timezone('US/Eastern'))
        # Assert that it isn't in DST
        self.assertEquals(aware_t.tzinfo.dst(aware_t), datetime.timedelta(0))
        # Assert the values are midnight for EST
        self.assertEquals(aware_t, datetime.datetime(2013, 3, 1, tzinfo=pytz.timezone('US/Eastern')))

        # Add a timedelta across the DST transition (Mar 10) within CST
        ret = fleming.add_timedelta(
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
        aware_t = fleming.convert_to_tz(datetime.datetime(2013, 3, 1, 5), pytz.timezone('US/Eastern'))
        # Assert that it isn't in DST
        self.assertEquals(aware_t.tzinfo.dst(aware_t), datetime.timedelta(0))
        # Assert the values are midnight for EST
        self.assertEquals(aware_t, datetime.datetime(2013, 3, 1, tzinfo=pytz.timezone('US/Eastern')))

        # Add a timedelta across the DST transition (Mar 10) within CST
        ret = fleming.add_timedelta(
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
        t = fleming.floor(t, year=1)
        self.assertEquals(t, datetime.datetime(2013, 1, 1, tzinfo=pytz.utc))

    def test_naive_floor_month(self):
        """
        Tests flooring a naive datetime to a month and returning an aware datetime.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = fleming.floor(t, month=1)
        self.assertEquals(t, datetime.datetime(2013, 3, 1, tzinfo=pytz.utc))

    def test_naive_floor_week_stays_in_month(self):
        """
        Tests flooring a naive datetime to a week where the month value remains the same.
        Returns an aware datetime.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = fleming.floor(t, week=1)
        self.assertEquals(t, datetime.datetime(2013, 3, 4, tzinfo=pytz.utc))

    def test_naive_floor_week_goes_to_prev_month(self):
        """
        Tests flooring a naive datetime to a week where the month value goes backwards.
        Return value is aware.
        """
        t = datetime.datetime(2013, 3, 1, 12, 23, 4, 40)
        t = fleming.floor(t, week=1)
        self.assertEquals(t, datetime.datetime(2013, 2, 25, tzinfo=pytz.utc))

    def test_naive_floor_day(self):
        """
        Tests flooring a naive datetime to a day. Return value is aware.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = fleming.floor(t, day=1)
        self.assertEquals(t, datetime.datetime(2013, 3, 4, tzinfo=pytz.utc))

    def test_naive_floor_day_return_naive(self):
        """
        Tests flooring a naive datetime to a day. Return value is naive.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = fleming.floor(t, day=1, return_naive=True)
        self.assertEquals(t, datetime.datetime(2013, 3, 4))

    def test_naive_floor_hour(self):
        """
        Tests flooring a naive datetime to an hour. Return value is aware
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = fleming.floor(t, hour=1)
        self.assertEquals(t, datetime.datetime(2013, 3, 4, 12, tzinfo=pytz.utc))

    def test_naive_floor_minute(self):
        """
        Tests flooring a naive datetime to a minute. Return value is aware.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = fleming.floor(t, minute=1)
        self.assertEquals(t, datetime.datetime(2013, 3, 4, 12, 23, tzinfo=pytz.utc))

    def test_naive_floor_second(self):
        """
        Tests flooring a naive datetime to a minute. Return value is aware
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = fleming.floor(t, second=1)
        self.assertEquals(t, datetime.datetime(2013, 3, 4, 12, 23, 4, tzinfo=pytz.utc))

    def test_aware_floor_year(self):
        """
        Tests flooring an aware datetime to a year and returning an aware datetime.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = fleming.floor(t, year=1)
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 1, 1, tzinfo=t.tzinfo))

    def test_aware_floor_month(self):
        """
        Tests flooring an aware datetime to a month and returning an aware datetime.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = fleming.floor(t, month=1)
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 3, 1, tzinfo=t.tzinfo))

    def test_aware_floor_week_stays_in_month(self):
        """
        Tests flooring an aware datetime to a week where the month value remains the same.
        Returns an aware datetime.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = fleming.floor(t, week=1)
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 3, 4, tzinfo=t.tzinfo))

    def test_aware_floor_week_goes_to_prev_month(self):
        """
        Tests flooring an aware datetime to a week where the month value goes backwards.
        Return value is aware.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 3, 1, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = fleming.floor(t, week=1)
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 2, 25, tzinfo=t.tzinfo))

    def test_aware_floor_day(self):
        """
        Tests flooring an aware datetime to a day. Return value is aware.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = fleming.floor(t, day=1)
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 3, 4, tzinfo=t.tzinfo))

    def test_aware_floor_day_return_naive(self):
        """
        Tests flooring an aware datetime to a day. Return value is naive.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = fleming.floor(t, day=1, return_naive=True)
        self.assertEquals(ret, datetime.datetime(2013, 3, 4))

    def test_aware_floor_hour(self):
        """
        Tests flooring an aware datetime to an hour. Return value is aware
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = fleming.floor(t, hour=1)
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 3, 4, t.hour, tzinfo=t.tzinfo))

    def test_aware_floor_minute(self):
        """
        Tests flooring an aware datetime to a minute. Return value is aware.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = fleming.floor(t, minute=1)
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 3, 4, t.hour, 23, tzinfo=t.tzinfo))

    def test_aware_floor_second(self):
        """
        Tests flooring an aware datetime to a minute. Return value is aware
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = fleming.floor(t, second=1)
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 3, 4, t.hour, 23, 4, tzinfo=t.tzinfo))

    def test_aware_floor_year_out_of_dst(self):
        """
        Tests flooring an aware datetime to a year and returning an aware datetime.
        Floor starts in DST and goes out of DST.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 3, 14, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(hours=1))
        ret = fleming.floor(t, year=1)
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 1, 1, tzinfo=ret.tzinfo))

    def test_aware_floor_month_out_of_dst(self):
        """
        Tests flooring an aware datetime to a month and returning an aware datetime.
        Floor starts in DST and goes out of DST.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 3, 14, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(hours=1))
        ret = fleming.floor(t, month=1)
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 3, 1, tzinfo=ret.tzinfo))

    def test_aware_floor_month_into_dst(self):
        """
        Tests flooring an aware datetime to a month and returning an aware datetime.
        Floor starts out of DST and goes into DST.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 11, 14, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(hours=0))
        ret = fleming.floor(t, month=1)
        # Resulting time zone should be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(hours=1))
        self.assertEquals(ret, datetime.datetime(2013, 11, 1, tzinfo=ret.tzinfo))

    def test_naive_floor_within_tz_day(self):
        """
        Tests the flooring of a naive datetime to a day within another timezone.
        """
        t = datetime.datetime(2013, 4, 1)
        # t is in midnight UTC, but it is still in the previous day for EST.
        ret = fleming.floor(t, day=1, within_tz=pytz.timezone('US/Eastern'))
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
        ret = fleming.floor(t, day=1, within_tz=pytz.timezone('US/Eastern'), return_naive=True)
        # The return value should be for the last day of the previous month, and the
        # timezone should still be in UTC
        self.assertEquals(ret, datetime.datetime(2013, 3, 31))

    def test_est_floor_within_cst_day(self):
        """
        Tests flooring of an EST time with respect to CST. Returns an aware datetime in EST.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 4, 1, 4), pytz.timezone('US/Eastern'))
        # Verify it is midnight for eastern time
        self.assertEquals(t.hour, 0)

        # Floor the time to a day with respect to CST. Since CST is an hour behind, the day
        # should be minus one
        ret = fleming.floor(t, day=1, within_tz=pytz.timezone('US/Central'))
        self.assertEquals(ret, datetime.datetime(2013, 3, 31, tzinfo=t.tzinfo))

    def test_utc_floor_within_est_week(self):
        """
        Tests the case where it is the starting of a week in UTC but the floor is
        performed relative to EST, meaning the result should be for the previous week.
        """
        t = datetime.datetime(2013, 4, 8, tzinfo=pytz.utc)
        ret = fleming.floor(t, week=1, within_tz=pytz.timezone('US/Eastern'))
        # The time should be a week earlier in UTC
        self.assertEquals(ret, datetime.datetime(2013, 4, 1, tzinfo=pytz.utc))

    def test_est_floor_within_utc_week(self):
        """
        Tests the case where it is the starting of a week in EST and the floor is
        performed relative to UTC, meaning the result should be for the next week.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 11, 4, 4), pytz.timezone('US/Eastern'))
        # Affirm that the time is 11 PM in EST
        self.assertEquals(t.day, 3)
        self.assertEquals(t.hour, 23)
        ret = fleming.floor(t, week=1, within_tz=pytz.utc)
        # The time should be a week later in EST since UTC was a week ahead
        self.assertEquals(ret, datetime.datetime(2013, 11, 4, tzinfo=t.tzinfo))

    def test_trimonth_floor(self):
        """
        Tests flooring to a trimonth (quarter).
        """
        t = datetime.datetime(2013, 5, 2)
        ret = fleming.floor(t, month=3)
        # The result should be at the beginning of the second quarter
        self.assertEquals(ret, datetime.datetime(2013, 4, 1, tzinfo=pytz.utc))

    def test_quadday_floor(self):
        """
        Tests flooring to every fourth day of a month.
        """
        t = datetime.datetime(2013, 5, 6)
        ret = fleming.floor(t, day=4)
        self.assertEquals(ret, datetime.datetime(2013, 5, 5, tzinfo=pytz.utc))

    def test_halfday_floor(self):
        """
        Tests flooring to a half day.
        """
        t = datetime.datetime(2013, 5, 6, 14)
        ret = fleming.floor(t, hour=12)
        self.assertEquals(ret, datetime.datetime(2013, 5, 6, 12, tzinfo=pytz.utc))

    def test_trimonth_triday_floor(self):
        """
        Floors to the nearest quarter and triday of the month.
        """
        t = datetime.datetime(2013, 1, 8)
        ret = fleming.floor(t, month=3, day=3)
        self.assertEquals(ret, datetime.datetime(2013, 1, 7, tzinfo=pytz.utc))

    def test_no_floor(self):
        """
        Tests that the original time is returned when no floor values are present.
        """
        t = datetime.datetime(2013, 4, 6, 7, 8)
        ret = fleming.floor(t)
        self.assertEquals(ret, datetime.datetime(2013, 4, 6, 7, 8, tzinfo=pytz.utc))

    def test_invalid_week_value(self):
        """
        Tests when a number other than 1 is given for the week value.
        """
        t = datetime.datetime(2013, 4, 4)
        with self.assertRaises(ValueError):
            fleming.floor(t, week=2)


class TestUnixTime(unittest.TestCase):
    """
    Tests the unix_time function.
    """
    def test_unix_time_epoch(self):
        """
        Tests the unix_time function when the epoch is given.
        """
        t = datetime.datetime(1970, 1, 1)
        ret = fleming.unix_time(t)
        self.assertEquals(ret, 0)

    def test_unix_time_arbitrary_one(self):
        """
        Tests unix_time with an arbitrary time.
        datetime(2013, 4, 1, 2) was confirmed to be equal to
        1364781600 by epochconverter.com.
        """
        t = datetime.datetime(2013, 4, 1, 2)
        ret = fleming.unix_time(t)
        self.assertEquals(ret, 1364781600)

    def test_unix_time_arbitrary_two(self):
        """
        Tests unix_time with an arbitrary time.
        datetime(2013, 12, 1, 2) was confirmed to be equal to
        1385863200 by epochconverter.com.
        """
        t = datetime.datetime(2013, 12, 1, 2)
        ret = fleming.unix_time(t)
        self.assertEquals(ret, 1385863200)

    def test_unix_time_return_ms(self):
        """
        Tests unix_time when returning milliseconds. Uses the
        same values from test_unix_time_arbitrary_two.
        """
        t = datetime.datetime(2013, 12, 1, 2)
        ret = fleming.unix_time(t, return_ms=True)
        self.assertEquals(ret, 1385863200 * 1000)

    def test_unix_time_aware_arbitrary(self):
        """
        Tests unix time for an aware time.
        datetime(2013, 12, 1, 2) in EST was confirmed to be
        equal to 1385881200 by epochconverter.com.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 12, 1, 7), pytz.timezone('US/Eastern'))
        self.assertEquals(t.hour, 2)
        ret = fleming.unix_time(t)
        self.assertEquals(ret, 1385881200)

    def test_unix_time_aware_arbitrary_ms(self):
        """
        Tests unix time for an aware time.
        datetime(2013, 12, 1, 2) in EST was confirmed to be
        equal to 1385881200 by epochconverter.com. Return value is
        in milliseconds.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 12, 1, 7), pytz.timezone('US/Eastern'))
        self.assertEquals(t.hour, 2)
        ret = fleming.unix_time(t, return_ms=True)
        self.assertEquals(ret, 1385881200 * 1000)

    def test_unix_time_naive_within_tz(self):
        """
        Tests that a naive UTC time is converted relative to an EST tz.
        This means that when converting the time back, the time values are
        correct for the EST time zone.
        """
        t = datetime.datetime(2013, 12, 1, 5)
        ret = fleming.unix_time(t, within_tz=pytz.timezone('US/Eastern'))
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
        ret = fleming.unix_time(t, within_tz=pytz.timezone('US/Eastern'))
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
        ret = fleming.unix_time(t, within_tz=pytz.timezone('US/Eastern'), return_ms=True)
        self.assertEquals(ret, 1385856000 * 1000)
        # Convert it back to a datetime objects. The values should be for midnight
        # since it was an EST time
        t = datetime.datetime.fromtimestamp(ret / 1000)
        self.assertEquals(t.hour, 0)
        self.assertEquals(t.day, 1)


class TestIntervals(unittest.TestCase):
    """
    Tests the intervals function.
    """
    def test_naive_start_day_td_count_zero(self):
        """
        Tests the intervals function with a naive start_dt parameter with a timedelta of a day. Uses
        a count to get the range. Tests when the count is 0
        """
        intervals = fleming.intervals(datetime.datetime(2013, 3, 1), datetime.timedelta(days=1), count=0)
        self.assertEquals(list(intervals), [])

    def test_naive_start_day_td_count_one(self):
        """
        Tests the intervals function with a naive start_dt parameter with a timedelta of a day. Uses
        a count to get the range. Tests when the count is 1
        """
        intervals = fleming.intervals(datetime.datetime(2013, 3, 1), datetime.timedelta(days=1), count=1)
        self.assertEquals(list(intervals), [datetime.datetime(2013, 3, 1, tzinfo=pytz.utc)])

    def test_naive_start_day_td_count(self):
        """
        Tests the intervals function with a naive start_dt parameter with a timedelta of a day. Uses
        a count to get the range.
        """
        intervals = fleming.intervals(datetime.datetime(2013, 3, 1), datetime.timedelta(days=1), count=10)
        self.assertEquals(
            list(intervals), [
                datetime.datetime(2013, 3, 1, tzinfo=pytz.utc), datetime.datetime(2013, 3, 2, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 3, tzinfo=pytz.utc), datetime.datetime(2013, 3, 4, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 5, tzinfo=pytz.utc), datetime.datetime(2013, 3, 6, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 7, tzinfo=pytz.utc), datetime.datetime(2013, 3, 8, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 9, tzinfo=pytz.utc), datetime.datetime(2013, 3, 10, tzinfo=pytz.utc),
            ])

    def test_naive_start_day_td_count_return_naive(self):
        """
        Tests the intervals function with a naive start_dt parameter with a timedelta of a day. Uses
        a count to get the range. Returns objects as naive times.
        """
        intervals = fleming.intervals(
            datetime.datetime(2013, 3, 1), datetime.timedelta(days=1), count=10, return_naive=True)
        self.assertEquals(
            list(intervals), [
                datetime.datetime(2013, 3, 1), datetime.datetime(2013, 3, 2),
                datetime.datetime(2013, 3, 3), datetime.datetime(2013, 3, 4),
                datetime.datetime(2013, 3, 5), datetime.datetime(2013, 3, 6),
                datetime.datetime(2013, 3, 7), datetime.datetime(2013, 3, 8),
                datetime.datetime(2013, 3, 9), datetime.datetime(2013, 3, 10),
            ])

    def test_aware_start_day_td_count(self):
        """
        Tests the intervals function with an aware start_dt parameter with a timedelta of a day. Uses
        a count to get the range.
        """
        intervals = fleming.intervals(
            datetime.datetime(2013, 3, 1, tzinfo=pytz.utc), datetime.timedelta(days=1), count=10)
        self.assertEquals(
            list(intervals), [
                datetime.datetime(2013, 3, 1, tzinfo=pytz.utc), datetime.datetime(2013, 3, 2, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 3, tzinfo=pytz.utc), datetime.datetime(2013, 3, 4, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 5, tzinfo=pytz.utc), datetime.datetime(2013, 3, 6, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 7, tzinfo=pytz.utc), datetime.datetime(2013, 3, 8, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 9, tzinfo=pytz.utc), datetime.datetime(2013, 3, 10, tzinfo=pytz.utc),
            ])

    def test_est_start_day_td_count_dst_cross(self):
        """
        Tests with an EST start_dt parameter with a timedelta of a day. Uses a count to get the range.
        This function crosses a DST border.
        """
        est_no_dst = pytz.timezone('US/Eastern')
        est_dst = fleming.convert_to_tz(datetime.datetime(2013, 3, 20), est_no_dst).tzinfo
        start_dt = fleming.convert_to_tz(datetime.datetime(2013, 3, 5, 5), est_no_dst)
        intervals = fleming.intervals(start_dt, datetime.timedelta(days=1), count=10)
        self.assertEquals(
            list(intervals), [
                datetime.datetime(2013, 3, 5, tzinfo=est_no_dst), datetime.datetime(2013, 3, 6, tzinfo=est_no_dst),
                datetime.datetime(2013, 3, 7, tzinfo=est_no_dst), datetime.datetime(2013, 3, 8, tzinfo=est_no_dst),
                datetime.datetime(2013, 3, 9, tzinfo=est_no_dst), datetime.datetime(2013, 3, 10, tzinfo=est_no_dst),
                datetime.datetime(2013, 3, 11, tzinfo=est_dst), datetime.datetime(2013, 3, 12, tzinfo=est_dst),
                datetime.datetime(2013, 3, 13, tzinfo=est_dst), datetime.datetime(2013, 3, 14, tzinfo=est_dst),
            ])

    def test_est_start_arbitrary_td_count(self):
        """
        Tests with an EST start_dt parameter with an arbitrary timedelta. Uses a count to get the range.
        """
        est = pytz.timezone('US/Eastern')
        start_dt = fleming.convert_to_tz(datetime.datetime(2013, 2, 5, 5), est)
        intervals = fleming.intervals(start_dt, datetime.timedelta(days=1, hours=1), count=10)
        self.assertEquals(
            list(intervals), [
                datetime.datetime(2013, 2, 5, tzinfo=est), datetime.datetime(2013, 2, 6, 1, tzinfo=est),
                datetime.datetime(2013, 2, 7, 2, tzinfo=est), datetime.datetime(2013, 2, 8, 3, tzinfo=est),
                datetime.datetime(2013, 2, 9, 4, tzinfo=est), datetime.datetime(2013, 2, 10, 5, tzinfo=est),
                datetime.datetime(2013, 2, 11, 6, tzinfo=est), datetime.datetime(2013, 2, 12, 7, tzinfo=est),
                datetime.datetime(2013, 2, 13, 8, tzinfo=est), datetime.datetime(2013, 2, 14, 9, tzinfo=est),
            ])

    def test_naive_within_est_day_td_dst_cross(self):
        """
        Tests with a naive start doing the range within another timezone while crossing a dst border.
        """
        start_dt = datetime.datetime(2013, 3, 5, tzinfo=pytz.utc)
        intervals = fleming.intervals(
            start_dt, datetime.timedelta(days=1), count=10, within_tz=pytz.timezone('US/Eastern'))
        self.assertEquals(
            list(intervals), [
                datetime.datetime(2013, 3, 5, tzinfo=pytz.utc), datetime.datetime(2013, 3, 6, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 7, tzinfo=pytz.utc), datetime.datetime(2013, 3, 8, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 9, tzinfo=pytz.utc), datetime.datetime(2013, 3, 10, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 10, 23, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 11, 23, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 12, 23, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 13, 23, tzinfo=pytz.utc),
            ])

    def test_naive_start_day_td_stop_dt(self):
        """
        Tests the intervals function with a naive start_dt parameter with a timedelta of a day. Uses
        a stop_dt to get the range.
        """
        intervals = fleming.intervals(
            datetime.datetime(2013, 3, 1), datetime.timedelta(days=1), stop_dt=datetime.datetime(2013, 3, 11))
        self.assertEquals(
            list(intervals), [
                datetime.datetime(2013, 3, 1, tzinfo=pytz.utc), datetime.datetime(2013, 3, 2, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 3, tzinfo=pytz.utc), datetime.datetime(2013, 3, 4, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 5, tzinfo=pytz.utc), datetime.datetime(2013, 3, 6, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 7, tzinfo=pytz.utc), datetime.datetime(2013, 3, 8, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 9, tzinfo=pytz.utc), datetime.datetime(2013, 3, 10, tzinfo=pytz.utc),
            ])

    def test_naive_start_day_td_stop_dt_inclusive(self):
        """
        Tests the intervals function with a naive start_dt parameter with a timedelta of a day. Uses
        an inclusive stop_dt to get the range.
        """
        intervals = fleming.intervals(
            datetime.datetime(2013, 3, 1), datetime.timedelta(days=1), stop_dt=datetime.datetime(2013, 3, 11),
            is_stop_dt_inclusive=True)
        self.assertEquals(
            list(intervals), [
                datetime.datetime(2013, 3, 1, tzinfo=pytz.utc), datetime.datetime(2013, 3, 2, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 3, tzinfo=pytz.utc), datetime.datetime(2013, 3, 4, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 5, tzinfo=pytz.utc), datetime.datetime(2013, 3, 6, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 7, tzinfo=pytz.utc), datetime.datetime(2013, 3, 8, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 9, tzinfo=pytz.utc), datetime.datetime(2013, 3, 10, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 11, tzinfo=pytz.utc),
            ])

    def test_naive_start_day_td_aware_stop_dt_inclusive(self):
        """
        Tests the intervals function with a naive start_dt parameter with a timedelta of a day. Uses
        an inclusive stop_dt to get the range. The stop_dt is aware and in EST
        """
        intervals = fleming.intervals(
            datetime.datetime(2013, 3, 1), datetime.timedelta(days=1),
            stop_dt=fleming.convert_to_tz(datetime.datetime(2013, 3, 11, 4), pytz.timezone('US/Eastern')),
            is_stop_dt_inclusive=True)
        self.assertEquals(
            list(intervals), [
                datetime.datetime(2013, 3, 1, tzinfo=pytz.utc), datetime.datetime(2013, 3, 2, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 3, tzinfo=pytz.utc), datetime.datetime(2013, 3, 4, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 5, tzinfo=pytz.utc), datetime.datetime(2013, 3, 6, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 7, tzinfo=pytz.utc), datetime.datetime(2013, 3, 8, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 9, tzinfo=pytz.utc), datetime.datetime(2013, 3, 10, tzinfo=pytz.utc),
                datetime.datetime(2013, 3, 11, tzinfo=pytz.utc),
            ])


class TestCeil(unittest.TestCase):
    """
    Tests the ceil function.
    """
    def test_naive_ceil_year(self):
        """
        Tests ceiling a naive datetime to a year and returning an aware datetime.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = fleming.ceil(t, year=1)
        self.assertEquals(t, datetime.datetime(2014, 1, 1, tzinfo=pytz.utc))

    def test_naive_ceil_month(self):
        """
        Tests ceiling a naive datetime to a month and returning an aware datetime.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = fleming.ceil(t, month=1)
        self.assertEquals(t, datetime.datetime(2013, 4, 1, tzinfo=pytz.utc))

    def test_naive_ceil_week_stays_in_month(self):
        """
        Tests ceiling a naive datetime to a week where the month value remains the same.
        Returns an aware datetime.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = fleming.ceil(t, week=1)
        self.assertEquals(t, datetime.datetime(2013, 3, 11, tzinfo=pytz.utc))

    def test_naive_ceil_week_goes_to_next_month(self):
        """
        Tests ceiling a naive datetime to a week where the month value goes forwards.
        Return value is aware.
        """
        t = datetime.datetime(2013, 3, 31, 12, 23, 4, 40)
        t = fleming.ceil(t, week=1)
        self.assertEquals(t, datetime.datetime(2013, 4, 1, tzinfo=pytz.utc))

    def test_naive_ceil_day(self):
        """
        Tests ceiling a naive datetime to a day. Return value is aware.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = fleming.ceil(t, day=1)
        self.assertEquals(t, datetime.datetime(2013, 3, 5, tzinfo=pytz.utc))

    def test_naive_ceil_day_next_month(self):
        """
        Tests ceiling a naive datetime to a day when it crosses to the next month. Return value is aware.
        """
        t = datetime.datetime(2013, 2, 28, 12, 23, 4, 40)
        t = fleming.ceil(t, day=1)
        self.assertEquals(t, datetime.datetime(2013, 3, 1, tzinfo=pytz.utc))

    def test_naive_ceil_day_return_naive(self):
        """
        Tests ceiling a naive datetime to a day. Return value is naive.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = fleming.ceil(t, day=1, return_naive=True)
        self.assertEquals(t, datetime.datetime(2013, 3, 5))

    def test_naive_ceil_hour(self):
        """
        Tests ceiling a naive datetime to an hour. Return value is aware
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = fleming.ceil(t, hour=1)
        self.assertEquals(t, datetime.datetime(2013, 3, 4, 13, tzinfo=pytz.utc))

    def test_naive_ceil_minute(self):
        """
        Tests ceiling a naive datetime to a minute. Return value is aware.
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = fleming.ceil(t, minute=1)
        self.assertEquals(t, datetime.datetime(2013, 3, 4, 12, 24, tzinfo=pytz.utc))

    def test_naive_ceil_second(self):
        """
        Tests ceiling a naive datetime to a minute. Return value is aware
        """
        t = datetime.datetime(2013, 3, 4, 12, 23, 4, 40)
        t = fleming.ceil(t, second=1)
        self.assertEquals(t, datetime.datetime(2013, 3, 4, 12, 23, 5, tzinfo=pytz.utc))

    def test_aware_ceil_year(self):
        """
        Tests ceiling an aware datetime to a year and returning an aware datetime.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = fleming.ceil(t, year=1)
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2014, 1, 1, tzinfo=t.tzinfo))

    def test_aware_ceil_month(self):
        """
        Tests ceiling an aware datetime to a month and returning an aware datetime.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = fleming.ceil(t, month=1)
        # Resulting time zone should be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(hours=1))
        self.assertEquals(ret, datetime.datetime(2013, 4, 1, tzinfo=ret.tzinfo))

    def test_aware_ceil_week_stays_in_month(self):
        """
        Tests ceiling an aware datetime to a week where the month value remains the same.
        Returns an aware datetime.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = fleming.ceil(t, week=1)
        # Resulting time zone should be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(hours=1))
        self.assertEquals(ret, datetime.datetime(2013, 3, 11, tzinfo=ret.tzinfo))

    def test_aware_ceil_week_goes_to_next_month(self):
        """
        Tests flooring an aware datetime to a week where the month value goes forwards.
        Return value is aware.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 3, 31, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(hours=1))
        ret = fleming.ceil(t, week=1)
        # Resulting time zone should be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(hours=1))
        self.assertEquals(ret, datetime.datetime(2013, 4, 1, tzinfo=t.tzinfo))

    def test_aware_ceil_day(self):
        """
        Tests ceiling an aware datetime to a day. Return value is aware.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = fleming.ceil(t, day=1)
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 3, 5, tzinfo=t.tzinfo))

    def test_aware_ceil_day_return_naive(self):
        """
        Tests ceiling an aware datetime to a day. Return value is naive.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = fleming.ceil(t, day=1, return_naive=True)
        self.assertEquals(ret, datetime.datetime(2013, 3, 5))

    def test_aware_ceil_hour(self):
        """
        Tests ceiling an aware datetime to an hour. Return value is aware
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = fleming.ceil(t, hour=1)
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 3, 4, t.hour + 1, tzinfo=t.tzinfo))

    def test_aware_ceil_minute(self):
        """
        Tests ceiling an aware datetime to a minute. Return value is aware.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = fleming.ceil(t, minute=1)
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 3, 4, t.hour, 24, tzinfo=t.tzinfo))

    def test_aware_ceil_second(self):
        """
        Tests ceiling an aware datetime to a minute. Return value is aware
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 3, 4, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(0))
        ret = fleming.ceil(t, second=1)
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 3, 4, t.hour, 23, 5, tzinfo=t.tzinfo))

    def test_aware_ceil_year_out_of_dst(self):
        """
        Tests ceiling an aware datetime to a year and returning an aware datetime.
        Floor starts in DST and goes out of DST.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 3, 14, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(hours=1))
        ret = fleming.ceil(t, year=1)
        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2014, 1, 1, tzinfo=ret.tzinfo))

    def test_aware_ceil_month_out_of_dst(self):
        """
        Tests ceiling an aware datetime to a month and returning an aware datetime.
        Floor starts in DST and goes out of DST.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 11, 1, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(hours=1))
        ret = fleming.ceil(t, month=1)

        # Resulting time zone should not be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(0))
        self.assertEquals(ret, datetime.datetime(2013, 12, 1, tzinfo=ret.tzinfo))

    def test_aware_ceil_month_into_dst(self):
        """
        Tests ceiling an aware datetime to a month and returning an aware datetime.
        Floor starts out of DST and goes into DST.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 3, 1, 12, 23, 4, 40), pytz.timezone('US/Eastern'))
        # Original time zone should not be in DST
        self.assertEquals(t.tzinfo.dst(t), datetime.timedelta(hours=0))
        ret = fleming.ceil(t, month=1)
        # Resulting time zone should be in DST
        self.assertEquals(ret.tzinfo.dst(ret), datetime.timedelta(hours=1))
        self.assertEquals(ret, datetime.datetime(2013, 4, 1, tzinfo=ret.tzinfo))

    def test_naive_ceil_within_tz_day(self):
        """
        Tests the ceiling of a naive datetime to a day within another timezone.
        """
        t = datetime.datetime(2013, 4, 1, 23)
        # t is the first in UTC, but it is the next day in Germany.
        ret = fleming.ceil(t, day=1, within_tz=pytz.timezone('Europe/Berlin'))
        # The return value should be for April 3, and the timezone should still be in UTC
        self.assertEquals(ret, datetime.datetime(2013, 4, 3, tzinfo=pytz.utc))

    def test_naive_ceil_within_est_no_diff(self):
        """
        Tests the ceiling of a month relative to another timezone when it is still
        that month in the other timezone.
        """
        t = datetime.datetime(2013, 3, 2)
        ret = fleming.ceil(t, month=1, within_tz=pytz.timezone('US/Eastern'))
        # The return value should be the start of the next month
        self.assertEquals(ret, datetime.datetime(2013, 4, 1, tzinfo=pytz.utc))

    def test_naive_ceil_within_est_diff(self):
        """
        Tests the ceiling of a month relative to another timezone when it is another
        month in that other timezone.
        """
        t = datetime.datetime(2013, 3, 1)
        ret = fleming.ceil(t, month=1, within_tz=pytz.timezone('US/Eastern'))
        # The return value should be the start of March since it was still Feb in EST
        self.assertEquals(ret, datetime.datetime(2013, 3, 1, tzinfo=pytz.utc))

    def test_cst_ceil_within_est_day(self):
        """
        Tests ceiling of an CST time with respect to EST. Returns an aware datetime in EST.
        """
        t = fleming.convert_to_tz(
            datetime.datetime(2013, 4, 1, 4, 2), pytz.timezone('US/Central'))
        # Verify it is 11pm for central time
        self.assertEquals(t.hour, 23)

        # Floor the time to a day with respect to EST. Since EST is an hour ahead, the day
        # should be plus two of the original day (March 31)
        ret = fleming.ceil(t, day=1, within_tz=pytz.timezone('US/Eastern'))
        self.assertEquals(ret, datetime.datetime(2013, 4, 2, tzinfo=t.tzinfo))

    def test_utc_ceil_within_berlin_week(self):
        """
        Tests the case where it is the starting of a week in UTC but the ceil is
        performed relative to Berlin, meaning the result should be for the next week.
        """
        t = datetime.datetime(2013, 4, 14, 23, tzinfo=pytz.utc)
        ret = fleming.ceil(t, week=1, within_tz=pytz.timezone('Europe/Berlin'))
        # The time should be a week later in UTC
        self.assertEquals(ret, datetime.datetime(2013, 4, 22, tzinfo=pytz.utc))

    def test_trimonth_ceil(self):
        """
        Tests ceiling to a trimonth (quarter).
        """
        t = datetime.datetime(2013, 11, 2)
        ret = fleming.ceil(t, month=3)
        # The result should be at the beginning of the next quarter
        self.assertEquals(ret, datetime.datetime(2014, 1, 1, tzinfo=pytz.utc))

    def test_quadday_ceil(self):
        """
        Tests ceiling to every fourth day of a month.
        """
        t = datetime.datetime(2013, 5, 6)
        ret = fleming.ceil(t, day=4)
        self.assertEquals(ret, datetime.datetime(2013, 5, 9, tzinfo=pytz.utc))

    def test_halfday_ceil(self):
        """
        Tests ceiling to a half day.
        """
        t = datetime.datetime(2013, 5, 6, 11)
        ret = fleming.ceil(t, hour=12)
        self.assertEquals(ret, datetime.datetime(2013, 5, 6, 12, tzinfo=pytz.utc))

    def test_trimonth_triday_ceil(self):
        """
        Floors to the next quarter and triday of the month.
        """
        t = datetime.datetime(2013, 1, 8)
        ret = fleming.ceil(t, month=3, day=3)
        self.assertEquals(ret, datetime.datetime(2013, 4, 1, tzinfo=pytz.utc))

    def test_no_ceil(self):
        """
        Tests that the original time is returned when no floor values are present.
        """
        t = datetime.datetime(2013, 4, 6, 7, 8)
        ret = fleming.ceil(t)
        self.assertEquals(ret, datetime.datetime(2013, 4, 6, 7, 8, tzinfo=pytz.utc))

    def test_invalid_week_value(self):
        """
        Tests when a number other than 1 is given for the week value.
        """
        t = datetime.datetime(2013, 4, 4)
        with self.assertRaises(ValueError):
            fleming.ceil(t, week=2)

    def test_ceil_year_on_boundary(self):
        """
        Tests ceil of a year that is already on the boundary. Should return the original time.
        """
        t = datetime.datetime(2013, 1, 1)
        ret = fleming.ceil(t, year=1)
        self.assertEquals(ret, datetime.datetime(2013, 1, 1, tzinfo=pytz.utc))

    def test_ceil_month_on_boundary(self):
        """
        Tests ceil of a month that is already on the boundary. Should return the original time.
        """
        t = datetime.datetime(2013, 5, 1)
        ret = fleming.ceil(t, month=1)
        self.assertEquals(ret, datetime.datetime(2013, 5, 1, tzinfo=pytz.utc))

    def test_ceil_aware_month_on_boundary(self):
        """
        Tests ceil of an aware month that is already on the boundary in its timezone. Should return the original time.
        """
        t = fleming.convert_to_tz(datetime.datetime(2013, 5, 1, 4, tzinfo=pytz.utc), pytz.timezone('US/Eastern'))
        self.assertEquals(t.day, 1)
        self.assertEquals(t.hour, 0)
        self.assertEquals(t.month, 5)
        ret = fleming.ceil(t, month=1)
        self.assertEquals(ret, datetime.datetime(2013, 5, 1, tzinfo=t.tzinfo))

    def test_ceil_naive_within_tz_on_boundary(self):
        """
        Tests ceil of a naive time when its within_tz equivalent is on the boundary of the ceil (in this case,
        a month).
        """
        t = datetime.datetime(2013, 5, 1, 4)
        ret = fleming.ceil(t, month=1, within_tz=pytz.timezone('US/Eastern'))
        self.assertEquals(ret, datetime.datetime(2013, 5, 1, tzinfo=pytz.utc))
