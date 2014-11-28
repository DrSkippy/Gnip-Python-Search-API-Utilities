#!/usr/bin/env python
####################################################################
# Various signal processing on time series from search api
#
# Scott Hendrickson
#    @drskippy
# 2014-11-28
#
# Detect peaks and output date
#
# INPUT (buckets of hours):
#    datetime string, count
#
# OUTPUT:
#    datetime string, model_value, model_type
#
####################################################################
# ranges for data collection
import sys
import csv
import datetime
from functools import partial

import numpy
from scipy import signal
import statsmodels.api as sm

# https://github.com/hildensia/bayesian_changepoint_detection/
import bayesian_changepoint_detection.offline_changepoint_detection as offcd

wrtr = csv.writer(sys.stdout)
####################################################################
# Configurations
OUTLIER_FRAC = 0.2
FMT = "%Y-%m-%dT%H:%M:%S"
N_PEAKS = 6

####################################################################
# initialize hours for averages
hours_data = {i:[] for i in range(24)}
# initialize data lists
dates = []
data = []
# read data in date, count format
for row in csv.reader(sys.stdin):
    data.append(float(row[2]))
    dates.append(datetime.datetime.strptime(row[0], FMT))

####################################################################
# detrend the data
data_no_trend = signal.detrend(numpy.array(data))
#print >>sys.stderr, data_no_trend

# hourly data buckets
for x,y in zip(dates,list(data_no_trend)):
    hours_data[x.hour].append(y)

# remove upper outliers for hourly averages 
n_remove = int(OUTLIER_FRAC * len(data)/24.) 
#print >>sys.stderr, n_remove

hours_avg = {i:numpy.average(sorted(hours_data[i])[:-n_remove]) for i in range(24)}
#print >>sys.stderr, hours_avg

# flatten daily cycle
data_no_day = numpy.array([data_no_trend[i] - hours_avg[dates[i].hour] for i in range(len(data))])
#print >>sys.stderr, data_no_day

#moving average size N
#N = 8
#data_1 = numpy.convolve(data_1, numpy.ones((N,))/N, mode='valid')

####################################################################
# peak detection
peakind = signal.find_peaks_cwt(data_no_day, numpy.arange(1,36), min_snr = .75)

#filter for top
top_peaks = sorted([(data[i+1], i) for i in peakind])[-N_PEAKS:]

# sort by date order
top_peaks = sorted([i[1] for i in top_peaks])
#print >> sys.stderr, top_peaks

# step across peak from t-1 starting point
for p in top_peaks:
    i = p-1
    while data[i] >= data[p-1]:
        i += 1
    wrtr.writerow([dates[p-1].strftime(FMT), 0, 0, "2_peaks"])
    wrtr.writerow([dates[p-1].strftime(FMT), 0, data[p+1], "2_peaks"])
    wrtr.writerow([dates[i].strftime(FMT), 0, data[p+1], "2_peaks"])
    wrtr.writerow([dates[i].strftime(FMT), 0, 0, "2_peaks"])

####################################################################
# stats models trend and cycle
 
cycle, trend = sm.tsa.filters.hpfilter(numpy.array(data))

for i in range(len(dates)):
    wrtr.writerow([dates[i].strftime(FMT), 0, cycle[i], "3_tc_cycle"])
for i in range(len(dates)):
    wrtr.writerow([dates[i].strftime(FMT), 0, trend[i], "4_tc_trend"])

####################################################################
# change point detection

Q, P, Pcp = offcd.offline_changepoint_detection(trend
        , partial(offcd.const_prior
        , l=(len(trend)+1))
        , offcd.gaussian_obs_log_likelihood, truncate=-20)

for d,x in zip(dates, list(numpy.exp(Pcp).sum(0))):
    wrtr.writerow([d.strftime(FMT), 0, x, "5_change_points"])

