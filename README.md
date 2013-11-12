Gnip-Python-Search-API-Utilities
================================


Install with `pip install gapi`

This package includes two utilities:
 - Simple Gnip Search API interactions
 - Paging back to 30 days for 1 or more filters (WARNING: this will make many API requests very quickly!)


## Search API

<pre>
$ ./search_api.py -h
usage: search_api.py [-h] [-f FILTER] [-l STREAM_URL] [-s START] [-e END] [-q]
                     [-u USER] [-p PWD] [-n MAX]
                     USE_CASE

GnipSearch supports the following use cases: ['json', 'wordcount', 'users',
'rate', 'links']

positional arguments:
  USE_CASE              Use case for this search.

optional arguments:
  -h, --help            show this help message and exit
  -f FILTER, --filter FILTER
                        PowerTrack filter rule (See: http://support.gnip.com/c
                        ustomer/portal/articles/901152-powertrack-operators)
  -l STREAM_URL, --stream-url STREAM_URL
                        Url of search endpoint. (See your Gnip console.)
  -s START, --start-date START
                        Start of datetime window, format 'YYYY-mm-DDTHH:MM'
                        (default: 30 days ago)
  -e END, --end-date END
                        End of datetime window, format 'YYYY-mm-DDTHH:MM'
                        [Omit for most recent activities] (default: none)
  -q, --query           View API query (no data)
  -u USER, --user-name USER
                        User name
  -p PWD, --password PWD
                        Password
  -n MAX, --results-max MAX
                        Maximum results to return (default 100)
</pre>


<pre>
$ ./search_api.py -p XXXX -f"from:drskippy27" users
------------------------------------------------------------
                 terms --   mentions     activities (55)
------------------------------------------------------------
            drskippy27 --   55  100.00%   55  100.00%
------------------------------------------------------------


$ ./search_api.py -p XXXX -f"from:drskippy27" rate
------------------------------------------------------------
   PowerTrack Rule: "from:drskippy27"
Oldest Tweet (UTC): 2013-08-29 14:24:51
         Now (UTC): 2013-09-27 22:27:21
         55 Tweets:  0.078 Tweets/Hour
------------------------------------------------------------


$ ./search_api.py -p XXXX -f"from:drskippy27" wordcount
------------------------------------------------------------
                 terms --   mentions     activities (55)
------------------------------------------------------------
                  gnip --   24   4.67%   21  38.18%
                  data --   13   2.53%   12  21.82%
            datagotham --    9   1.75%    9  16.36%
                   via --    7   1.36%    7  12.73%
               twitter --    6   1.17%    6  10.91%
                  foul --    4   0.78%    1   1.82%
                  team --    4   0.78%    4   7.27%
                social --    4   0.78%    4   7.27%
                  best --    4   0.78%    4   7.27%
                people --    4   0.78%    3   5.45%
                search --    3   0.58%    3   5.45%
             mikedewar --    3   0.58%    3   5.45%
                 today --    3   0.58%    3   5.45%
               awesome --    3   0.58%    3   5.45%
                   nyc --    3   0.58%    3   5.45%
                  talk --    3   0.58%    3   5.45%
                  good --    3   0.58%    3   5.45%
                   out --    3   0.58%    3   5.45%
                   one --    3   0.58%    3   5.45%
                  need --    3   0.58%    3   5.45%
              via gnip --    5   1.09%    5   9.09%
          put together --    2   0.44%    2   3.64%
              hate xml --    2   0.44%    1   1.82%
            search api --    2   0.44%    2   3.64%
             gnip data --    2   0.44%    2   3.64%
           social data --    2   0.44%    2   3.64%
          social media --    2   0.44%    2   3.64%
            beard good --    1   0.22%    1   1.82%
            good build --    1   0.22%    1   1.82%
   powertrack filtered --    1   0.22%    1   1.82%
       companies using --    1   0.22%    1   1.82%
            brain cell --    1   0.22%    1   1.82%
             data loss --    1   0.22%    1   1.82%
         signal social --    1   0.22%    1   1.82%
            amp reader --    1   0.22%    1   1.82%
        ranking models --    1   0.22%    1   1.82%
             good jeff --    1   0.22%    1   1.82%
              gnip put --    1   0.22%    1   1.82%
           jud valeski --    1   0.22%    1   1.82%
           tshirt didn --    1   0.22%    1   1.82%
------------------------------------------------------------



$ ./search_api.py -p XXXX -f"from:drskippy27" json
------------------------------------------------------------
{"body": "RT @drewconway: Python + Hadoop http://t.co/Jrof4dIxDT awww, that snake and elephant love each other!", "retweetCount": 10, "generator": {"link": "http://www.tweetdeck.com", "displayName": "TweetDeck"}, "twitter_filter_level": "medium", "gnip": {"language": {"value": "en"}, "urls": [{"url": "http://t.co/Jrof4dIxDT", "expanded_url": "http://blog.mortardata.com/post/62334142398/hadoop-python-pig-trunk?utm_content=buffer8aaed&utm_source=buffer&utm_medium=twitter&utm_campaign=Buffer"}], "profileLocations": [{"displayName": "Brighton, Colorado, United States", "address": {"country": "United States", "region": "Colorado", "countryCode": "US", "locality": "Brighton"}, "geo": {"type": "point", "coordinates": [-104.82053, 39.98526]}, "objectType": "place"}]}, "favoritesCount": 0, "object": {"body": "Python + Hadoop http://t.co/Jrof4dIxDT awww, that snake and elephant love each other!", "generator": {"link": "http://tapbots.com/software/tweetbot/mac", "displayName": "Tweetbot for Mac"},
...
</pre>

## Paged Search

<pre>
$ echo "Nothing" | ./paged_search_api.py -h
usage: paged_search_api.py [-h] [-s STREAM_URL] [-f] [-u USER] [-p PWD]
                           [-n MAX]

Call API until all available results returned

optional arguments:
  -h, --help            show this help message and exit
  -s STREAM_URL, --stream-url STREAM_URL
                        Url of search endpoint. (See your Gnip console.)
  -f, --file            If set, create a file for each page in ./data (you
                        must create this directory before running)
  -u USER, --user-name USER
                        User name
  -p PWD, --password PWD
                        Password
  -n MAX, --results-max MAX
                        Maximum results to return (default 500)
</pre>


<pre>
$ cat rules.txt | ./paged_search_api.py -p XXXX 
Now retrieving 500 results up to 2013-09-03 16:38:02 (UTC)...
[{"body": "RT @CloudElements1: Interested in social media &amp; data streaming, HTTP streaming, geo-referencing and live code examples? Meetup w/ @gnip ht\u2026", "retweetCount": 1, "generator": {"link": "http://www.tweetdeck.com", "displayName": "TweetDeck"}, "twitter_filter_level": "medium", "gnip": {"language": {"value": "en"}, "urls": [{"url": "http://t.co/jhASyTC1mN", "expanded_url": "http://www.meetup.com/All-things-Cloud-PaaS-SaaS-PaaS-XaaS/events/124584092/"}], "profileLocations": [{"displayName": "Boulder, Colorado, United States",
...
</pre>

or use the `-f` flag to write to file.

