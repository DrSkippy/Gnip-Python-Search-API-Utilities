#!/usr/bin/env python
import sys
import csv
#
# two args: query, name
print "#!/usr/bin/env bash"
vargs = sys.argv[1:]
STR = '../search_api.py -f"{}" -s{} -e{} -n500 json | jq ".body" | term_frequency.py -w -n20 > ./examples/{}_{}_freq.csv'
#ignore = False
state = 1
i = 0
for d in csv.reader(sys.stdin):
    v = float(d[2])
    if d[3] == "2_peaks":
        if int(v) > 0 and state == 1:
            i += 1
            state = 2
            arg_tuple = [vargs[0], d[0], vargs[1], i]
        elif int(v) == 0 and state == 2:
            arg_tuple = arg_tuple[:2] + [d[0]] + arg_tuple[2:]
            print STR.format(*arg_tuple)
            state = 1
