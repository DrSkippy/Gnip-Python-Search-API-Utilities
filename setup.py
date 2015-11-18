from distutils.core import setup

setup(
    name='gapi',
    version='1.0.0',
    author='Scott Hendrickson, Josh Montague, Jeff Kolb',
    author_email='scott@drskippy.net',
    packages=['search'],
    scripts=['gnip_search.py', 'gnip_time_series.py'],
    url='https://github.com/DrSkippy27/Gnip-Python-Search-API-Utilities',
    download_url='https://github.com/DrSkippy27/Gnip-Python-Search-API-Utilities/tags/',
    license='LICENSE.txt',
    description='Simple utilties to to explore the Gnip search API',
    install_requires=[
        "gnacs >= 1.0.0"
        , "sngrams >= 0.1.5"
        , "requests > 2.2.0"
        ],
    extras_require = {
        'timeseries':  ["numpy >= 1.10.1"
                , "scipy >= 0.16.1"
                , "statsmodels >= 0.6.1"
                , "matplotlib >= 1.5.0"
                , "pandas >= 0.17.0"
                ],
        }
    )
