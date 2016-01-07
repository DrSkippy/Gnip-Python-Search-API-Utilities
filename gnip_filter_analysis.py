#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__="Scott Hendrickson, Josh Montague" 

import sys
import json
import codecs
import argparse
import datetime
import time
import os
import csv
import ConfigParser

import pandas as pd
import numpy as np

from search.results import *

reload(sys)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stdin = codecs.getreader('utf-8')(sys.stdin)

DEFAULT_CONFIG_FILENAME = "./.gnip"

class GnipSearchCMD():

    def __init__(self, token_list_size=20):
        # default tokenizer and character limit
        char_upper_cutoff = 20  # longer than for normal words because of user names
        self.token_list_size = int(token_list_size)
        #############################################
        # CONFIG FILE/COMMAND LINE OPTIONS PATTERN
        # parse config file
        config_from_file = self.config_file()
        # set required fields to None.  Sequence of setting is:
        #  (1) config file
        #  (2) command line
        # if still none, then fail
        self.user = None
        self.password = None
        self.stream_url = None
        if config_from_file is not None:
            try:
                # command line options take presidence if they exist
                self.user = config_from_file.get('creds', 'un')
                self.password = config_from_file.get('creds', 'pwd')
                self.stream_url = config_from_file.get('endpoint', 'url')
            except (ConfigParser.NoOptionError,
                    ConfigParser.NoSectionError) as e:
                print >> sys.stderr, "Error reading configuration file ({}), ignoring configuration file.".format(e)
        # parse the command line options
        self.options = self.args().parse_args()
        # set up the job
        # over ride config file with command line args if present
        if self.options.user is not None:
            self.user = self.options.user
        if self.options.password is not None:
            self.password = self.options.password
        if self.options.stream_url is not None:
            self.stream_url = self.options.stream_url
        #
        # Search v2 uses a different url
        if "data-api.twitter.com" in self.stream_url:
            self.options.search_v2 = True
        else:
            print >> sys.stderr, "Requires search v2, but your URL appears to point to a v1 endpoint. Exiting."
            sys.exit(-1)
        # defaults
        self.options.paged = True
        self.options.max = 500
        # 
        self.job = self.read_job_description(self.options.job_description)

    def config_file(self):
        config = ConfigParser.ConfigParser()
        # (1) default file name precidence
        config.read(DEFAULT_CONFIG_FILENAME)
        if not config.has_section("creds"):
            # (2) environment variable file name second
            if 'GNIP_CONFIG_FILE' in os.environ:
                config_filename = os.environ['GNIP_CONFIG_FILE']
                config.read(config_filename)
        if config.has_section("creds") and config.has_section("endpoint"):
            return config
        else:
            return None

    def args(self):
        twitter_parser = argparse.ArgumentParser(
                description="Creates an aggregated filter statistics summary from filter rules and date periods in the job description.")
        twitter_parser.add_argument("-j", "--job_description", dest="job_description",
                default="./job.json",
                help="JSON formatted job description file")
        twitter_parser.add_argument("-b", "--bucket", dest="count_bucket", 
                default="day", 
                help="Bucket size for counts query. Options are day, hour, minute (default is 'day').")
        twitter_parser.add_argument("-l", "--stream-url", dest="stream_url", 
                default=None,
                help="Url of search endpoint. (See your Gnip console.)")
        twitter_parser.add_argument("-p", "--password", dest="password", default=None, 
                help="Password")
        twitter_parser.add_argument("-q", "--query", dest="query", action="store_true", 
                default=False, help="View API query (no data)")
        twitter_parser.add_argument("-u", "--user-name", dest="user", default=None,
                help="User name")
        twitter_parser.add_argument("-w", "--output-file-path", dest="output_file_path", 
                default="./data",
                help="Create files in ./OUTPUT-FILE-PATH. This path must exists and will not be created. Default is ./data")

        return twitter_parser

    def read_job_description(self, job_description):
        with open(job_description, "rb") as f:
            self.job_description = json.load(f)
        if not all([x in self.job_description for x in ("rules", "date_ranges")]):
            print >>sys.stderr, '"rules" or "date_ranges" missing from you job description file. Exiting'
            sys.exit(-1)
    
    def get_result(self):
        res = [["raw output"]]
        for rule_dict in self.job_description["rules"]:
            rule = rule_dict["value"]
            tag = None
            if "tag" in rule_dict:
                tag = rule_dict["tag"]
            for dates_dict in self.job_description["date_ranges"]:
                start_date = dates_dict["start"]
                end_date = dates_dict["end"]
                results = Results(
                    self.user
                    , self.password
                    , self.stream_url
                    , self.options.paged
                    , self.options.output_file_path
                    , pt_filter=rule
                    , max_results=int(self.options.max)
                    , start=start_date
                    , end=end_date
                    , count_bucket=self.options.count_bucket
                    , show_query=self.options.query
                    , search_v2=self.options.search_v2
                    )
                for x in results.get_time_series():
                    res.append(x + [rule, tag,  start_date, end_date])
        df = pd.DataFrame(res
                , columns=("bucket_datetag","counts","bucket_datetime","filter","filter_tag","start_date","end_date"))
        table = pd.pivot_table(df
                , values="counts"
                , index=["filter"]
                , columns = ["start_date"]
                , margins = True
                , aggfunc=np.sum)
        table.sort_values("All"
                , inplace=True
                , ascending=False)
        # outputs
        if self.options.output_file_path is not None:
            print >> sys.stderr,"Writing data to {}...".format(self.options.output_file_path)
            with open("{}/{}_raw_data.csv".format(
                        self.options.output_file_path
                        , datetime.datetime.now().strftime("%Y%m%d_%H%M"))
                    , "wb") as f:
                wrt = csv.writer(f)
                wrt.writerows(res)
            with open("{}/{}_pivot_data.csv".format(
                        self.options.output_file_path
                        , datetime.datetime.now().strftime("%Y%m%d_%H%M"))
                    , "wb") as f:
                f.write(table.to_csv())
        return res, table

if __name__ == "__main__":
    g = GnipSearchCMD()
    r,t = g.get_result()
    print t
