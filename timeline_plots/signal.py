#!/usr/bin/env python
# Detect peaks and output date
# ranges for data collection
import sys
import csv
import datetime
import numpy
from scipy import signal
#
OUTLIER_FRAC = 0.2
FMT = "%Y-%m-%dT%H:%M:%S"
N_PEAKS = 4
#
wrtr = csv.writer(sys.stdout)
# initialize hours for averages
hours_data = {i:[] for i in range(24)}
# initialize data
dates = []
data = []
#
# read data in date, count format
for row in csv.reader(sys.stdin):
    data.append(float(row[1]))
    dates.append(datetime.datetime.strptime(row[0], FMT))
#
# detrend the data for peak detection
data_no_trend = signal.detrend(numpy.array(data))
#print >>sys.stderr, data_no_trend
#
# hourly cycle data
for x,y in zip(dates,list(data_no_trend)):
    hours_data[x.hour].append(y)
#
# remove upper outliers for hourly averages 
n_out = int(OUTLIER_FRAC * len(data)/24.) 
#print >>sys.stderr, n_out
hours_avg = {i:numpy.average(sorted(hours_data[i])[:-n_out]) for i in range(24)}
#print >>sys.stderr, hours_avg
#
# flatten daily cycle
data_no_day = numpy.array([data_no_trend[i] - hours_avg[dates[i].hour] for i in range(len(data))])
#print >>sys.stderr, data_no_day
#
#moving average size N
#N = 8
#data_1 = numpy.convolve(data_1, numpy.ones((N,))/N, mode='valid')
#
# peak detection
peakind = signal.find_peaks_cwt(data_no_day, numpy.arange(1,36), min_snr = 1)
#filter for top
top_peaks = sorted([(data[i+1], i) for i in peakind])[-N_PEAKS:]
# sort by date order
top_peaks = sorted([i[1] for i in top_peaks])
#print >> sys.stderr, top_peaks
#
# output date ranges for peaks
# two sets:
#   - for querying to make n-grams (target 500 records)
#   - for plotting (target ~fwhm)
for p in top_peaks:
    i = p-1
    while data[i] >= data[p-1]:
        i += 1
    wrtr.writerow([dates[p-1].strftime(FMT), 0])
    wrtr.writerow([dates[p-1].strftime(FMT), data[p+1]])
    wrtr.writerow([dates[i].strftime(FMT), data[p+1]])
    wrtr.writerow([dates[i].strftime(FMT), 0])
#
# change point experiements
#for i in range(len(data)):
    #wrtr.writerow([dates[i], data_1[i]])

#import bayesian_changepoint_detection.offline_changepoint_detection as offcd
#from functools import partial

#Q, P, Pcp = offcd.offline_changepoint_detection(data_1
#        , partial(offcd.const_prior
#        , l=(len(data_1)+1))
#        , offcd.gaussian_obs_log_likelihood, truncate=-20)

#for d,x in zip(data, list(numpy.exp(Pcp).sum(0))):
#    pass
#    wrtr.writerow([d[0], x*max(data_1)])
