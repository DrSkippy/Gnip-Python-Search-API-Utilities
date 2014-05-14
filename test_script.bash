#!/usr/bin/env bash

###
### edit creds
###

mkdir data
cat rules.txt | ./paged_search_api.py -u<email> -p<console_password> -d201405040000 -t201405050000 -f
