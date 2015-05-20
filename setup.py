from distutils.core import setup

setup(
    name='gapi',
    version='0.7.2',
    author='Scott Hendrickson, Josh Montague',
    author_email='scott@drskippy.net',
    packages=['gnip_search'],
    scripts=['search_api.py','search.py'],
    url='https://github.com/DrSkippy27/Gnip-Python-Search-API-Utilities',
    download_url='https://github.com/DrSkippy27/Gnip-Python-Search-API-Utilities/tags/',
    license='LICENSE.txt',
    description='Simple utilties to to explore the Gnip search API',
    install_requires=[
        "gnacs >= 1.0.0"
        , "sngrams >= 0.1.5"
        , "requests > 2.2.0"
        ]
    )
