#!/usr/bin/env python
import sys
import csv
import datetime
import numpy
from scipy import signal

wrtr = csv.writer(sys.stdout)

hours_data = {i:[] for i in range(24)}

dates = []
data = []
for row in csv.reader(sys.stdin):
    x = datetime.datetime.strptime(row[0], "%Y-%m-%dT%H:%M:%S")
    data.append(float(row[1]))
    dates.append(x)
    hours_data[x.hour].append(float(row[1]))

# remove top n
n = 8
hours_avg = {i:numpy.average(sorted(hours_data[i])[:-n]) for i in range(24)}
data_1 = numpy.array([data[i] - hours_avg[dates[i].hour] for i in range(len(data))])
# moving average size N
N = 8
data_1 = numpy.convolve(data_1, numpy.ones((N,))/N, mode='valid')

peakind = signal.find_peaks_cwt(data_1, numpy.arange(1,36), min_snr = 1)
#filter for top
top = 4
top_peaks = sorted([(data[i+1], i) for i in peakind])[-top:]
top_peaks = sorted([i[1] for i in top_peaks])
#print >> sys.stderr, top_peaks

for p in top_peaks:
    #print >>sys.stderr, p, dates[p], data_1[p], data[p]
    i = p-1
    while data[i] >= data[p-1]:
        i += 1
    wrtr.writerow([dates[p-1], 0])
    wrtr.writerow([dates[p-1], data[p+1]])
    wrtr.writerow([dates[i], data[p+1]])
    wrtr.writerow([dates[i], 0])
    print >>sys.stderr, ' -s"{}" -e"{}" -n500 wordcount'.format(dates[p-1].strftime("%Y-%m-%dT%H:%M:%S"), dates[i].strftime("%Y-%m-%dT%H:%M:%S"))

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

