#!/usr/bin/env bash
#
# Takes 1 arguement: Filter for search
# e.g. ./plot.sh "@drskippy"
#
# Be sure the export GNIP_CONFIG or have your .gnip in the local folder
# Set this or export env variable
SEARCH_PATH=/Users/scotthendrickson/IdeaProjects/Gnip-Python-Search-API-Utilities
# can use minute, hour, day for bucket size
BUCKET_SIZE=hour
$SEARCH_PATH/search_api.py -f"$1" -cb$BUCKET_SIZE timeline > data.csv
./plot.r data.csv "$1" "$1" "$BUCKET_SIZE"
# on OSX, if you want to immediatly see your plot
open "$1".png
