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

./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)" -u ${un} -p ${paswd} -n10 -q json
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)" -u ${un} -p ${paswd} -n10 json
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)" -u ${un} -p ${paswd} -n10 geo
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)" -u ${un} -p ${paswd} -n10 wordcount
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)" -u ${un} -p ${paswd} -n10 timeline
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)" -u ${un} -p ${paswd} -n10 users
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)" -u ${un} -p ${paswd} -n10 -c geo
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)" -u ${un} -p ${paswd} -n10 -c timeline 
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)" -u ${un} -p ${paswd} -n10 -s"2014-05-15T12:30" -e"2014-05-16T12:30" json
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)" -u ${un} -p ${paswd} -n10 -s"2014-05-15T12:30" -e"2014-05-16T12:30" geo
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)" -u ${un} -p ${paswd} -n10 -s"2014-05-15T12:30" -e"2014-05-16T12:30" wordcount
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)" -u ${un} -p ${paswd} -n10 -s"2014-05-15T12:30" -e"2014-05-16T12:30" users
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)" -u ${un} -p ${paswd} -s"2014-05-25T12:30" -e"2014-06-10T12:30" -aw json
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)" -u ${un} -p ${paswd} -s"2014-05-25T12:30" -e"2014-06-10T12:30" -aw geo
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)" -u ${un} -p ${paswd} -s"2014-05-25T12:30" -e"2014-06-10T12:30" -a users

export GNIP_CONFIG_FILE=./.gnip
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)"  -n10 -q json
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)"  -n10 json
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)"  -n10 geo
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)"  -n10 wordcount
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)"  -n10 timeline
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)"  -n10 users
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)"  -n10 -c geo
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)"  -n10 -c timeline 
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)"  -n10 -s"2014-05-15T12:30" -e"2014-05-16T12:30" json
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)"  -n10 -s"2014-05-15T12:30" -e"2014-05-16T12:30" geo
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)"  -n10 -s"2014-05-15T12:30" -e"2014-05-16T12:30" wordcount
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)"  -n10 -s"2014-05-15T12:30" -e"2014-05-16T12:30" users
./search_api.py -f"has:geo (stanleycup OR stanley cup) (kings OR rangers)"  -s"2014-05-25T12:30" -e"2014-06-10T12:30" -aw json

