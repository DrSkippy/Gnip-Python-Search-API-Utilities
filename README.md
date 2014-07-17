Gnip Python Search API Utilities
================================


This package includes two utilities:
 - Simple Gnip Search API interactions
 - Paging back to 30 days for 1 or more filters (WARNING: this will make many API requests very quickly!)


#### Installation
Install from PyPI with `pip install gapi`

## Search API

Usage:

    ./search_api.py -h
    usage: search_api.py [-h] [-a] [-c] [-b COUNT_BUCKET] [-e END] [-f FILTER]
                         [-l STREAM_URL] [-n MAX] [-p PASSWORD] [-q] [-s START]
                         [-u USER] [-w OUTPUT_FILE_PATH]
                         USE_CASE

    GnipSearch supports the following use cases: ['json', 'wordcount', 'users',
    'rate', 'links', 'timeline', 'geo']

    positional arguments:
      USE_CASE              Use case for this search.

    optional arguments:
      -h, --help            show this help message and exit
      -a, --paged           Paged access to ALL available results (Warning: this
                            makes many requests)
      -c, --csv             Return comma-separated 'date,counts' or geo data.
      -b COUNT_BUCKET, --bucket COUNT_BUCKET
                            Bucket size for counts query. Options are day, hour,
                            minute (default is 'day').
      -e END, --end-date END
                            End of datetime window, format 'YYYY-mm-DDTHH:MM'
                            (default: most recent activities)
      -f FILTER, --filter FILTER
                            PowerTrack filter rule (See: http://support.gnip.com/c
                            ustomer/portal/articles/901152-powertrack-operators)
      -l STREAM_URL, --stream-url STREAM_URL
                            Url of search endpoint. (See your Gnip console.)
      -n MAX, --results-max MAX
                            Maximum results to return (default 100)
      -p PASSWORD, --password PASSWORD
                            Password
      -q, --query           View API query (no data)
      -s START, --start-date START
                            Start of datetime window, format 'YYYY-mm-DDTHH:MM'
                            (default: 30 days ago)
      -u USER, --user-name USER
                            User name
      -w OUTPUT_FILE_PATH, --output-file-path OUTPUT_FILE_PATH
                            Create files in ./OUTPUT-FILE-PATH. This path must
                            exists and will not be created. This options is
                            available only with -a option. Default is no output
                            files.


##Using a configuration file

To avoid entering the the -u, -p and -l options for every command, create a configuration file name ".gnip" 
in the directory where you will run the code. If this file contains the correct parameters, you can omit
this command line parameters.

Use this template:

    # export GNIP_CONFIG_FILE=<location and name of this file>
    #
    [creds]
    un = <email use for service>
    pwd = <password>

    [endpoint]
    # replace with your endpoint
    url = https://search.gnip.com/accounts/shendrickson/search/wayback.json

### Use cases

#### JSON

