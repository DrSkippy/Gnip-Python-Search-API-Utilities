#!/usr/bin/env Rscript
# Time line plots
# plot two identical timeline plots counts vs. counts to see relative growth
# scott hendrickson
# @drskippy
#
library(ggplot2)
##############
# Args are infile, outfile, title, time_period_string
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 3) {
    print(args)
    stop("Error! 3 arguments required (infile1[.csv], infile2[.csv], outfile[.csv], title). Don't include the csv.")
}
##############
Y1 = read.delim(paste(sep="", args[1], ".csv"), sep=",", header=TRUE)
colnames(Y1) <- c("time","ts","count")
Y1$date <- as.POSIXct(Y1$time, format="%Y-%m-%dT%H:%M:%S")
Y1$series <- as.factor(args[1])
##############
Y2 = read.delim(paste(sep="", args[2], ".csv"), sep=",", header=TRUE)
colnames(Y2) <- c("time","ts","count")
Y2$date <- as.POSIXct(Y2$time, format="%Y-%m-%dT%H:%M:%S")
Y2$series <- as.factor(args[2])
##############
Y <- Y1
Y$count2 <- Y2$count
##############
png(filename = paste(sep="", args[3], ".png"), width = 550, height = 550, units = 'px')
    ggplot(data=Y) +
	geom_point(aes(count, count2), size=1) + 
	stat_smooth(aes(count, count2), method="lm", size=1) + 
	geom_abline(intercept=0, slope=1) + 
    labs(title = args[3]) +
    xlab(args[1]) +
    ylab(paste(args[2])) +
    theme(legend.position = 'none', text = element_text(size=20))
dev.off()
##############
Y$count <- (Y$count - min(Y$count))/(max(Y$count) - min(Y$count))
Y$count2 <- (Y$count2 - min(Y$count2))/(max(Y$count2) - min(Y$count2))
png(filename = paste(sep="", args[3], "_norm.png"), width = 550, height = 550, units = 'px')
    ggplot(data=Y) +
	geom_point(aes(count, count2), size=1) + 
	stat_smooth(aes(count, count2), method="lm", size=1) + 
	geom_abline(intercept=0, slope=1) + 
    labs(title = args[3]) +
    xlab(args[1]) +
    ylab(paste(args[2])) +
    theme(legend.position = 'none', text = element_text(size=20))
dev.off()
##############
