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
import ConfigParser

from gnip_search.gnip_search_api import *

reload(sys)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stdin = codecs.getreader('utf-8')(sys.stdin)

DEFAULT_CONFIG_FILENAME = "./.gnip"

class GnipSearchCMD(GnipSearchAPI):

    USE_CASES = ["json", "wordcount","users", "rate", "links", "timeline", "geo"]
    
    def __init__(self, token_list_size=20):
        # default tokenizer and character limit
        space_tokenizer = False
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
        #############################################
        super(GnipSearchCMD, self).__init__(
            self.user
            , self.password
            , self.stream_url
            , self.options.paged
            , self.options.output_file_path
            , self.token_list_size
            )

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
                description="GnipSearch supports the following use cases: %s"%str(self.USE_CASES))
        twitter_parser.add_argument("use_case", metavar= "USE_CASE", choices=self.USE_CASES, 
                help="Use case for this search.")
        twitter_parser.add_argument("-a", "--paged", dest="paged", action="store_true", 
                default=False, help="Paged access to ALL available results (Warning: this makes many requests)")
        twitter_parser.add_argument("-c", "--csv", dest="csv_flag", action="store_true", 
                default=False,
                help="Return comma-separated 'date,counts' or geo data.")
        twitter_parser.add_argument("-b", "--bucket", dest="count_bucket", 
                default="day", 
                help="Bucket size for counts query. Options are day, hour, minute (default is 'day').")
        twitter_parser.add_argument("-e", "--end-date", dest="end", 
                default=None,
                help="End of datetime window, format 'YYYY-mm-DDTHH:MM' (default: most recent activities)")
        twitter_parser.add_argument("-f", "--filter", dest="filter", default="from:jrmontag OR from:gnip",
                help="PowerTrack filter rule (See: http://support.gnip.com/customer/portal/articles/901152-powertrack-operators)")
        twitter_parser.add_argument("-l", "--stream-url", dest="stream_url", 
                default=None,
                help="Url of search endpoint. (See your Gnip console.)")
        twitter_parser.add_argument("-n", "--results-max", dest="max", default=100, 
                help="Maximum results to return (default 100)")
        twitter_parser.add_argument("-p", "--password", dest="password", default=None, 
                help="Password")
        twitter_parser.add_argument("-q", "--query", dest="query", action="store_true", 
                default=False, help="View API query (no data)")
        twitter_parser.add_argument("-s", "--start-date", dest="start", 
                default=None,
                help="Start of datetime window, format 'YYYY-mm-DDTHH:MM' (default: 30 days ago)")
        twitter_parser.add_argument("-u", "--user-name", dest="user", default=None,
                help="User name")
        twitter_parser.add_argument("-w", "--output-file-path", dest="output_file_path", default=None,
                help="Create files in ./OUTPUT-FILE-PATH. This path must exists and will not be created. This options is available only with -a option. Default is no output files.")
        return twitter_parser
    
    def __call__(self):
        return self.get_repr(
            self.options.filter
            , self.options.max
            , self.options.use_case
            , self.options.start
            , self.options.end
            , self.options.count_bucket 
            , self.options.csv_flag
            , self.options.query)
    
if __name__ == "__main__":
    print GnipSearchCMD()()
