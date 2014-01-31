#!/Users/jmontague/.virtualenvs/data/bin/python
# -*- coding: UTF-8 -*-
__author__="Scott Hendrickson, Josh Montague" 

import sys
import requests
import json
import codecs
import argparse
import datetime
import re

from acscsv.twacscsv import TwacsCSV
from simple_n_grams.simple_n_grams import SimpleNGrams

reload(sys)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stdin = codecs.getreader('utf-8')(sys.stdin)

# formatter of data from API 
TIME_FMT = "%Y%m%d%H%M"

class GnipSearchAPI:

    USE_CASES = ["json", "wordcount","users", "rate", "links", "timeline"]
    
    def __init__(self, token_list_size=20):
        self.token_list_size = int(token_list_size)
        twitter_parser = argparse.ArgumentParser(
                description="GnipSearch supports the following use cases: %s"%str(self.USE_CASES))
        twitter_parser.add_argument("use_case", metavar= "USE_CASE", choices=self.USE_CASES, 
                help="Use case for this search.")
        twitter_parser.add_argument("-f", "--filter", dest="filter", default="from:jrmontag OR from:gnip",
                help="PowerTrack filter rule (See: http://support.gnip.com/customer/portal/articles/901152-powertrack-operators)")
        twitter_parser.add_argument("-l", "--stream-url", dest="stream_url", 
                default="https://search.gnip.com/accounts/shendrickson/search/wayback.json",
                help="Url of search endpoint. (See your Gnip console.)")
        twitter_parser.add_argument("-c", "--count", dest="csv_count", action="store_true", 
                default=False,
                help="Return comma-separated 'date,counts' when using a counts.json endpoint.")
        twitter_parser.add_argument("-b", "--bucket", dest="count_bucket", 
                default="day", 
                help="Bucket size for counts query. Options are day, hour, minute (default is 'day').")
        twitter_parser.add_argument("-s", "--start-date", dest="start", 
                default=None,
                help="Start of datetime window, format 'YYYY-mm-DDTHH:MM' (default: 30 days ago)")
        twitter_parser.add_argument("-e", "--end-date", dest="end", 
                default=None,
                help="End of datetime window, format 'YYYY-mm-DDTHH:MM' [Omit for most recent activities] (default: none)")
        twitter_parser.add_argument("-q", "--query", dest="query", action="store_true", 
                default=False, help="View API query (no data)")
        twitter_parser.add_argument("-u", "--user-name", dest="user", default="jmontague@gnip.com",
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
        #
        if self.options.use_case.startswith("links"):
            char_upper_cutoff=100
            space_tokenizer = True
        self.freq = SimpleNGrams(charUpperCutoff=char_upper_cutoff, space_tokenizer=space_tokenizer)
        if self.options.use_case.startswith("user"):
            self.index = USER_NAME_INDEX
        elif self.options.use_case.startswith("wordc"):
            self.index = TEXT_INDEX
        elif self.options.use_case.startswith("rate"):
            self.index = DATE_INDEX
        elif self.options.use_case.startswith("link"):
            self.index = LINKS_INDEX
        elif self.options.use_case.startswith("time"):
            if not self.options.stream_url.endswith("counts.json"): 
                self.options.stream_url = self.options.stream_url[:-5] + "/counts.json"
            if self.options.count_bucket not in ['day', 'minute', 'hour']:
                print >> sys.stderr, "Error. Invalid count bucket: %s \n"%str(self.options.count_bucket)
                sys.exit()
        timeRE = re.compile("([0-9]{4}).([0-9]{2}).([0-9]{2}).([0-9]{2}):([0-9]{2})")
        if self.options.start:
            dt = re.search(timeRE, self.options.start)
            if not dt:
                print >> sys.stderr, "Error. Invalid start-date format: %s \n"%str(self.options.start)
                sys.exit()    
            else:
                f =''
                for i in range(re.compile(timeRE).groups):
                    f += dt.group(i+1) 
                self.fromDate = f
        if self.options.end:
            dt = re.search(timeRE, self.options.end)
            if not dt:
                print >> sys.stderr, "Error. Invalid end-date format: %s \n"%str(self.options.end)
                sys.exit()
            else:
                e =''
                for i in range(re.compile(timeRE).groups):
                    e += dt.group(i+1) 
                self.toDate = e


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
            if "error" in tacs:
                print >> sys.stderr, "Error, invalid request"
                print >> sys.stderr, "Query: %s"%self.rule_payload
                print >> sys.stderr, "Response: %s"%doc
        except ValueError:
            print >> sys.stderr, "Error, results not parsable"
            print >> sys.stderr, doc
            sys.exit()
        return acs

    def __call__(self):
        self.rule_payload = {'query':self.options.filter, 'maxResults': int(self.options.max), 'publisher': 'twitter'}
        if self.options.start:
            self.rule_payload["fromDate"] = self.fromDate
        if self.options.end:
            self.rule_payload["toDate"] = self.toDate
        if self.options.use_case.startswith("time"):
            self.rule_payload["bucket"] = self.options.count_bucket
        if self.options.query:
            print >>sys.stderr, "API query:"
            print >>sys.stderr, self.rule_payload
            sys.exit() 
        #
        self.doc = []
        self.res_cnt = 0
        self.delta_t = 1    # keeps non-'rate' use-cases from crashing 
        # default delta_t = 30d & search only goes back 30 days
        self.oldest_t = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        self.newest_t = datetime.datetime.utcnow()
        for rec in self.parse_JSON(self.req()):
            self.res_cnt += 1
            if self.options.use_case.startswith("rate"):
                t_str = self.twitter_parser.procRecordToList(rec)[self.index]
                t = datetime.datetime.strptime(t_str,"%Y-%m-%dT%H:%M:%S.000Z")
                if t < self.oldest_t:
                    self.oldest_t = t
                if t > self.newest_t:
                    self.newest_t = t
                self.delta_t = (self.newest_t - self.oldest_t).total_seconds()/60.
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
            elif self.options.use_case.startswith("time"):
                self.doc.append(rec)
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
            res.append("Newest Tweet (UTC): %s"%str(self.newest_t))
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
        elif self.options.use_case.startswith("time"):
            if self.options.csv_count:
                res = ["{:%Y-%m-%dT%H:%M:%S},{}".format(datetime.datetime.strptime(x["timePeriod"], TIME_FMT), x["count"]) for x in self.doc]
            else:
                res = [json.dumps({"results": self.doc})] 
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
