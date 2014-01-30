Gnip-Python-Search-API-Utilities
================================


Install with `pip install gapi`

This package includes two utilities:
 - Simple Gnip Search API interactions
 - Paging back to 30 days for 1 or more filters (WARNING: this will make many API requests very quickly!)


## Search API

<pre>
$ ./search_api.py 
usage: search_api.py [-h] [-f FILTER] [-l STREAM_URL] [-c] [-s START] [-e END]
                     [-q] [-u USER] [-p PWD] [-n MAX]
                     USE_CASE
search_api.py: error: too few arguments
jmontague:~/gnip/Gnip-Python-Search-API-Utilities$ ./search_api.py -h
usage: search_api.py [-h] [-f FILTER] [-l STREAM_URL] [-c] [-s START] [-e END]
                     [-q] [-u USER] [-p PWD] [-n MAX]
                     USE_CASE

GnipSearch supports the following use cases: ['json', 'wordcount', 'users',
'rate', 'links', 'timeline']

positional arguments:
  USE_CASE              Use case for this search.

optional arguments:
  -h, --help            show this help message and exit
  -f FILTER, --filter FILTER
                        PowerTrack filter rule (See: http://support.gnip.com/c
                        ustomer/portal/articles/901152-powertrack-operators)
  -l STREAM_URL, --stream-url STREAM_URL
                        Url of search endpoint. (See your Gnip console.)
  -c, --count           Return comma-separated 'date,counts' when using a
                        counts.json endpoint.
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

</pre>

<pre>
$ ./search_api.py -p XXXX -f"from:drskippy27" rate
------------------------------------------------------------
   PowerTrack Rule: "from:drskippy27"
Oldest Tweet (UTC): 2013-08-29 14:24:51
         Now (UTC): 2013-09-27 22:27:21
         55 Tweets:  0.078 Tweets/Hour
------------------------------------------------------------
</pre>

<pre>
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
</pre>
<pre>
$ ./search_api.py -pXXX -f"from:jrmontag" -s"2014-01-01T00:00" -e"2014-01-15T00:00" json
{"body": "Bring on the #sochi #olympics. @gnip now delivering data from Russia's biggest social network. http://t.co/nUFMC8GcTC", "retweetCount": 0, "generator": {"link": "https://about.twitter.com/products/tweetdeck", "displayName": "TweetDeck"}, "twitter_filter_level": "medium", "gnip": {"language": {"value": "en"}, "urls": [{"url": "http://t.co/nUFMC8GcTC", "expanded_status": 200, "expanded_url": "http://adage.com/abstract?article_id=291068"}], "profileLocations": [{"displayName": "Boulder, Colorado, United States", "address": {"country": "United States", "region": "Colorado", "subRegion": "Boulder County", "countryCode": "US", "locality": "Boulder"}, "geo": {"type": "point", "coordinates": [-105.27055, 40.01499]}, "objectType": "place"}]}, "favoritesCount": 0, "object": {"postedTime": "2014-01-14T19:14:58.000Z", "summary": "Bring on the #sochi #olympics. @gnip now delivering data from Russia's biggest social network. http://t.co/nUFMC8GcTC", "link": "http://twitter.com/jrmontag/statuses/423171400799506432", "id": "object:search.twitter.com,2005:423171400799506432", "objectType": "note"}, "actor": {"preferredUsername": "jrmontag", "displayName": "Josh", "links": [{"href": "http://about.me/joshmontague", "rel": "me"}], "twitterTimeZone": "Mountain Time (US & Canada)", "image": "https://pbs.twimg.com/profile_images/378800000733631857/ae9fe362605ca63c1acbb93f1778592f_normal.jpeg", "verified": false, "location": {"displayName": "Boulder / Golden", "objectType": "place"}, "statusesCount": 29789, "summary": "data @gnip \r\n(and other stuff!)", "languages": ["en"], "utcOffset": "-25200", "link": "http://www.twitter.com/jrmontag", "followersCount": 1806, "favoritesCount": 568, "friendsCount": 1987, "listedCount": 161, "postedTime": "2009-06-15T20:33:22.000Z", "id": "id:twitter.com:47436444", "objectType": "person"}, "twitter_lang": "en", "twitter_entities": {"symbols": [], "user_mentions": [{"id": 16958875, "indices": [31, 36], "id_str": "16958875", "screen_name": "gnip", "name": "Gnip, Inc."}], "hashtags": [{"indices": [13, 19], "text": "sochi"}, {"indices": [20, 29], "text": "olympics"}], "urls": [{"url": "http://t.co/nUFMC8GcTC", "indices": [95, 117], "expanded_url": "http://bit.ly/1a4ycTy", "display_url": "bit.ly/1a4ycTy"}]}, "verb": "post", "link": "http://twitter.com/jrmontag/statuses/423171400799506432", "provider": {"link": "http://www.twitter.com", "displayName": "Twitter", "objectType": "service"}, "postedTime": "2014-01-14T19:14:58.000Z", "id": "tag:search.twitter.com,2005:423171400799506432", "objectType": "activity"}
...
</pre>

<pre>
$ ./search_api.py -pXXXX -f"bieber" -s"2014-01-20T00:00" -e"2014-01-25T00:00" timeline -c
2014-01-20T00:00:00,9516
2014-01-20T01:00:00,9879
2014-01-20T02:00:00,9337
2014-01-20T03:00:00,9983
2014-01-20T04:00:00,10284
2014-01-20T05:00:00,8306
2014-01-20T06:00:00,6750
2014-01-20T07:00:00,5245
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

