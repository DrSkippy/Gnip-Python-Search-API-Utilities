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
    """Encapsulates a paged search API resusts for a a single filter"""

    def __init__(self, filter, max_records, to_date, from_date, pub, user_name, password, file_name, stream_url):
        self.user_name = user_name
        self.password = password
        self.file_name = file_name
        self. stream_url = stream_url
        self.twitter_parser = TwacsCSV(",",False, True, False, True, False, False, False,False) 
        self.activities_returned = []
        self.ts = datetime.datetime.utcnow()
        self.page_count = 1
        self.rule_payload = {'q':filter, 'max': int(max_records), 'toDate':str(to_date),'fromDate':str(from_date),'publisher':pub}
        self.name_munger(filter)

    def name_munger(self, f):
        """creates a file name per rule"""
        f = re.sub(' +','_',f)
        f = f.replace(':','_')
        f = f.replace('"','_Q_')
        f = f.replace('(','_p_') 
        f = f.replace(')','_p_') 
        self.file_name_prefix = f

    def req(self):
        """Called from get_json - uses Session from requests"""
        try:
            s = requests.Session()
            s.headers = {'Accept-encoding': 'gzip'}
            s.auth = (self.user_name, self.password)
            res = s.post(self.stream_url, data=json.dumps(self.rule_payload))
        except requests.exceptions.ConnectionError, e:
            print >> sys.stderr, "Error (%s). Exiting without results."%str(e)
            sys.exit()
        except requests.exceptions.HTTPError, e:
            print >> sys.stderr, "Error (%s). Exiting without results."%str(e)
            sys.exit()
        return res.text

    def parse_JSON(self, doc):
        """stores results locally as timestamp_file_name.json"""
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
        if len(t_acs) > 0:
            if self.file_name:
                local_storage="data/"
                file_name=local_storage+"{0}_{1}.json".format(str(datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")),str(self.file_name_prefix))
                with open(file_name, "wb") as out:
                    print >> sys.stderr, "(writing to file ...)"
                    for item in t_acs:
                        out.write(json.dumps(item)+"\n")
            else:
                for item in t_acs:
                    print json.dumps(item)
        else:
            print >> sys.stderr, "no results returned for rule:{0}".format(str(self.rule_payload))
        if "next" in tacs:
            self.rule_payload["next"]=tacs["next"]
            return True
        else:
            if "next" in self.rule_payload:
                del self.rule_payload["next"]
            return False

    def get_json(self):
        """Makes requests until "next" is not in the returned record"""
        while self.parse_JSON(self.req()):
            print >> sys.stderr, "Now retrieving %d results ..."%(int(self.max_records)) 

    def metrics(self):
        return  self.page_count, float(sum(a.activities_returned))/a.page_count

if __name__ == "__main__":
    twitter_parser = argparse.ArgumentParser(
            description="Call API until all available results returned")
    twitter_parser.add_argument("-s", "--stream-url", dest="stream_url", 
            default="https://search.gnip.com/accounts/shendrickson/publishers/twitter/search/wayback.json",
            help="Url of search endpoint. (See your Gnip console.)")
    twitter_parser.add_argument("-f", "--file", dest="file_name", default=False, action="store_true", 
            help="If set, create a file for each page in ./data (you must create this directory before running)")
    twitter_parser.add_argument("-u", "--user_name", dest="user_name", default="shendrickson@gnip.com",
            help="User name")
    twitter_parser.add_argument("-p", "--password", dest="password", 
            help="Password")
    twitter_parser.add_argument("-n", "--results-max", dest="max", default=500, 
            help="Maximum results to return (default 500)")
    twitter_parser.add_argument("-d", "--from date", dest="fromDate",  
            help="yyyymmddhhmm")
    twitter_parser.add_argument("-t", "--to date", dest="toDate",  
            help="yyyymmddhhmm")
    twitter_parser.add_argument("-z", "--publisher", dest="pub", default="twitter", 
            help="twitter")
    options = twitter_parser.parse_args() 
    
    start = datetime.datetime.now()
    print >> sys.stderr, "Local time:",str(start)
    for x in sys.stdin:
        a = PagedSearchAPI(x.strip(), options.max, options.toDate, options.fromDate, options.pub, options.user_name, options.password, options.file_name, options.stream_url)
        a.get_json()
        print >> sys.stderr, a.metrics()
    end =  datetime.datetime.now()
    print >> sys.stderr, "Local time:", str(end), int((end-start).total_seconds()), sum(a.activities_returned)/float((end-start).total_seconds())        

