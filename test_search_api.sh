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
dt1=$(date -v-1d +%Y-%m-%dT00:00:00)
dt2=$(date -v-2d +%Y-%m-%dT00:00:00)
dt3=$(date -v-2d +%Y-%m-%dT23:55:00)

./search_api.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 -q json
./search_api.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 json
./search_api.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 geo
./search_api.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 wordcount
./search_api.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 timeline
./search_api.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 users
./search_api.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 -c geo
./search_api.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 -c timeline 
./search_api.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 -s"$dt2" -e"$dt1" json
./search_api.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 -s"$dt2" -e"$dt1" geo
./search_api.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 -s"$dt2" -e"$dt1" wordcount
./search_api.py -f"has:geo $rulez" -u ${un} -p ${paswd} -n10 -s"$dt2" -e"$dt1" users
./search_api.py -f"has:geo $rulez" -u ${un} -p ${paswd} -s"$dt3" -e"$dt1" -aw ./data json
./search_api.py -f"has:geo $rulez" -u ${un} -p ${paswd} -s"$dt3" -e"$dt1" -aw ./data geo
./search_api.py -f"has:geo $rulez" -u ${un} -p ${paswd} -s"$dt3" -e"$dt1" -a users

export GNIP_CONFIG_FILE=./.gnip
./search_api.py -f"has:geo $rulez"  -n10 -q json
./search_api.py -f"has:geo $rulez"  -n10 json
./search_api.py -f"has:geo $rulez"  -n10 geo
./search_api.py -f"has:geo $rulez"  -n10 wordcount
./search_api.py -f"has:geo $rulez"  -n10 timeline
./search_api.py -f"has:geo $rulez"  -n10 users
./search_api.py -f"has:geo $rulez"  -n10 -c geo
./search_api.py -f"has:geo $rulez"  -n10 -c timeline 
./search_api.py -f"has:geo $rulez"  -n10 -s"$dt2" -e"$dt1" json
./search_api.py -f"has:geo $rulez"  -n10 -s"$dt2" -e"$dt1" geo
./search_api.py -f"has:geo $rulez"  -n10 -s"$dt2" -e"$dt1" wordcount
./search_api.py -f"has:geo $rulez"  -n10 -s"$dt2" -e"$dt1" users
./search_api.py -f"has:geo $rulez"  -s"$dt3" -e"$dt1" -aw ./data json

