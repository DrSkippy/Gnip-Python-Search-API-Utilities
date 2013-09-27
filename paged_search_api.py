#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @DrSkippy27
# http://upload.wikimedia.org/wikipedia/en/3/3f/Waybackmachine3.png
import sys
import requests
import json
import codecs
import argparse
import datetime
import re

from acscsv.twacscsv import TwacsCSV

reload(sys)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stdin = codecs.getreader('utf-8')(sys.stdin)

class PagedSearchAPI:

    def __init__(self, filter):
        twitter_parser = argparse.ArgumentParser(
                description="Call API until all available results returned")
        twitter_parser.add_argument("-s", "--stream-url", dest="stream_url", 
                default="https://search.gnip.com/accounts/shendrickson/publishers/twitter/search/wayback.json",
                help="Url of search endpoint. (See your Gnip console.)")
        twitter_parser.add_argument("-f", "--file", dest="filename", default=False, action="store_true", 
                help="If set, create a file for each page in ./data (you must create this directory before running)")
        twitter_parser.add_argument("-u", "--user-name", dest="user", default="shendrickson@gnip.com",
                help="User name")
        twitter_parser.add_argument("-p", "--password", dest="pwd", 
                help="Password")
        twitter_parser.add_argument("-n", "--results-max", dest="max", default=500, 
                help="Maximum results to return (default 500)")
        self.options = twitter_parser.parse_args()
        self.twitter_parser = TwacsCSV(",",False, True, False, True, False, False, False)
        self.acs = []
        self.activities_returned = []
        self.oldest = datetime.datetime.utcnow()
        self.rule_payload = {'q':filter, 'max': int(self.options.max), 'toDate':None}
        self.page_count = 1
        self.name_munger(filter)

    def name_munger(self, f):
        f = re.sub(' +','_',f)
        f = f.replace(':','_')
        f = f.replace('"','_Q_')
        f = f.replace('(','_p_') 
        f = f.replace(')','_p_') 
        self.filename_prefix = f

    def req(self):
        try:
            s = requests.Session()
            s.headers = {'Accept-encoding': 'gzip'}
            s.auth = (self.options.user, self.options.pwd)
            self.rule_payload["toDate"] = self.oldest.strftime("%Y%m%d%H%M")
            #print self.rule_payload
            res = s.post(self.options.stream_url, data=json.dumps(self.rule_payload))
        except requests.exceptions.ConnectionError, e:
            print >> sys.stderr, "Error (%s). Exiting without results."%str(e)
            sys.exit()
        except requests.exceptions.HTTPError, e:
            print >> sys.stderr, "Error (%s). Exiting without results."%str(e)
            sys.exit()
        #print res.text
        return res.text

    def parse_JSON(self, doc):
        t_acs = []
        try:
            tacs =  json.loads(doc)
            if "results" in tacs:
                t_acs = tacs["results"]
                self.activities_returned.append(len(t_acs))
                self.page_count += 1
        except ValueError:
            print >> sys.stderr, "Error, results not parsable"
            print >> sys.stderr, doc
            sys.exit()
        self.acs.extend(t_acs)
        #
        t_oldest = datetime.datetime.utcnow()
        for x in self.acs:
            tmp_t = datetime.datetime.strptime(x["postedTime"],"%Y-%m-%dT%H:%M:%S.000Z")
            if tmp_t < t_oldest:
                t_oldest = tmp_t
        if t_oldest < self.oldest:
            self.oldest = t_oldest
        if len(t_acs) > 0:
            if self.options.filename:
                with open("./data/%s-%s.json"%(self.filename_prefix,  self.oldest.strftime("%Y%m%d%H%M")), "wb") as out:
                    out.write(json.dumps(t_acs))
                self.acs = []
            return True
        else:
            return False

    def get_json(self):
        while self.parse_JSON(self.req()):
            print >> sys.stderr, "Now retrieving %d results up to %s (UTC)..."%(int(self.options.max), self.oldest) 
        if self.acs == []:
            return "(writing to file %s)"%self.filename_prefix
        else:
            return json.dumps(self.acs)

    def metrics(self):
        return  str(self.oldest), self.page_count, float(sum(a.activities_returned))/a.page_count

if __name__ == "__main__":
    for x in sys.stdin:
        a = PagedSearchAPI(x.strip())
        print a.get_json()
        print >> sys.stderr, a.metrics()
