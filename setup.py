from distutils.core import setup

setup(
    name='python-datetime-helpers',
    version='0.1',
    packages=['datetime_helpers'],
    url='https://github.com/ambitioninc/datetime_helpers',
    description='Python helpers for manipulating datetime objects in local time zones',
    install_requires=['pytz==2012h'],
    test_suite='nose.collector',
    tests_require=['nose'],
)
