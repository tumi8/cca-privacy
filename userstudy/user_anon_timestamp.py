#!/usr/bin/env python3

# this script anonymizes timestamp for the valid from dataset by replacing the day in a pattern like
# 587,13,03 (Day of year, hour, minute)
# by day + random offset (sys.argv[2])

import sys, re
regex = re.compile("^(\d+),(\d+),(\d+)")
offset = int(sys.argv[2]) % 65536
# sys.stderr.write("Using offset of {}\n".format(offset))  # do not document offset for published version
with open(sys.argv[1]) as f:
    for line in f:
        line = line.strip()
        result = regex.search(line)
        if not result:
            print("Critical: no match found in line {}".format(line))
        else:
            print("{},{},{}".format(int(result.group(1)) + offset, result.group(2), result.group(3)))