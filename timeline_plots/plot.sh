#!/usr/bin/env bash
#
echo "######################################################################"
echo "USAGE: plot.sh takes 2 arguements: a valid powertrack filter, and a valid"
echo "       file name."
echo ""
echo "           e.g. ./plot.sh \"@drskippy\" \"MyTweets\""
echo 
echo "OUTPUT:    - Summary statistics table"
echo "           - ./examples/<filter>.png is the timeline"
echo "           - ./examples/<filter>_hist.png is the distribution of bucket volumes"
echo "           - 1- and 2-grams summary"
echo "           - treemap of 1- and 2-grams summary"
echo 
echo "REQUIREMENTS:"
echo "           - gnip search (install with e.g. sudo pip install gapi)"
echo "           - .gnip configuration file with your credentials"
echo "             in this directory or export appropirate environment"
echo "             variable"
echo "           - jq"
echo "           - r with ggplot and treemap libraries"
echo "           - python numpy and scipy"
# echo "           - python package https://github.com/hildensia/bayesian_changepoint_detection/tree/master/"
echo "######################################################################"
# can use minute, hour, day for bucket size
BUCKET_SIZE=hour
SEARCH_VERSION=""
SEARCH_VERSION="-t"
if [ ! -d ./examples ]; then
    mkdir ./examples
fi

# Timeline Search
../gnip_search.py $SEARCH_VERSION -f"$1" -c -b$BUCKET_SIZE timeline > "./examples/$2.csv" &
wait

# Signal processing
cat "./examples/${2}.csv" | ./signal.py | grep -v "scipy" > "./examples/${2}_sig.csv"
# build n-gram queries
cat "./examples/${2}_sig.csv" | "./make_query_str.py" "${1}" "${2}" "${SEARCH_VERSION}"> "./${2}_queries.sh"
# run n-gram queries we built
. ./${2}_queries.sh
# Plots!
./plot.r "./examples/$2" "./examples/$2" "$1" "$BUCKET_SIZE"
if [ $(uname) == "Darwin" ]; then
    # on OSX, if you want to immediatly see your plot
    # open "./examples/${2}_hist.png"
    open ./examples/${2}_*_treemap.png
    open ./examples/${2}_*_points.png
    sleep 2
    open ./examples/${2}_sig.png
    open ./examples/${2}.png
fi
