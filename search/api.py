#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__="Scott Hendrickson, Josh Montague" 

import sys
import requests
import json
import codecs
import datetime
import time
import os
import re
import unicodedata

from acscsv.twitter_acs import TwacsCSV

## update for python3
if sys.version_info[0] == 2:
    reload(sys)
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    sys.stdin = codecs.getreader('utf-8')(sys.stdin)

#remove this
requests.packages.urllib3.disable_warnings()

# formatter of data from API 
TIME_FORMAT_SHORT = "%Y%m%d%H%M"
TIME_FORMAT_LONG = "%Y-%m-%dT%H:%M:%S.000Z"
PAUSE = 1 # seconds between page requests
POSTED_TIME_IDX = 1
#date time parsing utility regex
DATE_TIME_RE = re.compile("([0-9]{4}).([0-9]{2}).([0-9]{2}).([0-9]{2}):([0-9]{2})")

class Query(object):
    """Object represents a single search API query and provides utilities for
       managing parameters, executing the query and parsing the results."""
    
    def __init__(self
            , user
            , password
            , stream_url
            , paged = False
            , output_file_path = None
            , hard_max = None
            ):
        """A Query requires at least a valid user name, password and endpoint url.
           The URL of the endpoint should be the JSON records endpoint, not the counts
           endpoint.

           Additional parambers specifying paged search and output file path allow
           for making queries which return more than the 500 activity limit imposed by
           a single call to the API. This is called paging or paged search. Setting 
           paged = True will enable the token interpretation 
           functionality provided in the API to return a seamless set of activites.

           Once the object is created, it can be used for repeated access to the
           configured end point with the same connection configuration set at
           creation."""
        self.output_file_path = output_file_path
        self.paged = paged
        self.hard_max = hard_max
        self.paged_file_list = []
        self.user = user
        self.password = password
        self.end_point = stream_url # activities end point NOT the counts end point
        # get a parser for the twitter columns
        # TODO: use the updated retriveal methods in gnacs instead of this?
        self.twitter_parser = TwacsCSV(",", None, False, True, False, True, False, False, False)
        # Flag for post processing tweet timeline from tweet times
        self.tweet_times_flag = False

    def set_dates(self, start, end):
        """Utility function to set dates from strings. Given string-formated 
           dates for start date time and end date time, extract the required
           date string format for use in the API query and make sure they
           are valid dates. 

           Sets class fromDate and toDate date strings."""
        if start:
            dt = re.search(DATE_TIME_RE, start)
            if not dt:
                raise ValueError("Error. Invalid start-date format: %s \n"%str(start))
            else:
                f =''
                for i in range(re.compile(DATE_TIME_RE).groups):
                    f += dt.group(i+1) 
                self.fromDate = f
                # make sure this is a valid date
                tmp_start = datetime.datetime.strptime(f, TIME_FORMAT_SHORT)

        if end:
            dt = re.search(DATE_TIME_RE, end)
            if not dt:
                raise ValueError("Error. Invalid end-date format: %s \n"%str(end))
            else:
                e =''
                for i in range(re.compile(DATE_TIME_RE).groups):
                    e += dt.group(i+1) 
                self.toDate = e
                # make sure this is a valid date
                tmp_end = datetime.datetime.strptime(e, TIME_FORMAT_SHORT)
                if start:
                    if tmp_start >= tmp_end:
                        raise ValueError("Error. Start date greater than end date.\n")

    def name_munger(self, f):
        """Utility function to create a valid, friendly file name base 
           string from an input rule."""
        f = re.sub(' +','_',f)
        f = f.replace(':','_')
        f = f.replace('"','_Q_')
        f = f.replace('(','_p_') 
        f = f.replace(')','_p_') 
        self.file_name_prefix = unicodedata.normalize(
                "NFKD",f[:42]).encode(
                        "ascii","ignore")

    def request(self):
        """HTTP request based on class variables for rule_payload, 
           stream_url, user and password"""
        try:
            s = requests.Session()
            s.headers = {'Accept-encoding': 'gzip'}
            s.auth = (self.user, self.password)
            res = s.post(self.stream_url, data=json.dumps(self.rule_payload))
            if res.status_code != 200:
                sys.stderr.write("Exiting with HTTP error code {}\n".format(res.status_code))
                sys.stderr.write("ERROR Message: {}\n".format(res.json()["error"]["message"]))
                if 1==1: #self.return_incomplete:
                    sys.stderr.write("Returning incomplete dataset.")
                    return(res.content.decode(res.encoding))
                sys.exit(-1)
        except requests.exceptions.ConnectionError as e:
            e.msg = "Error (%s). Exiting without results."%str(e)
            raise e
        except requests.exceptions.HTTPError as e:
            e.msg = "Error (%s). Exiting without results."%str(e)
            raise e
        except requests.exceptions.MissingSchema as e:
            e.msg = "Error (%s). Exiting without results."%str(e)
            raise e
        #Don't use res.text as it creates encoding challenges!
        return(res.content.decode(res.encoding))

    def parse_responses(self, count_bucket):
        """Parse returned responses.

           When paged=True, manage paging using the API token mechanism
           
           When output file is set, write output files for paged output."""
        acs = []
        repeat = True
        page_count = 1
        self.paged_file_list = []
        while repeat:
            doc = self.request()
            tmp_response = json.loads(doc)
            if "results" in tmp_response:
                acs.extend(tmp_response["results"])
            else:
                raise ValueError("Invalid request\nQuery: %s\nResponse: %s"%(self.rule_payload, doc))
            if self.hard_max is None or len(acs) < self.hard_max:
                repeat = False
                if self.paged or count_bucket:
                    if len(acs) > 0:
                        if self.output_file_path is not None:
                            # writing to file
                            file_name = self.output_file_path + "/{0}_{1}.json".format(
                                    str(datetime.datetime.utcnow().strftime(
                                        "%Y%m%d%H%M%S"))
                                  , str(self.file_name_prefix))
                            with codecs.open(file_name, "wb","utf-8") as out:
                                for item in tmp_response["results"]:
                                    out.write(json.dumps(item)+"\n")
                            self.paged_file_list.append(file_name)
                            # if writing to file, don't keep track of all the data in memory
                            acs = []
                        else:
                            # storing in memory, so give some feedback as to size
                            sys.stderr.write("[{0:8d} bytes] {1:5d} total activities retrieved...\n".format(
                                                                sys.getsizeof(acs)
                                                              , len(acs)))
                    else:
                        sys.stderr.write( "No results returned for rule:{0}\n".format(str(self.rule_payload)) ) 
                    if "next" in tmp_response:
                        self.rule_payload["next"]=tmp_response["next"]
                        repeat = True
                        page_count += 1
                        sys.stderr.write( "Fetching page {}...\n".format(page_count) )
                    else:
                        if "next" in self.rule_payload:
                            del self.rule_payload["next"]
                        repeat = False
                    time.sleep(PAUSE)
            else:
                # stop iterating after reaching hard_max
                repeat = False
        return acs

    def get_time_series(self):
        if self.paged and self.output_file_path is not None:
            for file_name in self.paged_file_list:
                with codecs.open(file_name,"rb") as f:
                    for res in f:
                        rec = json.loads(res.decode('utf-8').strip())
                        t = datetime.datetime.strptime(rec["timePeriod"], TIME_FORMAT_SHORT)
                        yield [rec["timePeriod"], rec["count"], t]
        else:
            if self.tweet_times_flag:
                # todo: list of tweets, aggregate by bucket
                raise NotImplementedError("Aggregated buckets on json tweets not implemented!")
            else:
                for i in self.time_series:
                    yield i


    def get_activity_set(self):
        """Generator iterates through the entire activity set from memory or disk."""
        if self.paged and self.output_file_path is not None:
            for file_name in self.paged_file_list:
                with codecs.open(file_name,"rb") as f:
                    for res in f:
                        yield json.loads(res.decode('utf-8'))
        else:
            for res in self.rec_dict_list:
                yield res

    def get_list_set(self):
        """Like get_activity_set, but returns a list containing values parsed by 
           current Twacs parser configuration."""
        for rec in self.get_activity_set():
            yield self.twitter_parser.get_source_list(rec)

    def execute(self
            , pt_filter
            , max_results = 100
            , start = None
            , end = None
            , count_bucket = None # None is json
            , show_query = False):
        """Execute a query with filter, maximum results, start and end dates.

           Count_bucket determines the bucket size for the counts endpoint.
           If the count_bucket variable is set to a valid bucket size such 
           as mintute, day or week, then the acitivity counts endpoint will 
           Otherwise, the data endpoint is used."""
        # set class start and stop datetime variables
        self.set_dates(start, end)
        # make a friendlier file name from the rules
        self.name_munger(pt_filter)
        if self.paged or max_results > 500:
            # avoid making many small requests
            max_results = 500
        self.rule_payload = {
                    'query': pt_filter
            }
        self.rule_payload["maxResults"] = int(max_results)
        if start:
            self.rule_payload["fromDate"] = self.fromDate
        if end:
            self.rule_payload["toDate"] = self.toDate
        # use the proper endpoint url
        self.stream_url = self.end_point
        if count_bucket:
            if not self.end_point.endswith("counts.json"): 
                self.stream_url = self.end_point[:-5] + "/counts.json"
            if count_bucket not in ['day', 'minute', 'hour']:
                raise ValueError("Error. Invalid count bucket: %s \n"%str(count_bucket))
            self.rule_payload["bucket"] = count_bucket
            self.rule_payload.pop("maxResults",None)
        # for testing, show the query JSON and stop
        if show_query:
            sys.stderr.write("API query:\n")
            sys.stderr.write(json.dumps(self.rule_payload) + '\n')
            sys.exit() 
        # set up variable to catch the data in 3 formats
        self.time_series = []
        self.rec_dict_list = []
        self.rec_list_list = []
        self.res_cnt = 0
        # timing
        self.delta_t = 1    # keeps us from crashing 
        # actual oldest tweet before now
        self.oldest_t = datetime.datetime.utcnow()
        # actual newest tweet more recent that 30 days ago
        # self.newest_t = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        # search v2: newest date is more recent than 2006-03-01T00:00:00
        self.newest_t = datetime.datetime.strptime("2006-03-01T00:00:00.000z", TIME_FORMAT_LONG)
        #
        for rec in self.parse_responses(count_bucket):
            # parse_responses returns only the last set of activities retrieved, not all paged results.
            # to access the entire set, use the helper functions get_activity_set and get_list_set!
            self.res_cnt += 1
            self.rec_dict_list.append(rec)
            if count_bucket:
                # timeline data
                t = datetime.datetime.strptime(rec["timePeriod"], TIME_FORMAT_SHORT)
                tmp_tl_list = [rec["timePeriod"], rec["count"], t]
                self.tweet_times_flag = False
            else:
                # json activities
                # keep track of tweet times for time calculation
                tmp_list = self.twitter_parser.procRecordToList(rec)
                self.rec_list_list.append(tmp_list)
                t = datetime.datetime.strptime(tmp_list[POSTED_TIME_IDX], TIME_FORMAT_LONG)
                tmp_tl_list = [tmp_list[POSTED_TIME_IDX], 1, t]
                self.tweet_times_flag = True
            # this list is ***either*** list of buckets or list of tweet times!
            self.time_series.append(tmp_tl_list)
            # timeline requests don't return activities!
            if t < self.oldest_t:
                self.oldest_t = t
            if t > self.newest_t:
                self.newest_t = t
            self.delta_t = (self.newest_t - self.oldest_t).total_seconds()/60.
        return 

    def get_rate(self):
        """Returns rate from last query executed"""
        if self.delta_t != 0:
            return float(self.res_cnt)/self.delta_t
        else:
            return None

    def __len__(self):
        """Returns the size of the results set when len(Query) is called."""
        try:
            return self.res_cnt
        except AttributeError:
            return 0

    def __repr__(self):
        """Returns a string represenataion of the result set."""
        try:
            return "\n".join([json.dumps(x) for x in self.rec_dict_list])
        except AttributeError:
            return "No query completed."

if __name__ == "__main__":
    g = Query("shendrickson@gnip.com"
            , "XXXXXPASSWORDXXXXX"
            , "https://gnip-api.twitter.com/search/30day/accounts/shendrickson/wayback.json")
    g.execute("bieber", 10)
    for x in g.get_activity_set():
        print(x)
    print(g)
    print(g.get_rate())
    g.execute("bieber", count_bucket = "hour")
    print(g)
    print(len(g))
    pg = Query("shendrickson@gnip.com"
            , "XXXXXPASSWORDXXXXX"
            , "https://gnip-api.twitter.com/search/30day/accounts/shendrickson/wayback.json"
            , paged = True 
            , output_file_path = "../data/")
    now_date = datetime.datetime.now()
    pg.execute("bieber"
            , end=now_date.strftime(TIME_FORMAT_LONG)
            , start=(now_date - datetime.timedelta(seconds=200)).strftime(TIME_FORMAT_LONG))
    for x in pg.get_activity_set():
        print(x)
    g.execute("bieber", show_query=True)
