from distutils.core import setup

setup(
    name='datetime_helpers',
    version='0.1',
    packages=[
        'datetime_helpers',
    ],
    url='https://github.com/ambitioninc/datetime_helpers',
    description='Python helpers for manipulating datetime objects in local time zones',
    install_requires=[
        'pytz==2012h',
    ]
)
