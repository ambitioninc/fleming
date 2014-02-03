from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='fleming',
    version='0.1',
    description='Python helpers for manipulating datetime objects relative to time zones',
    long_description=readme(),
    classifiers=[
      'Topic :: Utilities',
      'Topic :: Software Development :: Libraries :: Python Modules',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3.0',
      'Programming Language :: Python :: 3.1',
      'Programming Language :: Python :: 3.2',
      'Programming Language :: Python :: 3.3',
      'Programming Language :: Python :: 3.4',
    ],
    keywords='python datetime pytz timezone timedelta arithmetic floor conversion',
    url='https://github.com/ambitioninc/fleming',
    author='Wes Kendall',
    author_email='wesleykendall@gmail.com',
    license='MIT',
    packages=['fleming'],
    install_requires=['pytz==2012h'],
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    tests_require=['nose'],
)
