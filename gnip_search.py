#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__="Scott Hendrickson, Jeff Kolb, Josh Montague" 

import sys
import json
import codecs
import argparse
import datetime
import time
import os

if sys.version_info.major == 2:
    import ConfigParser as configparser
else:
    import configparser

from search.results import * 

if (sys.version_info[0]) < 3:
    try:
        reload(sys)
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
        sys.stdin = codecs.getreader('utf-8')(sys.stdin)
    except NameError:
        pass

DEFAULT_CONFIG_FILENAME = "./.gnip"

class GnipSearchCMD():

    USE_CASES = ["json", "wordcount","users", "rate", "links", "timeline", "geo", "audience"]
    
    def __init__(self, token_list_size=40):
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
            except (configparser.NoOptionError,
                    configparser.NoSectionError) as e:
                sys.stderr.write("Error reading configuration file ({}), ignoring configuration file.".format(e))
        # parse the command line options
        self.options = self.args().parse_args()
        if int(sys.version_info[0]) < 3:
            self.options.filter = self.options.filter.decode("utf-8")
        # set up the job
        # over ride config file with command line args if present
        if self.options.user is not None:
            self.user = self.options.user
        if self.options.password is not None:
            self.password = self.options.password
        if self.options.stream_url is not None:
            self.stream_url = self.options.stream_url

        # exit if the config file isn't set
        if (self.stream_url is None) or (self.user is None) or (self.password is None):
            sys.stderr.write("Something is wrong with your configuration. It's possible that the we can't find your config file.")
            sys.exit(-1)

        # Gnacs is not yet upgraded to python3, so don't allow CSV output option (which uses Gnacs) if python3
        if self.options.csv_flag and sys.version_info.major == 3:
            raise ValueError("CSV option not yet available for Python3")

    def config_file(self):
        config = configparser.ConfigParser()
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
                help="Maximum results to return per page (default 100; max 500)")
        twitter_parser.add_argument("-N", "--hard-max", dest="hard_max", default=None, type=int,
                help="Maximum results to return for all pages; see -a option")
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
        # depricated... leave in for compatibility
        twitter_parser.add_argument("-t", "--search-v2", dest="search_v2", action="store_true",
                default=False, 
                help="Using search API v2 endpoint. [This is depricated and is automatically set based on endpoint.]")
        return twitter_parser
    
    def get_result(self):
        WIDTH = 80
        BIG_COLUMN = 32
        res = [u"-"*WIDTH]
        if self.options.use_case.startswith("time"):
            self.results = Results(
                self.user
                , self.password
                , self.stream_url
                , self.options.paged
                , self.options.output_file_path
                , pt_filter=self.options.filter
                , max_results=int(self.options.max)
                , start=self.options.start
                , end=self.options.end
                , count_bucket=self.options.count_bucket
                , show_query=self.options.query
                , hard_max=self.options.hard_max
                )
            res = []
            if self.options.csv_flag:
                for x in self.results.get_time_series():
                    res.append("{:%Y-%m-%dT%H:%M:%S},{},{}".format(x[2], x[0], x[1]))
            else:
                res = [x for x in self.results.get_activities()]
                return '{"results":' + json.dumps(res) + "}"

        else:
            self.results = Results(
                self.user
                , self.password
                , self.stream_url
                , self.options.paged
                , self.options.output_file_path
                , pt_filter=self.options.filter
                , max_results=int(self.options.max)
                , start=self.options.start
                , end=self.options.end
                , count_bucket=None
                , show_query=self.options.query
                , hard_max=self.options.hard_max
                )
            if self.options.use_case.startswith("rate"):
                rate = self.results.query.get_rate()
                unit = "Tweets/Minute"
                if rate < 0.01:
                    rate *= 60.
                    unit = "Tweets/Hour"
                res.append("     PowerTrack Rule: \"%s\""%self.options.filter)
                res.append("  Oldest Tweet (UTC): %s"%str(self.results.query.oldest_t))
                res.append("  Newest Tweet (UTC): %s"%str(self.results.query.newest_t))
                res.append("           Now (UTC): %s"%str(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))
                res.append("        %5d Tweets: %6.3f %s"%(len(self.results), rate, unit))
                res.append("-"*WIDTH)
            elif self.options.use_case.startswith("geo"):
                res = []
                for x in self.results.get_geo():
                    if self.options.csv_flag:
                        try:
                            res.append("{},{},{},{}".format(x["id"], x["postedTime"], x["longitude"], x["latitude"]))
                        except KeyError as e:
                            print >> sys.stderr, str(e)
                    else:
                        res.append(json.dumps(x))
            elif self.options.use_case.startswith("json"):
                res = [json.dumps(x) for x in self.results.get_activities()]
                if self.options.csv_flag:
                    res = ["|".join(x) for x in self.results.query.get_list_set()]
            elif self.options.use_case.startswith("word"):
                fmt_str = u"%{}s -- %10s     %8s ".format(BIG_COLUMN)
                res.append(fmt_str%( "terms", "mentions", "activities"))
                res.append("-"*WIDTH)
                fmt_str =  u"%{}s -- %4d  %5.2f%% %4d  %5.2f%%".format(BIG_COLUMN)
                for x in self.results.get_top_grams(n=self.token_list_size):
                    res.append(fmt_str%(x[4], x[0], x[1]*100., x[2], x[3]*100.))
                res.append("    TOTAL: %d activities"%len(self.results))
                res.append("-"*WIDTH)
            elif self.options.use_case.startswith("user"):
                fmt_str = u"%{}s -- %10s     %8s ".format(BIG_COLUMN)
                res.append(fmt_str%( "terms", "mentions", "activities"))
                res.append("-"*WIDTH)
                fmt_str =  u"%{}s -- %4d  %5.2f%% %4d  %5.2f%%".format(BIG_COLUMN)
                for x in self.results.get_top_users(n=self.token_list_size):
                    res.append(fmt_str%(x[4], x[0], x[1]*100., x[2], x[3]*100.))
                res.append("    TOTAL: %d activities"%len(self.results))
                res.append("-"*WIDTH)
            elif self.options.use_case.startswith("link"):
                res[-1]+=u"-"*WIDTH
                res.append(u"%100s -- %10s     %8s (%d)"%("links", "mentions", "activities", len(self.results)))
                res.append("-"*2*WIDTH)
                for x in self.results.get_top_links(n=self.token_list_size):
                    res.append(u"%100s -- %4d  %5.2f%% %4d  %5.2f%%"%(x[4], x[0], x[1]*100., x[2], x[3]*100.))
                res.append("-"*WIDTH)
            elif self.options.use_case.startswith("audie"):
                for x in self.results.get_users():
                    res.append(u"{}".format(x))
                res.append("-"*WIDTH)
        return u"\n".join(res)

if __name__ == "__main__":
    g = GnipSearchCMD()
    print(g.get_result())
