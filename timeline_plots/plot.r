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
colnames(Y) <- c("time","ts","count")
Y$date <- as.POSIXct(Y$time, format="%Y-%m-%dT%H:%M:%S")
##############
png(filename = paste(sep="", args[2], ".png"), width = 750, height = 400, units = 'px')
    ggplot(data=Y) +
	geom_point(aes(date, count), size=1) + 
	geom_line(aes(date, count), color="#00aced", size=1) + 
    labs(title = args[3]) +
    xlab("date and time (UTC)") +
    ylab(paste("tweets/",args[4],sep="")) +
    theme(legend.position = 'none', text = element_text(size=20))
dev.off()
##############
Y$signal_type = as.factor("1_time_line")

X1 = read.delim(paste(sep="", args[1], "_sig.csv"), sep=",", header=TRUE)
colnames(X1) <- c("time","ts","count","signal_type")
X1$date <- as.POSIXct(X1$time, format="%Y-%m-%dT%H:%M:%S")
X1$signal_type <- as.factor(X1$signal_type)
X = rbind(X1,Y)
#X$signal_type <- factor(X$signal_type, order(X$signal_type))
png(filename = paste(sep="", args[2], "_sig.png"), width = 750, height = 900, units = 'px')
    ggplot(data=X) +
	geom_line(aes(date, count, color=signal_type), size=1) + 
    facet_wrap(~signal_type, ncol=1, scale="free_y") +
    labs(title = args[3]) +
    xlab("date and time (UTC)") +
    ylab(paste("tweets/",args[4],sep="")) +
    theme(legend.position = 'none', text = element_text(size=20))
dev.off()
##############
for (i in 1:6) {
    print(paste(sep="", args[1], "_", i, "_freq.csv"))
    Z = read.delim(paste(sep="", args[1], "_", i, "_freq.csv"), sep=",", header=TRUE)

    png(filename = paste(sep="", args[2], "_", i, "_treemap.png"), width = 750, height = 750, units = 'px')
        treemap(Z, index=c("tokens"), vSize="percent.of.total")
    dev.off()
    ##############
    Z <- transform(Z, tokens=reorder(tokens, total.count))
    png(filename = paste(sep="", args[2], "_", i, "_points.png"), width = 750, height = 900, units = 'px')
        print(ggplot(data=Z, aes(y=tokens, x=total.count, color=n_gram, size=1.5)) + 
            geom_point(stat="identity") +
            #facet_wrap(~n_gram, ncol=1) +
            labs(title = args[3]) +
            theme(text = element_text(size=20))
)
    dev.off()
}
summary(X) 