Return full, enriched, Activity Streams-format JSON payloads from the Search API endpoint.

    $ ./search_api.py -uXXX -pXXX -f"from:Gnip" json
    {"body": "RT @bbi: The #BigBoulder bloggers have been busy. Head to http://t.co/Rwve0dVA82 for recaps of the Sina Weibo, Tumblr &amp; Academic Research s\u2026", "retweetCount": 3, "generator": {"link": "http://twitter.com", "displayName": "Twitter Web Client"}, "twitter_filter_level": "medium", "gnip": {"klout_profile": {"link": "http://klout.com/user/id/651348", "topics": [{"link": "http://klout.com/topic/id/5144818194631006088", "displayName": "Software", "
    ...

*Notes* 

``-a`` option (paging) collects _all_ results before printing to stdout/file and also forces ``-n 500`` in request. 


#### Wordcount 

Return top 1- and 2-grams - with counts and document frequency - from matching activities. Can modify the settings within simple ngrams package (``sngrams``) to modify the range of output.

    $ ./search_api.py -uXXX -pXXX -f"world cup" -n200 wordcount
    ------------------------------------------------------------
                     terms --   mentions     activities (200)
    ------------------------------------------------------------
                     world --  203  11.41%  198  99.00%
                       cup --  203  11.41%  198  99.00%
                  ceremony --   46   2.59%   45  22.50%
                   opening --   45   2.53%   45  22.50%
                      fifa --   25   1.41%   25  12.50%
                      2014 --   22   1.24%   22  11.00%
                    brazil --   20   1.12%   19   9.50%
                  watching --   15   0.84%   12   6.00%
                     ready --   14   0.79%   14   7.00%
                   tonight --   11   0.62%   11   5.50%
                      game --   11   0.62%   11   5.50%
                      wait --   10   0.56%   10   5.00%
                   million --   10   0.56%    8   4.00%
                     first --   10   0.56%   10   5.00%
                 indonesia --   10   0.56%    2   1.00%
                      time --   10   0.56%    9   4.50%
             niallofficial --    9   0.51%    9   4.50%
                      here --    9   0.51%    9   4.50%
                majooooorr --    9   0.51%    9   4.50%
             braziiiilllll --    9   0.51%    9   4.50%
                 world cup --  198  12.54%  196  98.00%
          opening ceremony --   33   2.09%   33  16.50%
               cup opening --   23   1.46%   23  11.50%
                fifa world --   23   1.46%   23  11.50%
                  cup 2014 --   13   0.82%   13   6.50%
               ready world --   12   0.76%   12   6.00%
               cup tonight --   11   0.70%   11   5.50%
       niallofficial first --    9   0.57%    9   4.50%
           cima majooooorr --    9   0.57%    9   4.50%
        cmon braziiiilllll --    9   0.57%    9   4.50%
              tonight wait --    9   0.57%    9   4.50%
                  wait pra --    9   0.57%    9   4.50%
           majooooorr cmon --    9   0.57%    9   4.50%
                game world --    9   0.57%    9   4.50%
                  pra cima --    9   0.57%    9   4.50%
            watching world --    9   0.57%    7   3.50%
                first game --    9   0.57%    9   4.50%
       indonesia indonesia --    8   0.51%    2   1.00%
               watch world --    8   0.51%    8   4.00%
            ceremony world --    7   0.44%    7   3.50%
    ------------------------------------------------------------



#### Users 

Return the most common usernames occuring in matching activities

    $ ./search_api.py -uXXX -pXXX -f"obama" -n500 users
    ------------------------------------------------------------
                     terms --   mentions     activities (500)
    ------------------------------------------------------------
                tsalazar66 --    5   1.00%    5   1.00%
             sunnyherring1 --    5   1.00%    5   1.00%
             debwilliams57 --    3   0.60%    3   0.60%
                   tattooq --    2   0.40%    2   0.40%
                  carlanae --    2   0.40%    2   0.40%
                  miisslys --    2   0.40%    2   0.40%
              celtic_norse --    2   0.40%    2   0.40%
           tvkoolturaldgoh --    2   0.40%    2   0.40%
               tarynmorman --    2   0.40%    2   0.40%
            __coleston_s__ --    2   0.40%    2   0.40%
              alinka2linka --    2   0.40%    2   0.40%
            falakhzafrieyl --    2   0.40%    2   0.40%
              coolstoryluk --    2   0.40%    2   0.40%
              law_colorado --    2   0.40%    2   0.40%
            genelingerfelt --    2   0.40%    2   0.40%
             annerkissed69 --    2   0.40%    2   0.40%
             shotoftheweek --    2   0.40%    2   0.40%
                 matemary1 --    2   0.40%    2   0.40%
               orlando_ooh --    2   0.40%    2   0.40%
            c0nt0stavl0s__ --    2   0.40%    2   0.40%
    ------------------------------------------------------------



#### Rate 

Calculate the approximate activity rate from matched activities.

    $ ./search_api.py -uXXX -pXXX -f"from:jrmontag" -n500 rate
    ------------------------------------------------------------
       PowerTrack Rule: "from:jrmontag"
    Oldest Tweet (UTC): 2014-05-13 02:14:44
    Newest Tweet (UTC): 2014-06-12 18:41:44.306984
             Now (UTC): 2014-06-12 18:41:55
            254 Tweets:  0.345 Tweets/Hour
    ------------------------------------------------------------



#### Links 

Return the most frequently observed links - count and document frequency - in matching activities

    $ ./search_api.py -uXXX -pXXX -f"from:drskippy" -n500 links
    ---------------------------------------------------------------------------------------------------------------------------------
                                                                                                   links --   mentions     activities (31)
    ---------------------------------------------------------------------------------------------------------------------------------
                                                                                                 nolinks --    9  27.27%    9  26.47%
                                         http://twitter.com/mutualmind/status/476460889147600896/photo/1 --    1   3.03%    1   2.94%
                                              http://thenewinquiry.com/essays/the-anxieties-of-big-data/ --    1   3.03%    1   2.94%
      http://www.nytimes.com/2014/05/30/opinion/krugman-cutting-back-on-carbon.html?hp&rref=opinion&_r=0 --    1   3.03%    1   2.94%
                                           http://twitter.com/mdcin303/status/474991971170131968/photo/1 --    1   3.03%    1   2.94%
                                       http://twitter.com/notfromshrek/status/475034884189085696/photo/1 --    1   3.03%    1   2.94%
                                                                            https://github.com/dlwh/epic --    1   3.03%    1   2.94%
                                           http://twitter.com/jrmontag/status/471762525449900032/photo/1 --    1   3.03%    1   2.94%
                                               http://pandas.pydata.org/pandas-docs/stable/whatsnew.html --    1   3.03%    1   2.94%
                                      http://www.economist.com/blogs/graphicdetail/2014/06/daily-chart-1 --    1   3.03%    1   2.94%
          http://www.zdnet.com/google-turns-to-machine-learning-to-build-a-better-datacentre-7000029930/ --    1   3.03%    1   2.94%
                                    https://groups.google.com/forum/#!topic/scalanlp-discuss/bd9jhmm2nxc --    1   3.03%    1   2.94%
                                                                 http://www.ladamic.com/wordpress/?p=681 --    1   3.03%    1   2.94%
        http://www.linkedin.com/today/post/article/20140407232811-442872-do-your-analysts-really-analyze --    1   3.03%    1   2.94%
                                    http://twitter.com/giorgiocaviglia/status/474319737761980417/photo/1 --    1   3.03%    1   2.94%
                                http://faculty.washington.edu/kstarbi/starbird_iconference2014-final.pdf --    1   3.03%    1   2.94%
                                           http://twitter.com/drskippy/status/474903707407384576/photo/1 --    1   3.03%    1   2.94%
                                       http://en.wikipedia.org/wiki/lissajous_curve#logos_and_other_uses --    1   3.03%    1   2.94%
                                                                     http://datacolorado.com/knitr_test/ --    1   3.03%    1   2.94%
                                                                 http://opendata-hackday.de/?page_id=227 --    1   3.03%    1   2.94%
    ---------------------------------------------------------------------------------------------------------------------------------



#### Timeline 

Return a count timeline of matching activities. Without further options, results are returned in JSON format...

    $ ./search_api.py -uXXX -pXXX -f"@cia"  timeline
    {"results": [{"count": 32, "timePeriod": "201405130000"}, {"count": 31, "timePeriod": "201405140000"}, 

Results can be returned in comma-delimited format with the ``-c`` option:

    $ ./search_api.py -uXXX -pXXX -f"@cia"  timeline -c
    2014-05-13T00:00:00,32
    2014-05-14T00:00:00,31
    2014-05-15T00:00:00,23
    2014-05-16T00:00:00,81
    ...


And bucket size can be adjusted with ``-b``:

    $ ./search_api.py -uXXX -pXXX -f"@cia"  timeline -c -b hour
    ...
    2014-06-06T11:00:00,0
    2014-06-06T12:00:00,0
    2014-06-06T13:00:00,0
    2014-06-06T14:00:00,0
    2014-06-06T15:00:00,1
    2014-06-06T16:00:00,0
    2014-06-06T17:00:00,7234
    2014-06-06T18:00:00,77403
    2014-06-06T19:00:00,44704
    2014-06-06T20:00:00,38512
    2014-06-06T21:00:00,23463
    2014-06-06T22:00:00,17458
    2014-06-06T23:00:00,13352
    2014-06-07T00:00:00,12618
    2014-06-07T01:00:00,11373
    2014-06-07T02:00:00,10641
    2014-06-07T03:00:00,9457
    ...


#### Geo 
    
Return JSON payloads with the latitude, longitude, timestamp, and activity id for matching activities 

    $ ./search_api.py -uXXX -pXXX -f"vamos has:geo" geo 
    {"latitude": 4.6662819, "postedTime": "2014-06-12T18:52:48", "id": "477161613775351808", "longitude": -74.0557122}
    {"latitude": null, "postedTime": "2014-06-12T18:52:48", "id": "477161614354165760", "longitude": null}
    {"latitude": -24.4162955, "postedTime": "2014-06-12T18:52:47", "id": "477161609786568704", "longitude": -53.5296426}
    {"latitude": 14.66637167, "postedTime": "2014-06-12T18:52:47", "id": "477161607299342336", "longitude": -90.52661}
    {"latitude": -22.94064485, "postedTime": "2014-06-12T18:52:45", "id": "477161600429088769", "longitude": -43.05257938}
    ...


This can also be output in delimited format:

    $ ./search_api.py -uXXX -pXXX -f"vamos has:geo" geo -c 
    477161971364933632,2014-06-12T18:54:13,-6.350394,38.926667
    477161943015636992,2014-06-12T18:54:07,-46.60175585,-23.63230955
    477161939647623168,2014-06-12T18:54:06,-49.0363085,-26.6042339
    477161938833907712,2014-06-12T18:54:06,-1.5364198,53.9949317
    477161936938094592,2014-06-12T18:54:05,-76.06161259,1.84834405
    477161932806692865,2014-06-12T18:54:04,None,None
    477161928377516032,2014-06-12T18:54:03,-51.08593214,0.03778787

