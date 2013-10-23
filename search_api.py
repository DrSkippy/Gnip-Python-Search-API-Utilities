#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @DrSkippy27
import sys
import requests
import json
import codecs
import argparse
import datetime

from acscsv.twacscsv import TwacsCSV
from simple_n_grams.simple_n_grams import SimpleNGrams

reload(sys)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stdin = codecs.getreader('utf-8')(sys.stdin)

class GnipSearchAPI:

    USE_CASES = ["json", "wordcount","users", "rate", "links"]
    
    def __init__(self, token_list_size=20):
        self.token_list_size = int(token_list_size)
        twitter_parser = argparse.ArgumentParser(
                description="GnipSearch supports the following use cases: %s"%str(self.USE_CASES))
        twitter_parser.add_argument("use_case", metavar= "USE_CASE", choices=self.USE_CASES, 
                help="Use case for this search.")
        twitter_parser.add_argument("-f", "--filter", dest="filter", default="from:drskippy27 OR from:gnip",
                help="PowerTrack filter rule (See: http://support.gnip.com/customer/portal/articles/901152-powertrack-operators)")
        twitter_parser.add_argument("-s", "--stream-url", dest="stream_url", 
                default="https://search.gnip.com/accounts/shendrickson/publishers/twitter/search/wayback.json",
                help="Url of search endpoint. (See your Gnip console.)")
        twitter_parser.add_argument("-u", "--user-name", dest="user", default="shendrickson@gnip.com",
                help="User name")
        twitter_parser.add_argument("-p", "--password", dest="pwd", 
                help="Password")
        twitter_parser.add_argument("-n", "--results-max", dest="max", default=100, 
                help="Maximum results to return (default 100)")
        self.options = twitter_parser.parse_args()
        self.twitter_parser = TwacsCSV(",", False, False, True, False, True, False, False, False)
        DATE_INDEX = 1
        TEXT_INDEX = 2
        LINKS_INDEX = 3
        USER_NAME_INDEX = 7
        space_tokenizer = False
        char_upper_cutoff=11
        if self.options.use_case.startswith("links"):
            char_upper_cutoff=100
            space_tokenizer = True
        self.freq = SimpleNGrams(charUpperCutoff=char_upper_cutoff, spaceTokenizer=space_tokenizer)
        if self.options.use_case.startswith("user"):
            self.index = USER_NAME_INDEX
        elif self.options.use_case.startswith("wordc"):
            self.index = TEXT_INDEX
        elif self.options.use_case.startswith("rate"):
            self.index = DATE_INDEX
        elif self.options.use_case.startswith("link"):
            self.index = LINKS_INDEX

    def req(self):
        try:
            s = requests.Session()
            s.headers = {'Accept-encoding': 'gzip'}
            s.auth = (self.options.user, self.options.pwd)
            res = s.post(self.options.stream_url, data=json.dumps(self.rule_payload))
        except requests.exceptions.ConnectionError, e:
            print >> sys.stderr, "Error (%s). Exiting without results."%str(e)
            sys.exit()
        except requests.exceptions.HTTPError, e:
            print >> sys.stderr, "Error (%s). Exiting without results."%str(e)
            sys.exit()
        return res.text

    def parse_JSON(self, doc):
        acs = []
        try:
            tacs =  json.loads(doc)
            if "results" in tacs:
                acs = tacs["results"]
        except ValueError:
            print >> sys.stderr, "Error, results not parsable"
            print >> sys.stderr, doc
            sys.exit()
        return acs

    def __call__(self):
        self.rule_payload = {'q':self.options.filter, 'max': int(self.options.max)}
        self.oldest_t = datetime.datetime.utcnow()
        start_t = self.oldest_t
        self.doc = []
        self.res_cnt = 0
        for rec in self.parse_JSON(self.req()):
            self.res_cnt += 1
            if self.options.use_case.startswith("rate"):
                t_str = self.twitter_parser.procRecordToList(rec)[self.index]
                t = datetime.datetime.strptime(t_str,"%Y-%m-%dT%H:%M:%S.000Z")
                if t < self.oldest_t:
                    self.oldest_t = t
                    self.delta_t = (start_t - self.oldest_t).total_seconds()/60.
            elif self.options.use_case.startswith("links"):
                link_str = self.twitter_parser.procRecordToList(rec)[self.index]
                if link_str != "None":
                    exec("link_list=%s"%link_str)
                    for l in link_list:
                        self.freq.add(l)
                else:
                    self.freq.add("NoLinks")
            elif self.options.use_case.startswith("json"):
                self.doc.append(json.dumps(rec))
            else:
                self.freq.add(self.twitter_parser.procRecordToList(rec)[self.index])
        return self

    def get_repr(self):
        WIDTH = 60
        res = [u"-"*WIDTH]
        if self.options.use_case.startswith("rate"):
            rate = float(self.res_cnt)/self.delta_t
            unit = "Tweets/Minute"
            if rate < 0.01:
                rate *= 60.
                unit = "Tweets/Hour"
            res.append("   PowerTrack Rule: \"%s\""%self.options.filter)
            res.append("Oldest Tweet (UTC): %s"%str(self.oldest_t))
            res.append("         Now (UTC): %s"%str(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))
            res.append("      %5d Tweets: %6.3f %s"%(self.res_cnt, rate, unit))
            res.append("-"*WIDTH)
        elif self.options.use_case.startswith("json"):
            res.extend(self.doc)
        elif self.options.use_case.startswith("word") or self.options.use_case.startswith("user"):
            res.append("%22s -- %10s     %8s (%d)"%( "terms", "mentions", "activities", self.res_cnt))
            res.append("-"*WIDTH)
            for x in self.freq.get_tokens(self.token_list_size):
                res.append("%22s -- %4d  %5.2f%% %4d  %5.2f%%"%(x[4], x[0], x[1]*100., x[2], x[3]*100.))
            res.append("-"*WIDTH)
        else:
            res[-1]+=u"-"*WIDTH
            res.append("%100s -- %10s     %8s (%d)"%("links", "mentions", "activities", self.res_cnt))
            res.append("-"*2*WIDTH)
            for x in self.freq.get_tokens(self.token_list_size):
                res.append("%100s -- %4d  %5.2f%% %4d  %5.2f%%"%(x[4], x[0], x[1]*100., x[2], x[3]*100.))
            res.append("-"*WIDTH)
        return "\n".join(res)

if __name__ == "__main__":
    print GnipSearchAPI()().get_repr()
