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

from acscsv.twitter_acs import TwacsCSV

reload(sys)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stdin = codecs.getreader('utf-8')(sys.stdin)

# formatter of data from API 
TIME_FORMAT_SHORT = "%Y%m%d%H%M"
TIME_FORMAT_LONG = "%Y-%m-%dT%H:%M:%S.000Z"
PAUSE = 1 # seconds between page requests
POSTED_TIME_IDX = 1
#date time parsing utility regex
DATE_TIME_RE = re.compile("([0-9]{4}).([0-9]{2}).([0-9]{2}).([0-9]{2}):([0-9]{2})")

class GnipSearchAPI(object):
    
    def __init__(self
            , user
            , password
            , stream_url
            , paged = False
            , output_file_path = None
            ):
        self.output_file_path = output_file_path
        self.paged = paged
        self.paged_file_list = []
        self.user = user
        self.password = password
        self.end_point = stream_url # records end point NOT the counts end point
        # get a parser for the twitter columns
        # TODO: use the updated retriveal methods in gnacs instead of this
        self.twitter_parser = TwacsCSV(",", None, False, True, False, True, False, False, False)

    def set_dates(self, start, end):
        """Given string-formated dates for start and end, parse the dates and create
        datetime objects for use in the API query. Sets class date strings."""
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
        """Creates a valid, friendly file name  fro an input rule."""
        f = re.sub(' +','_',f)
        f = f.replace(':','_')
        f = f.replace('"','_Q_')
        f = f.replace('(','_p_') 
        f = f.replace(')','_p_') 
        self.file_name_prefix = f[:42]

    def req(self):
        """HTTP request based on class variables for rule_payload, stream_url, user and password"""
        try:
            s = requests.Session()
            s.headers = {'Accept-encoding': 'gzip'}
            s.auth = (self.user, self.password)
            res = s.post(self.stream_url, data=json.dumps(self.rule_payload))
        except requests.exceptions.ConnectionError, e:
            e.msg = "Error (%s). Exiting without results."%str(e)
            raise e
        except requests.exceptions.HTTPError, e:
            e.msg = "Error (%s). Exiting without results."%str(e)
            raise e
        except requests.exceptions.MissingSchema, e:
            e.msg = "Error (%s). Exiting without results."%str(e)
            raise e
        #Don't use res.text -- creates encoding challenges!
        return unicode(res.content, "utf-8")

    def parse_JSON(self):
        acs = []
        repeat = True
        page_count = 1
        self.paged_file_list = []
        while repeat:
            doc = self.req()
            try:
                tmp_response =  json.loads(doc)
                if "results" in tmp_response:
                    acs.extend(tmp_response["results"])
                if "error" in tmp_response:
                    raise ValueError("Invalid request\nQuery: %s\nResponse: %s"%(self.rule_payload, doc))
            except ValueError, e:
                e.msg = "Error. Failed to retrieve valid JSON records:\n%s"%e
                raise e
            # 
            repeat = False
            if self.paged:
                if len(acs) > 0:
                    if self.output_file_path is not None:
                        file_name = self.output_file_path + "/{0}_{1}.json".format(
                                str(datetime.datetime.utcnow().strftime(
                                    "%Y%m%d%H%M%S"))
                              , str(self.file_name_prefix))
                        with codecs.open(file_name, "wb","utf-8") as out:
                            for item in tmp_response["results"]:
                                out.write(json.dumps(item)+"\n")
                        self.paged_file_list.append(file_name)
                    else:
                        # if writing to file, don't keep track of all the data in memory
                        acs = []
                else:
                    print >> sys.stderr, "No results returned for rule:{0}".format(str(self.rule_payload))
                if "next" in tmp_response:
                    self.rule_payload["next"]=tmp_response["next"]
                    repeat = True
                    page_count += 1
                    print >> sys.stderr, "Fetching page {}...".format(page_count)
                else:
                    if "next" in self.rule_payload:
                        del self.rule_payload["next"]
                    repeat = False
                time.sleep(PAUSE)
        return acs

    def get_record_set(self):
        """Iterates through the entire record set from memory or disk."""
        if self.paged:
            for file_name in self.paged_file_list:
                with codecs.open(file_name,"rb") as f:
                    for res in f:
                        yield json.loads(res)
        else:
            for res in self.rec_dict_list:
                yield res

    def get_list_set(self):
        for rec in self.get_record_set():
            yield self.twitter_parser.procRecordToList(rec)

    def query_api(self
            , pt_filter
            , max_results = 100
            , start = None
            , end = None
            , count_bucket = None # None is json
            , query = False):
        # set class start and stop datetime variables
        self.set_dates(start, end)
        # make a friendlier file name from the rules
        self.name_munger(pt_filter)
        if self.paged or max_results > 500:
            # avoid making many small requests
            max_results = 500
        self.rule_payload = {
                    'query': pt_filter
            , 'maxResults': int(max_results)
            ,  'publisher': 'twitter'
            }
        if start:
            self.rule_payload["fromDate"] = self.fromDate
        if end:
            self.rule_payload["toDate"] = self.toDate
        # use teh proper endpoint url
        self.stream_url = self.end_point
        if count_bucket:
            if not self.end_point.endswith("counts.json"): 
                self.stream_url = self.end_point[:-5] + "/counts.json"
            if count_bucket not in ['day', 'minute', 'hour']:
                raise ValueError("Error. Invalid count bucket: %s \n"%str(count_bucket))
            self.rule_payload["bucket"] = count_bucket
        # for testing, show the query JSON and stop
        if query:
            print >>sys.stderr, "API query:"
            print >>sys.stderr, self.rule_payload
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
        self.newest_t = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        #
        for rec in self.parse_JSON():
            # parse_JSON returns only the last set of records retrieved, not all paged results.
            # to access the entire set, use the helper functions get_record_set and get_list_set!
            self.res_cnt += 1
            self.rec_dict_list.append(rec)
            if count_bucket:
                # timeline
                t = datetime.datetime.strptime(rec["timePeriod"], TIME_FORMAT_SHORT)
                tmp_tl_list = [rec["timePeriod"], rec["count"], t]
            else:
                # json records
                tmp_list = self.twitter_parser.procRecordToList(rec)
                self.rec_list_list.append(tmp_list)
                t = datetime.datetime.strptime(tmp_list[POSTED_TIME_IDX], TIME_FORMAT_LONG)
                tmp_tl_list = [tmp_list[POSTED_TIME_IDX], 1, t]
            self.time_series.append(tmp_tl_list)
            # timeline reqeusts don't return records!
            if t < self.oldest_t:
                self.oldest_t = t
            if t > self.newest_t:
                self.newest_t = t
            self.delta_t = (self.newest_t - self.oldest_t).total_seconds()/60.
        return 

    def get_rate(self):
        """Return rate from last query"""
        if self.delta_t != 0:
            return float(self.res_cnt)/self.delta_t
        else:
            return None

    def __len__(self):
        try:
            return self.res_cnt
        except AttributeError:
            return 0

    def __repr__(self):
        try:
            return "\n".join([json.dumps(x) for x in self.rec_dict_list])
        except AttributeError:
            return "No query completed."

if __name__ == "__main__":
    g = GnipSearchAPI("shendrickson@gnip.com"
            , "XXXXXPASSWORDXXXXX"
            , "https://search.gnip.com/accounts/shendrickson/search/wayback.json")
    g.query_api("bieber", 10)
    for x in g.get_record_set():
        print x
    print g
    print g.get_rate()
    g.query_api("bieber", count_bucket = "hour")
    print g
    print len(g)
    pg = GnipSearchAPI("shendrickson@gnip.com"
            , "XXXXXPASSWORDXXXXX"
            , "https://search.gnip.com/accounts/shendrickson/search/wayback.json"
            , paged = True 
            , output_file_path = "../data/")
    now_date = datetime.datetime.now()
    pg.query_api("bieber"
            , end=now_date.strftime(TIME_FORMAT_LONG)
            , start=(now_date - datetime.timedelta(seconds=200)).strftime(TIME_FORMAT_LONG))
    for x in pg.get_record_set():
        print x
    g.query_api("bieber", query=True)
