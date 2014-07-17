from distutils.core import setup

setup(
    name='gapi',
    version='0.6.1',
    author='Scott Hendrickson, Josh Montague',
    author_email='scott@drskippy.net',
    packages=[],
    scripts=['search_api.py', 'paged_search_api.py'],
    url='https://github.com/DrSkippy27/Gnip-Python-Search-API-Utilities',
    download_url='https://github.com/DrSkippy27/Gnip-Python-Search-API-Utilities/tags/',
    license='LICENSE.txt',
    description='Simple utilties to to explore the Gnip search API',
    install_requires=[
        "gnacs > 0.9.0",
        "sngrams > 0.1.0",
        "requests > 1.2.2"
        ]
    )
