#!/usr/bin/env python3

# this script anonymizes timestamp for the valid from dataset by replacing a pattern like
# Oct 28 02:45:23 2015 GMT
# by something like (Day of month set to 1, time set to fixed string)
# Oct 1 12:34:56 2015 GMT

import sys, re
regex = re.compile("^([a-zA-Z]{3})\s+[0-9]+\s+[0-9:]+\s([0-9]{4})\s+")
with open(sys.argv[1]) as f:
    for line in f:
        line = line.strip()
        result = regex.search(line)
        if not result:
            print("Critical: no match found in line {}".format(line))
        else:
            print("{} 1 12:34:56 {} GMT".format(result.group(1), result.group(2)))
            #print("From {} to {} 1 12:34:56 {} GMT".format(line, result.group(1), result.group(2)))
            #print("{} 1 12:34:56 {} GMT".format(result.group(1), result.group(2)))