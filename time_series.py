#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__="Scott Hendrickson" 

import time
import sys
import statsmodels.api as sm
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import matplotlib
import json
import datetime
import csv
import codecs
import calendar
import argparse
import ConfigParser
from search.results import *
from scipy import signal
from operator import itemgetter
from functools import partial

reload(sys)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
sys.stdin = codecs.getreader('utf-8')(sys.stdin)

# some plot styling
matplotlib.style.use('ggplot')

# set up simple logging
import logging
logging.basicConfig(filename='time_series.log',level=logging.DEBUG)
logging.info("################# started {} #################".format(datetime.datetime.now()))

DEFAULT_CONFIG_FILENAME = "./.gnip"
DATE_FMT = "%Y%m%d%H%M"
DATE_FMT2 = "%Y-%m-%dT%H:%M:%S"
CHAR_UPPER_CUTOFF = 20
TWEET_SAMPLE = 10000
MIN_SNR = 0.75 
MAX_N_PEAKS = 5
MAX_PEAK_WIDTH = 36
PEAK_OFFSET = 5
N_MOVING = 4 
OUTLIER_FRAC = 0.8
START_OFFSET = 3

class TimeSeries():
    pass

class GnipSearchTimeseries():

    def __init__(self, token_list_size=20):
        # default tokenizer and character limit
        char_upper_cutoff = CHAR_UPPER_CUTOFF  # longer than for normal words because of user names
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
                logging.warn("Error reading configuration file ({}), ignoring configuration file.".format(e))
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
        
        # Search v2 uses a different url
        if "data-api.twitter.com" not in self.stream_url:
            logging.error("GnipSearch timeline tools require Search V2. Exiting.")
            exit(-1)

        # Defaults
        self.options.paged = True
        self.options.search_v2 = True
        self.options.max = 500
        self.options.query = False
        
        # log options
        logging.debug("### options ###")
        for v in dir(self):
            if not v.startswith('__') and not callable(getattr(self,v)) and not v.startswith('password'):
                logging.debug(" {} = {}".format(v, getattr(self,v)))

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
                description="GnipSearch timeline tools")
        twitter_parser.add_argument("-b", "--bucket", dest="count_bucket", 
                default="day", 
                help="Bucket size for counts query. Options are day, hour, minute (default is 'day').")
        twitter_parser.add_argument("-e", "--end-date", dest="end", 
                default=None,
                help="End of datetime window, format 'YYYY-mm-DDTHH:MM' (default: most recent activities)")
        twitter_parser.add_argument("-f", "--filter", dest="filter", 
                default="from:jrmontag OR from:gnip",
                help="PowerTrack filter rule (See: http://support.gnip.com/customer/portal/articles/901152-powertrack-operators)")
        twitter_parser.add_argument("-l", "--stream-url", dest="stream_url", 
                default=None,
                help="Url of search endpoint. (See your Gnip console.)")
        twitter_parser.add_argument("-p", "--password", dest="password", default=None, 
                help="Password")
        twitter_parser.add_argument("-s", "--start-date", dest="start", 
                default=None,
                help="Start of datetime window, format 'YYYY-mm-DDTHH:MM' (default: 30 days ago)")
        twitter_parser.add_argument("-u", "--user-name", dest="user", 
                default=None,
                help="User name")
        twitter_parser.add_argument("-w", "--output-file-path", dest="output_file_path", 
                default=None,
                help="Create files in ./OUTPUT-FILE-PATH. This path must exists and will not be created. This options is available only with -a option. Default is no output files.")
        return twitter_parser
    
    def get_results(self):
        ######################
        # (1) Get the timeline
        ######################
        results_timeseries = Results( self.user
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
            , search_v2=self.options.search_v2
            )
        # sort by date
        res_timeseries = sorted(results_timeseries.get_time_series(), key = itemgetter(0))
        # calculate total time interval span
        time_min_date = min(res_timeseries, key = itemgetter(2))[2]
        time_max_date = max(res_timeseries, key = itemgetter(2))[2]
        time_min = float(calendar.timegm(time_min_date.timetuple()))
        time_max = float(calendar.timegm(time_max_date.timetuple()))
        time_span = time_max - time_min
        logging.debug("time_min = {}, time_max = {}, time_span = {}".format(time_min, time_max, time_span))
        # create a simple object to hold our data 
        ts = TimeSeries()
        ts.dates = []
        ts.x = []
        ts.counts = []
        # load and format data
        for i in res_timeseries:
            ts.dates.append(i[2])
            ts.counts.append(float(i[1]))
            # crate a independent variable in interval [0.0,1.0]
            ts.x.append((calendar.timegm(datetime.datetime.strptime(i[0], DATE_FMT).timetuple()) - time_min)/time_span)
        logging.info("read {} time items from search API".format(len(ts.dates)))
        logging.debug('dates: ' + ','.join(map(str, ts.dates[:10])) + "...")
        logging.debug('counts: ' + ','.join(map(str, ts.counts[:10])) + "...")
        logging.debug('indep var: ' + ','.join(map(str, ts.x[:10])) + "...")
        ######################
        # (2) Detrend
        ######################
        no_trend = signal.detrend(np.array(ts.counts))
        # determine period of data
        df = (ts.dates[1] - ts.dates[0]).total_seconds()
        if df == 86400:
            # day counts, average over week
            n_buckets = 7
            n_avgs = {i:[] for i in range(n_buckets)}
            for t,c in zip(ts.dates, no_trend):
                n_avgs[t.weekday()].append(c)
        elif df == 3600:
            # hour counts, average over day
            n_buckets = 24
            n_avgs = {i:[] for i in range(n_buckets)}
            for t,c in zip(ts.dates, no_trend):
                n_avgs[t.hour].append(c)
        elif df == 60:
            # minute counts; average over day
            n_buckets = 24*60
            n_avgs = {i:[] for i in range(n_buckets)}
            for t,c in zip(ts.dates, no_trend):
                n_avgs[t.minute].append(c)
        else:
            print "Weird interval problem! Exiting."
            sys.exit()
        logging.info("averaging over periods of {} buckets".format(n_buckets))
        # remove upper outliers from averages 
        df_avg_all = {i:np.average(n_avgs[i]) for i in range(n_buckets)}
        logging.debug("bucket averages: {}".format(','.join(map(str, [df_avg_all[i] for i in df_avg_all]))))
        n_avgs_remove_outliers = {i: [j for j in n_avgs[i] 
            if  abs(j - df_avg_all[i])/df_avg_all[i] < (1. + OUTLIER_FRAC) ]
            for i in range(n_buckets)}
        df_avg = {i:np.average(n_avgs_remove_outliers[i]) for i in range(n_buckets)}
        logging.debug("bucket averages w/o outliers: {}".format(','.join(map(str, [df_avg[i] for i in df_avg]))))

        # flatten cycle
        ts.counts_no_cycle_trend = np.array([no_trend[i] - df_avg[ts.dates[i].hour] for i in range(len(ts.counts))])
        logging.debug('no trend: ' + ','.join(map(str, ts.counts_no_cycle_trend[:10])) + "...")

        ######################
        # (3) Moving average 
        ######################
        ts.moving = np.convolve(ts.counts, np.ones((N_MOVING,))/N_MOVING, mode='valid')
        logging.debug('moving ({}): '.format(N_MOVING) + ','.join(map(str, ts.moving[:10])) + "...")

        ######################
        # (4) Peak detection
        ######################
        peakind = signal.find_peaks_cwt(ts.counts_no_cycle_trend, np.arange(1,MAX_PEAK_WIDTH), min_snr = MIN_SNR)
        n_peaks = min([MAX_N_PEAKS, len(peakind)])
        logging.debug('peaks ({}): '.format(n_peaks) + ','.join(map(str, peakind)) + "...")
        logging.debug('peaks ({}): '.format(n_peaks) + ','.join(map(str, [ts.dates[i] for i in peakind])) + "...")
        
        # top peaks determined by peak height, better way?
        # peak detector
        #       is leading by a few periods or up to 1 period late
        #       finds peaks up to MAX_PEAK_WIDTH wide
        #       peak size by volume
        #
        #   alg0: find max, find fwhm, find start, step past peak, keep track of volume and peak height
        peaks = []
        for i in peakind:
            # find the first max in the possible window
            tmp = [0]
            i_max = None
            for j in range(max([i-1, 0]), min(i + MAX_PEAK_WIDTH, len(ts.dates))):
                if tmp[-1] > ts.counts[j]:
                    # record index of peak
                    i_max = j - 1 
                    break
                else:
                    tmp.append(ts.counts[j])
            # dropped off the end of data
            if i_max is None:
                i_max = min(i + MAX_PEAK_WIDTH, len(ts.dates) - 1) 
            p_max = max(tmp)
            h_max = p_max/2.
            p_sum = 0
            tmp = []
            i_start, i_finish = None, None
            for j in range(max([i-START_OFFSET, 0]), min(i + MAX_PEAK_WIDTH, len(ts.dates))): 
                if j <= i_max:
                    # before or on peak
                    if ts.counts[j] > h_max:
                        if i_start is None:
                            i_start = j - 1
                        tmp.append(ts.counts[j])
                else:
                    # past peak and going up
                    if ts.counts[j] > tmp[-1] or ts.counts[j] < h_max:
                        # going back up
                        i_finish = j
                        break
                    else:
                        tmp.append(ts.counts[j])
            if i_start is None:
                i_start = max([i-1, 0])
            if i_finish is None:
                i_finish = min(i + MAX_PEAK_WIDTH, len(ts.dates)) - 1
            p_volume = sum(tmp)
            peaks.append([ i , p_volume , (i, i_start, i_max, i_finish
                                            , h_max  , p_max, p_volume
                                            , ts.dates[i_start], ts.dates[i_max], ts.dates[i_finish])])
        logging.debug(peaks)           
        # top n_peaks by volume
        top_peaks = sorted(peaks, key = itemgetter(1))[-n_peaks:]
        # re-sort peaks by date
        ts.top_peaks = sorted(top_peaks, key = itemgetter(0))
        logging.debug('top peaks ({}): '.format(len(ts.top_peaks)) + ','.join(map(str, ts.top_peaks)) + "...")
    
        ######################
        # (5) high/low frequency 
        ######################
        ts.cycle, ts.trend = sm.tsa.filters.hpfilter(np.array(ts.counts))
        logging.debug('cycle: ' + ','.join(map(str, ts.cycle[:10])) + "...")
        logging.debug('trend: ' + ','.join(map(str, ts.trend[:10])) + "...")
    
        ######################
        # (6) n-grams for top peaks
        ######################
        ts.topics = []
        for a in ts.top_peaks:
            # start at peak
            ds = datetime.datetime.strftime(a[2][8], DATE_FMT2)
            # estimate how long to get TWEET_SAMPLE tweets
            # a[1] is max tweets per period
            est_periods = float(TWEET_SAMPLE)/a[1]
            # df comes from above, in seconds
            # time resolution is hours
            est_time = max([int(est_periods * df), 60])
            logging.debug("est_periods={}, est_time={}".format(est_periods, est_time))
            #
            if a[2][8] + datetime.timedelta(seconds=est_time) < a[2][9]:
                de = datetime.datetime.strftime(a[2][8] + datetime.timedelta(seconds=est_time), DATE_FMT2)
            elif a[2][8] < a[2][9]:
                de = datetime.datetime.strftime(a[2][9], DATE_FMT2)
            else:
                de = datetime.datetime.strftime(a[2][8] + datetime.timedelta(seconds=60), DATE_FMT2)

            logging.info("retreive data for peak index={} [{},{}]".format(a[0], ds, de))
            res = Results(
                self.user
                , self.password
                , self.stream_url
                , self.options.paged
                , self.options.output_file_path
                , pt_filter=self.options.filter
                , max_results=int(self.options.max)
                , start=ds
                , end=de
                , count_bucket=None
                , show_query=self.options.query
                , search_v2=self.options.search_v2
                )
            n_grams = list(res.get_top_grams(n=self.token_list_size))
            ts.topics.append(n_grams)
            logging.debug(n_grams)
        return ts

    def plots(self, ts):
        # timeline
        df0 = pd.Series(ts.counts, index=ts.dates)
        df0.plot()
        plt.tight_layout()
        plt.savefig('./plots/time_line.pdf')
        plt.close("all")
        # cycle and trend
        df1 = pd.DataFrame({"cycle":ts.cycle, "trend":ts.trend}, index=ts.dates)
        df1.plot()
        plt.tight_layout()
        plt.savefig('./plots/cycle_trend_line.pdf')
        plt.close("all")
        # moving avg
        df2 = pd.DataFrame({"moving":ts.moving}, index=ts.dates[:len(ts.moving)])
        df2.plot()
        plt.tight_layout()
        plt.savefig('./plots/moving_line.pdf')
        plt.close("all")
        # timeline with peaks
        df3 = pd.Series(ts.counts, index=ts.dates)
        df3.plot()
        # peaks
        for a in ts.top_peaks:
            xs = a[2][7]
            xp = a[2][8]
            xe = a[2][9]
            y = a[2][5]
            # need to get x and y locs
            plt.axvspan(xs, xe, ymin=0, ymax = y, linewidth=1, color='g', alpha=0.3)
            plt.axvline(xp, ymin=0, ymax = y, linewidth=1, color='y')
        plt.tight_layout()
        plt.savefig('./plots/time_peaks_line.pdf')
        plt.close("all")



if __name__ == "__main__":
    g = GnipSearchTimeseries()
    ts = g.get_results()
    import pickle
    pickle.dump(ts,open("./deleteme.pickle", "wb"))
    ts = pickle.load(open("./deleteme.pickle", "rb"))
    g.plots(ts)
