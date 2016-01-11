#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__="Scott Hendrickson, Josh Montague" 

import sys
import json
import codecs
import argparse
import datetime
import time
import numbers
import os
import ConfigParser
import logging
try:
        from cStringIO import StringIO
except:
        from StringIO import StringIO

import pandas as pd
import numpy as np

from search.results import *

reload(sys)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stdin = codecs.getreader('utf-8')(sys.stdin)

DEFAULT_CONFIG_FILENAME = "./.gnip"
LOG_FILE_PATH = os.path.join(".","filter_analysis.log")

# set up simple logging
logging.basicConfig(filename=LOG_FILE_PATH,level=logging.DEBUG)
logging.info("#"*70)
logging.info("################# started {} #################".format(datetime.datetime.now()))

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
                logging.debug(u"Error reading configuration file ({}), ignoring configuration file.".format(e))
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
            logging.debug(u"Requires search v2, but your URL appears to point to a v1 endpoint. Exiting.")
            print >> sys.stderr, "Requires search v2, but your URL appears to point to a v1 endpoint. Exiting."
            sys.exit(-1)
        # defaults
        self.options.paged = True
        self.options.max = 500
        # 
        # check paths
        if self.options.output_file_path is not None:
            if not os.path.exists(self.options.output_file_path):
                logging.debug(u"Path {} doesn't exist. Please create it and try again. Exiting.".format(
                    self.options.output_file_path))
                sys.stderr.write("Path {} doesn't exist. Please create it and try again. Exiting.\n".format(
                    self.options.output_file_path))
                sys.exit(-1)
        #
        # log the attributes of this class including all of the options
        for v in dir(self):
            # except don't log the password!
            if not v.startswith('__') and not callable(getattr(self,v)) and not v.lower().startswith('password'):
                tmp = str(getattr(self,v))
                tmp = re.sub("password=.*,", "password=XXXXXXX,", tmp) 
                logging.debug(u"  {}={}".format(v, tmp))
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
                description="Creates an aggregated filter statistics summary from \
                    filter rules and date periods in the job description.")
        twitter_parser.add_argument("-j", "--job_description", dest="job_description",
                default="./job.json",
                help="JSON formatted job description file")
        twitter_parser.add_argument("-b", "--bucket", dest="count_bucket", 
                default="day", 
                help="Bucket size for counts query. Options are day, hour, \
                    minute (default is 'day').")
        twitter_parser.add_argument("-l", "--stream-url", dest="stream_url", 
                default=None,
                help="Url of search endpoint. (See your Gnip console.)")
        twitter_parser.add_argument("-p", "--password", dest="password", default=None, 
                help="Password")
        twitter_parser.add_argument("-r", "--rank_sample", dest="rank_sample"
                , default=None
                , help="Rank inclusive sampling depth. Default is None. This runs filter rule \
                    production for rank1, rank1 OR rank2, rank1 OR rank2 OR rank3, etc.to \
                    the depths specifed.")
        twitter_parser.add_argument("-m", "--rank_negation_sample", dest="rank_negation_sample"
                , default=False
                , action="store_true"
                , help="Like rank inclusive sampling, but rules of higher ranks are negated \
                    on successive retrievals. Uses rank_sample setting.")
        twitter_parser.add_argument("-n", "--negation_rules", dest="negation_rules"
                , default=False
                , action="store_true"
                , help="Apply entire negation rules list to all queries")
        twitter_parser.add_argument("-q", "--query", dest="query", action="store_true", 
                default=False, help="View API query (no data)")
        twitter_parser.add_argument("-u", "--user-name", dest="user", default=None,
                help="User name")
        twitter_parser.add_argument("-w", "--output-file-path", dest="output_file_path", 
                default="./data",
                help="Create files in ./OUTPUT-FILE-PATH. This path must exists and will \
                    not be created. Default is ./data")

        return twitter_parser

    def read_job_description(self, job_description):
        with codecs.open(job_description, "rb", "utf-8") as f:
            self.job_description = json.load(f)
        if not all([x in self.job_description for x in ("rules", "date_ranges")]):
            print >>sys.stderr, '"rules" or "date_ranges" missing from you job description file. Exiting.\n'
            logging.error('"rules" or "date_ranges" missing from you job description file. Exiting')
            sys.exit(-1)
    
    def get_date_ranges_for_rule(self, rule, base_rule, tag=None):
        res = []
        for dates_dict in self.job_description["date_ranges"]:
            start_date = dates_dict["start"]
            end_date = dates_dict["end"]
            logging.debug(u"getting date range for {} through {}".format(start_date, end_date))
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
                res.append(x + [rule, tag,  start_date, end_date, base_rule])
        return res

    def get_pivot_table(self, res):
        df = pd.DataFrame(res
            , columns=("bucket_datetag"
                    ,"counts"
                    ,"bucket_datetime"
                    ,"filter"
                    ,"filter_tag"
                    ,"start_date"
                    ,"end_date"
                    ,"base_rule"))
        pdf = pd.pivot_table(df
            , values="counts"
            , index=["filter", "base_rule"]
            , columns = ["start_date"]
            , margins = True
            , aggfunc=np.sum)
        pdf.sort_values("All"
            , inplace=True
            , ascending=False)
        logging.debug(u"pivot tables calculated with shape(df)={} and shape(pdf)={}".format(df.shape, pdf.shape))
        return df, pdf

    def write_output_files(self, df, pdf, pre=""):
        if pre != "":
            pre += "_"
        logging.debug(u"Writing raw and pivot data to {}...".format(self.options.output_file_path))
        with open("{}/{}_{}raw_data.csv".format(
                    self.options.output_file_path
                    , datetime.datetime.now().strftime("%Y%m%d_%H%M")
                    , pre)
                , "wb") as f:
            f.write(df.to_csv(encoding='utf-8'))
        with open("{}/{}_{}pivot_data.csv".format(
                    self.options.output_file_path
                    , datetime.datetime.now().strftime("%Y%m%d_%H%M")
                    , pre)
                , "wb") as f:
            f.write(pdf.to_csv(encoding='utf-8'))

    def get_result(self):
        if self.options.negation_rules and self.job_description["negation_rules"] is not None:
            negation_rules = [x["value"] for x in self.job_description["negation_rules"]]
            negation_clause = " -(" + " OR ".join(negation_rules) + ")"
        else:
            negation_clause = ""
        all_rules = []
        res = []
        for rule_dict in self.job_description["rules"]:
            # in the case that rule is compound, ensure grouping
            rule = u"(" + rule_dict["value"] + u")" + negation_clause
            logging.debug(u"rule str={}".format(rule))
            all_rules.append(rule_dict["value"])
            tag = None
            if "tag" in rule_dict:
                tag = rule_dict["tag"]
            res.extend(self.get_date_ranges_for_rule(
                rule
                , rule_dict["value"]
                , tag=tag
                ))
        # All rules 
        all_rules_res = []
        sub_all_rules = []
        filter_str_last = u"(" + u" OR ".join(sub_all_rules) + u")"
        for rule in all_rules:
            # try adding one more rule
            sub_all_rules.append(rule)
            filter_str = u"(" + u" OR ".join(sub_all_rules) + u")"
            if len(filter_str + negation_clause) > 2048:
                # back up one rule if the length is too too long
                filter_str = filter_str_last
                logging.debug(u"All rules str={}".format(filter_str + negation_clause))
                all_rules_res = self.get_date_ranges_for_rule(
                    filter_str + negation_clause
                    , filter_str
                    , tag=None
                    )
                # start a new sublist
                sub_all_rules = [rule]
                filter_str = u"(" + u" OR ".join(sub_all_rules) + u")"
            filter_str_last = filter_str
        res.extend(all_rules_res)
        df, pdf = self.get_pivot_table(res)
        if self.options.output_file_path is not None:
            self.write_output_files(df, pdf)
        # rank inclusive results
        rdf, rpdf = None, None
        if self.options.rank_sample is not None:
            # because margin = True, we have an "all" row at the top
            # the second row will be the all_rules results, skip these too
            # therefore, start at the third row 
            rank_list = [x[1] for x in pdf.index.values[2:2+int(self.options.rank_sample)]]
            res = all_rules_res
            for i in range(int(self.options.rank_sample)):
                if self.options.rank_negation_sample:
                    filter_str = "((" + u") -(".join(rank_list[i+1::-1]) + "))"
                else:
                    filter_str = "((" + u") OR (".join(rank_list[:i+1]) + "))"
                logging.debug(u"rank rules str={}".format(filter_str + negation_clause))
                res.extend(self.get_date_ranges_for_rule(
                    filter_str + negation_clause
                    , filter_str
                    , tag=None
                    ))
            rdf, rpdf = self.get_pivot_table(res)
            if self.options.output_file_path is not None:
                self.write_output_files(rdf, rpdf, pre="ranked")
        return df, pdf, rdf, rpdf

if __name__ == "__main__":
    g = GnipSearchCMD()
    df, pdf, rdf, rpdf = g.get_result()
    sys.stdout.write(pdf.to_string())
    print
    print
    if rpdf is not None:
        sys.stdout.write(rpdf.to_string())
        print
