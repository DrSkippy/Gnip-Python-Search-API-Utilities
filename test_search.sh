#!/usr/bin/env bash

###
### edit creds
###
un=email
un=shendrickson@gnip.com
paswd=password
paswd=$1

if [ ! -d data ]; then
    mkdir data
fi

rulez="bieber OR bieber"
if [ $(uname) == "Linux" ]; then
    dt1=$(date --date="1 day ago" +%Y-%m-%dT00:00:00)
    dt2=$(date --date="2 days ago" +%Y-%m-%dT00:00:00)
    dt3=$(date --date="2 days ago" +%Y-%m-%dT23:55:00)
else
    dt1=$(date -v-1d +%Y-%m-%dT00:00:00)
    dt2=$(date -v-2d +%Y-%m-%dT00:00:00)
    dt3=$(date -v-2d +%Y-%m-%dT23:55:00)
fi

./search.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 -q json
./search.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 json
./search.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 geo
./search.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 wordcount
./search.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 timeline
./search.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 users
./search.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 -c geo
./search.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 -c timeline 
./search.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 -s"$dt2" -e"$dt1" json
./search.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 -s"$dt2" -e"$dt1" geo
./search.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 -s"$dt2" -e"$dt1" wordcount
./search.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 -s"$dt2" -e"$dt1" users
./search.py -f"has:geo $rulez" -u ${un} -p ${paswd} -s"$dt3" -e"$dt1" -aw ./data json
./search.py -f"has:geo $rulez" -u ${un} -p ${paswd} -s"$dt3" -e"$dt1" -aw ./data geo
./search.py -f"has:geo $rulez" -u ${un} -p ${paswd} -s"$dt3" -e"$dt1" -a users

export GNIP_CONFIG_FILE=./.gnip
./search.py -f"has:geo $rulez"  -n10 -q json
./search.py -f"has:geo $rulez"  -n10 json
./search.py -f"has:geo $rulez"  -n10 geo
./search.py -f"has:geo $rulez"  -n10 wordcount
./search.py -f"has:geo $rulez"  -n10 timeline
./search.py -f"has:geo $rulez"  -n10 users
./search.py -f"has:geo $rulez"  -n10 -c geo
./search.py -f"has:geo $rulez"  -n10 -c timeline 
./search.py -f"has:geo $rulez"  -n10 -s"$dt2" -e"$dt1" json
./search.py -f"has:geo $rulez"  -n10 -s"$dt2" -e"$dt1" geo
./search.py -f"has:geo $rulez"  -n10 -s"$dt2" -e"$dt1" wordcount
./search.py -f"has:geo $rulez"  -n10 -s"$dt2" -e"$dt1" users
./search.py -f"has:geo $rulez"  -s"$dt3" -e"$dt1" -aw ./data json

