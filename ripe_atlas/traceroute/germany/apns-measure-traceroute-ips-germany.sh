#!/bin/bash

# APNs server IPs when resolving from Germany
for i in "17.252.92.30" "17.252.28.16" "17.130.144.53"
do
	curl --dump-header - -H "Content-Type: application/json" -H "Accept: application/json" -X POST -d '{
 "definitions": [
  {
   "target": "'$i'",
   "af": 4,
   "timeout": 4000,
   "description": "APNS trrt ger run1 '$i'",
   "protocol": "TCP",
   "resolve_on_probe": false,
   "packets": 1,
   "size": 48,
   "first_hop": 3,
   "max_hops": 32,
   "port": 5233,
   "paris": 16,
   "destination_option_size": 0,
   "hop_by_hop_option_size": 0,
   "dont_fragment": false,
   "skip_dns_check": true,
   "type": "traceroute"
  }
 ],
 "probes": [
  {
   "tags": {
    "include": [],
    "exclude": []
   },
   "type": "country",
   "value": "DE",
   "requested": 1000
  }
 ],
 "is_oneoff": true,
 "bill_to": "REDACTED"
}' https://atlas.ripe.net/api/v2/measurements/?key=REDACTED
done
