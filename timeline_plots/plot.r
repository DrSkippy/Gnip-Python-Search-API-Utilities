#!/usr/bin/env Rscript
# Time line plots
# scott hendrickson
# @drskippy
#
library(ggplot2)
library(treemap)
##############
# Args are infile, outfile, title, time_period_string
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 4) {
    print(args)
    stop("Error! 4 arguments required (infile[.csv], outfile[.csv], title, time_period_string). Don't include the csv. time_period_string may be any of (minute, hour, day)")
}
##############
Y = read.delim(paste(sep="", args[1], ".csv"), sep=",", header=TRUE)
X = read.delim(paste(sep="", args[1], "_sig.csv"), sep=",", header=TRUE)
colnames(Y) <- c("time","count")
colnames(X) <- c("time","count","signal_type")
Y$date <- as.POSIXct(Y$time, format="%Y-%m-%dT%H:%M:%S")
X$date <- as.POSIXct(X$time, format="%Y-%m-%dT%H:%M:%S")
##############
png(filename = paste(sep="", args[2], ".png"), width = 850, height = 500, units = 'px')
    ggplot(data=Y) +
	geom_point(aes(date, count), size=1) + 
	geom_line(aes(date, count), color="#00aced", size=1) + 
    labs(title = args[3]) +
    xlab("date and time (UTC)") +
    ylab(paste("tweets/",args[4],sep="")) +
    theme(legend.position = 'none', text = element_text(size=20))
dev.off()
##############
Y$signal_type = "time_line"
X = rbind(X,Y)
png(filename = paste(sep="", args[2], "_sig.png"), width = 850, height = 500, units = 'px')
    ggplot(data=X) +
	geom_point(aes(date, count), size=1) + 
	geom_line(aes(date, count), color="#00aced", size=1) + 
    facet_wrap(~signal_type, ncol=1, scale="free_y") +
    labs(title = args[3]) +
    xlab("date and time (UTC)") +
    ylab(paste("tweets/",args[4],sep="")) +
    theme(legend.position = 'none', text = element_text(size=20))
dev.off()
##############
#png(filename = paste(sep="", args[2], "_hist.png"), width = 850, height = 500, units = 'px')
#    ggplot(data=Y) +
#	 geom_histogram(aes(count), fill="#00aced") + 
#    labs(title = args[3]) +
#    xlab(paste("tweets/",args[4],sep="")) +
#    ylab("count") + 
#    theme(legend.position = 'none', text = element_text(size=20))
#dev.off()
##############
for (i in 1:6) {
    print(paste(sep="", args[1], "_", i, "_freq.csv"))
    Z = read.delim(paste(sep="", args[1], "_", i, "_freq.csv"), sep=",", header=TRUE)
    png(filename = paste(sep="", args[2], "_", i, "_treemap.png"), width = 850, height = 500, units = 'px')
        treemap(Z, index=c("tokens"), vSize="percent.of.total")
    dev.off()
}
summary(Y) 
