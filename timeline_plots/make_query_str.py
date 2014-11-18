#!/usr/bin/env python
import sys
import csv
#
# two args: query, name
print "#!/usr/bin/env bash"
vargs = sys.argv[1:]
STR = 'search_api.py -f"{}" -s{} -n500 json | jq ".body" | term_frequency.py -w -n20 > ./examples/{}_{}_freq.csv &'
ignore = False
i = 0
for d in csv.reader(sys.stdin):
    v = float(d[1])
    if int(v) > 0 and not ignore:
        i += 1
        ignore = True
        print STR.format(vargs[0], d[0], vargs[1], i)
    else:
        ignore = False
    
