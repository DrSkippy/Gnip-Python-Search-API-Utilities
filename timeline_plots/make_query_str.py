#!/usr/bin/env python
import sys
import csv
#
# three args: query, name, search type
print "#!/usr/bin/env bash"
vargs = sys.argv[1:]
STR = '../gnip_search.py {} -w"./data" -f"{}" -s{} -e{} -n500 json | jq ".body" | term_frequency.py -w -n20 > ./examples/{}_{}_freq.csv'
# search  type, query, start date, end date, query, index
#ignore = False
state = 1
i = 0
for d in csv.reader(sys.stdin):
    v = float(d[2])
    if d[3] == "2_peaks":
        # alternating rows, so keep track of start date and state
        if int(v) > 0 and state == 1:
            i += 1
            state = 2
            arg_tuple = [vargs[2], vargs[0], d[0], vargs[1], i]
        elif int(v) == 0 and state == 2:
            # ok, have second half, so splice in the end date
            arg_tuple = arg_tuple[:3] + [d[0]] + arg_tuple[3:]
            print STR.format(*arg_tuple)
            state = 1
