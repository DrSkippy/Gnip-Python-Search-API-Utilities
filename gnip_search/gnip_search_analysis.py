#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__="Scott Hendrickson, Josh Montague" 

import sys
import codecs
import datetime
import time
import os
import re

from gnip_search_api import *

from simple_n_grams.simple_n_grams import SimpleNGrams

reload(sys)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stdin = codecs.getreader('utf-8')(sys.stdin)

#############################################
# Some constants to configure column retrieval from TwacsCSV
DATE_INDEX = 1
TEXT_INDEX = 2
LINKS_INDEX = 3
USER_NAME_INDEX = 7 

class GnipSearchAnalysis(GnipSearchAPI):

    last_pt_filter = None
         
    def get_records(self
            , pt_filter = None
            , max_results = None
            , start = None
            , end = None
            , count_bucket = None
            , query = False):
        if pt_filter is None:
            if self.last_pt_filter is None:
                print >> sys.stderr, "No filter rule provided. Exiting."
                sys.exit()
        else:
            self.last_pt_filter = pt_filter
            self.query_api(self.last_pt_filter 
                , max_results = max_results
                , start = start
                , end = end
                , count_bucket = count_bucket
                , query = query)
        self.freq = None
        return self.rec_dict_list

    def get_time_series(self
            , pt_filter = None
            , max_results = None
            , start = None
            , end = None
            , count_bucket = None
            , query = False):
        if pt_filter is None:
            if self.last_pt_filter is None:
                print >> sys.stderr, "No filter rule provided. Exiting."
                sys.exit()
        else:
            self.last_pt_filter = pt_filter
            self.query_api(self.last_pt_filter 
                , max_results = max_results
                , start = start
                , end = end
                , count_bucket = count_bucket
                , query = query)
        self.freq = None
        return self.time_series

    def get_top_links(self
            , pt_filter = None
            , max_results = None
            , start = None
            , end = None
            , count_bucket = None
            , query = False
            , n = 20):
        if pt_filter is None:
            if self.last_pt_filter is None:
                print >> sys.stderr, "No filter rule provided. Exiting."
                sys.exit()
        else:
            self.last_pt_filter = pt_filter
            self.query_api(self.last_pt_filter 
                , max_results = max_results
                , start = start
                , end = end
                , count_bucket = count_bucket
                , query = query)
        self.freq = SimpleNGrams(char_upper_cutoff=100, tokenizer="space")
        for x in self.rec_list_list:
            link_str = x[LINKS_INDEX]
            if link_str != "GNIPEMPTYFIELD" and link_str != "None":
                exec("link_list=%s"%link_str)
                for l in link_list:
                    self.freq.add(l)
            else:
                self.freq.add("NoLinks")
        return self.freq.get_tokens(n) 

    def get_top_users(self
            , pt_filter = None
            , max_results = None
            , start = None
            , end = None
            , count_bucket = None
            , query = False
            , n = 20):
        if pt_filter is None:
            if self.last_pt_filter is None:
                print >> sys.stderr, "No filter rule provided. Exiting."
                sys.exit()
        else:
            self.last_pt_filter = pt_filter
            self.query_api(self.last_pt_filter 
                , max_results = max_results
                , start = start
                , end = end
                , count_bucket = count_bucket
                , query = query)
        self.freq = SimpleNGrams(char_upper_cutoff=20, tokenizer="twitter")
        for x in self.rec_list_list:
            self.freq.add(x["USER_INDEX"])
        return self.freq.get_tokens(n) 

    def get_top_grams(self
            , pt_filter = None
            , max_results = None
            , start = None
            , end = None
            , count_bucket = None
            , query = False
            , n = 20):
        if pt_filter is None:
            if self.last_pt_filter is None:
                print >> sys.stderr, "No filter rule provided. Exiting."
                sys.exit()
        else:
            self.last_pt_filter = pt_filter
            self.query_api(self.last_pt_filter 
                , max_results = max_results
                , start = start
                , end = end
                , count_bucket = count_bucket
                , query = query)
        self.freq = SimpleNGrams(char_upper_cutoff=20, tokenizer="twitter")
        for x in self.rec_list_list:
            self.freq.add(x["TEXT_INDEX"])
        return self.freq.get_tokens(n) 
            
    def get_geo(self
            , pt_filter = None
            , max_results = None
            , start = None
            , end = None
            , count_bucket = None
            , query = False
            , n = 20):
        if pt_filter is None:
            if self.last_pt_filter is None:
                print >> sys.stderr, "No filter rule provided. Exiting."
                sys.exit()
        else:
            self.last_pt_filter = pt_filter
            self.query_api(self.last_pt_filter 
                , max_results = max_results
                , start = start
                , end = end
                , count_bucket = count_bucket
                , query = query)
        self.freq = None
        res = []
        for x in self.rec_list_list:
            lat, lng = None, None
            if "geo" in rec:
                if "coordinates" in rec["geo"]:
                    [lat,lng] = rec["geo"]["coordinates"]
                    record = { "id": rec["id"].split(":")[2]
                        , "postedTime": rec["postedTime"].strip(".000Z")
                        , "latitude": lat
                        , "longitude": lng }
                rec.append(record)
        return rec
 
    def get_frequency_list(self, size = 20):
        """Retrieve the token list structure from the last query"""
        if self.freq is None:
            print >> sys.stderr, "No frequency available for user _case"
            return []
        return list(self.freq.get_tokens(size))

    def get_repr(self
            , pt_filter
            , max_results = 100
            , use_case = "wordcount"
            , start = None
            , end = None
            , count_bucket = "day" 
            , csv_flag = False
            , query = False):
        if pt_filter is None:
            if self.last_pt_filter is None:
                print >> sys.stderr, "No filter rule provided. Exiting."
                sys.exit()
        else:
            self.last_pt_filter = pt_filter
            self.query_api(self.last_pt_filter 
                , max_results = max_results
                , start = start
                , end = end
                , count_bucket = count_bucket
                , query = query)
        # e.g. command line style text output
        # TODO: Fix mixed formatting types
        WIDTH = 80
        BIG_COLUMN = 32
        res = [u"-"*WIDTH]
        if use_case.startswith("rate"):
            rate = self.get_rate()
            unit = "Tweets/Minute"
            if rate < 0.01:
                rate *= 60.
                unit = "Tweets/Hour"
            res.append("     PowerTrack Rule: \"%s\""%pt_filter)
            res.append("  Oldest Tweet (UTC): %s"%str(self.oldest_t))
            res.append("  Newest Tweet (UTC): %s"%str(self.newest_t))
            res.append("           Now (UTC): %s"%str(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))
            res.append("        %5d Tweets: %6.3f %s"%(self.res_cnt, rate, unit))
            res.append("-"*WIDTH)
        elif use_case.startswith("geo"):
            self.get_geo()
            if csv_flag:
                res = []
                for x in self.rec_dict_list:
                    try:
                        res.append("{},{},{},{}".format(x["id"], x["postedTime"], x["longitude"], x["latitude"]))
                    except KeyError, e:
                        print >> sys.stderr, str(e)
            else:
                res = [json.dumps(x) for x in self.rec_dict_list]
        elif use_case.startswith("json"):
            self.get_records()
            res = self.rec_dict_list
        elif use_case.startswith("word") or use_case.startswith("user"):
            fmt_str = "%{}s -- %10s     %8s (%d)".format(BIG_COLUMN)
            res.append(fmt_str%( "terms", "mentions", "activities", self.res_cnt))
            res.append("-"*WIDTH)
            fmt_str =  "%{}s -- %4d  %5.2f%% %4d  %5.2f%%".format(BIG_COLUMN)
            for x in self.freq.get_tokens(self.token_list_size):
                res.append(fmt_str%(x[4], x[0], x[1]*100., x[2], x[3]*100.))
            res.append("-"*WIDTH)
        elif use_case.startswith("time"):
            if csv_flag:
                res = ["{:%Y-%m-%dT%H:%M:%S},{}".format(
                    datetime.datetime.strptime(x["timePeriod"]
                  , TIME_FMT)
                  , x["count"]) 
                        for x in self.rec_dict_list]
            else:
                res = [json.dumps({"results": self.rec_dict_list})] 
        else:
            res[-1]+=u"-"*WIDTH
            res.append("%100s -- %10s     %8s (%d)"%("links", "mentions", "activities", self.res_cnt))
            res.append("-"*2*WIDTH)
            for x in self.freq.get_tokens(self.token_list_size):
                res.append("%100s -- %4d  %5.2f%% %4d  %5.2f%%"%(x[4], x[0], x[1]*100., x[2], x[3]*100.))
            res.append("-"*WIDTH)
        return u"\n".join(res)

if __name__ == "__main__":
    g = GnipSearchAnalysis("shendrickson@gnip.com"
            , "merploft"
            , "https://search.gnip.com/accounts/shendrickson/search/wayback.json")
    print g.get_repr("bieber", 100, "rate")
    print g.get_rate()
    print g.get_repr("bieber")
    print g.get_frequency_list(25)
    print g.get_repr("bieber", 50)
    print g.query_api("bieber", 10, "json")
    print g.get_frequency_list(10)
    print g.query_api("bieber", use_case = "timeline")
    print g.get_repr("bieber", 10, "users")
    print g.get_rate()
    print g.get_repr("bieber", 10, "links")
    print g.query_api("bieber", query=True)
