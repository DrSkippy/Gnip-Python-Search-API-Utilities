#!/usr/bin/env Rscript
library(ggplot2)
# args are infile, outfile, title, time_period_string
args <- commandArgs(trailingOnly = TRUE)
#print(args)
Y = read.delim(args[1], sep=",", header=TRUE)
colnames(Y) <- c("time","count")
Y$date <- as.POSIXct(Y$time, format="%Y-%m-%dT%H:%M:%S")
png(filename = paste(sep="", args[2], ".png"), width = 850, height = 500, units = 'px')
    ggplot(data=Y) +
	geom_point(aes(date, count), size=1) + 
	geom_line(aes(date, count), color="#00aced", size=1) + 
    labs(title = args[3]) +
    xlab("date and time (UTC)") +
    ylab(paste("tweets/",args[4],sep="")) +
    theme(legend.position = 'none', text = element_text(size=20))
dev.off()
 
