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
TIME_FMT_SHORT = "%Y%m%d%H%M"
TIME_FMT_LONG = "%Y-%m-%dT%H:%M:%S.000Z"
PAUSE = 3 # seconds between page requests
POSTED_TIME_IDX = 1

class GnipSearchAPI(object):
    
    def __init__(self
            , user
            , password
            , stream_url
            , paged = False
            , output_file_path = None
            ):
        #############################################
        self.output_file_path = output_file_path
        self.paged = paged
        self.user = user
        self.password = password
        self.end_point = stream_url # records end point NOT the counts end point
        # get a parser for the twitter columns
        # TODO: use the updated retriveal methods in gnacs instead of this
        self.twitter_parser = TwacsCSV(",", None, False, True, False, True, False, False, False)

    def set_dates(self, start, end):
        # re for the acceptable datetime formats
        timeRE = re.compile("([0-9]{4}).([0-9]{2}).([0-9]{2}).([0-9]{2}):([0-9]{2})")
        if start:
            dt = re.search(timeRE, start)
            if not dt:
                print >> sys.stderr, "Error. Invalid start-date format: %s \n"%str(start)
                sys.exit()    
            else:
                f =''
                for i in range(re.compile(timeRE).groups):
                    f += dt.group(i+1) 
                self.fromDate = f
        if end:
            dt = re.search(timeRE, end)
            if not dt:
                print >> sys.stderr, "Error. Invalid end-date format: %s \n"%str(end)
                sys.exit()
            else:
                e =''
                for i in range(re.compile(timeRE).groups):
                    e += dt.group(i+1) 
                self.toDate = e

    def name_munger(self, f):
        """Creates a valid, friendly file name  fro an input rule."""
        f = re.sub(' +','_',f)
        f = f.replace(':','_')
        f = f.replace('"','_Q_')
        f = f.replace('(','_p_') 
        f = f.replace(')','_p_') 
        self.file_name_prefix = f[:42]

    def req(self):
        try:
            s = requests.Session()
            s.headers = {'Accept-encoding': 'gzip'}
            s.auth = (self.user, self.password)
            res = s.post(self.stream_url, data=json.dumps(self.rule_payload))
        except requests.exceptions.ConnectionError, e:
            print >> sys.stderr, "Error (%s). Exiting without results."%str(e)
            sys.exit()
        except requests.exceptions.HTTPError, e:
            print >> sys.stderr, "Error (%s). Exiting without results."%str(e)
            sys.exit()
        #Don't use res.text -- creates encoding challenges!
        return unicode(res.content, "utf-8")

    def parse_JSON(self):
        acs = []
        repeat = True
        page_count = 0
        while repeat:
            doc = self.req()
            try:
                tmp_response =  json.loads(doc)
                if "results" in tmp_response:
                    acs.extend(tmp_response["results"])
                if "error" in tmp_response:
                    print >> sys.stderr, "Error, invalid request"
                    print >> sys.stderr, "Query: %s"%self.rule_payload
                    print >> sys.stderr, "Response: %s"%doc
                    sys.exit()
            except ValueError:
                print >> sys.stderr, "Error, results not parsable"
                print >> sys.stderr, doc
                sys.exit()
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
                            print >> sys.stderr, "(writing to file ...)"
                            for item in tmp_response["results"]:
                                out.write(json.dumps(item)+"\n")
                    else:
                        # if writing to file, don't keep track of all the data in memory
                        acs = []
                else:
                    print >> sys.stderr, "no results returned for rule:{0}".format(str(self.rule_payload))
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

    def query_api(self
            , pt_filter
            , max_results = 100
            , start = None
            , end = None
            , count_bucket = "hour" # None is json
            , query = False):
        self.set_dates(start, end)
        self.name_munger(pt_filter)
        if self.paged:
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
        self.stream_url = self.end_point
        if count_bucket:
            if not self.end_point.endswith("counts.json"): 
                self.stream_url = self.end_point[:-5] + "/counts.json"
            if count_bucket not in ['day', 'minute', 'hour']:
                print >> sys.stderr, "Error. Invalid count bucket: %s \n"%str(count_bucket)
                sys.exit()
            self.rule_payload["bucket"] = count_bucket
        if query:
            print >>sys.stderr, "API query:"
            print >>sys.stderr, self.rule_payload
            sys.exit() 
        # 
        self.time_series = []
        self.rec_dict_list = []
        self.rec_list_list = []
        self.res_cnt = 0
        # timing
        self.delta_t = 1    # keeps non-'rate' use-cases from crashing 
        # actual oldest tweet before now
        self.oldest_t = datetime.datetime.utcnow()
        # actual newest tweet more recent that 30 days ago
        self.newest_t = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        #
        for rec in self.parse_JSON():
            self.res_cnt += 1
            self.rec_dict_list.append(rec)
            if count_bucket:
                # timeline
                t = datetime.datetime.strptime(rec["timePeriod"], TIME_FMT_SHORT)
                tmp_tl_list = [rec["timePeriod"], rec["count"], t]
            else:
                # json records
                tmp_list = self.twitter_parser.procRecordToList(rec)
                self.rec_list_list.append(tmp_list)
                t = datetime.datetime.strptime(tmp_list[POSTED_TIME_IDX], TIME_FMT_LONG)
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
        return float(self.res_cnt)/self.delta_t

    def __len__(self):
        return self.res_cnt

    def __repr__(self):
        return "\n".join([json.dumps(x) for x in self.rec_dict_list])

if __name__ == "__main__":
    g = GnipSearchAPI("shendrickson@gnip.com"
            , "XXXPWDXXX"
            , "https://search.gnip.com/accounts/shendrickson/search/wayback.json")
    g.query_api("bieber", 10)
    print g
    print g.get_rate()
    g.query_api("bieber")
    g.query_api("bieber", count_bucket = "hour")
    print len(g)
    g.query_api("bieber", query=True)
