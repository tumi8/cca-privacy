#!/bin/bash
# replace REDACTED with valid API KEY before use
for i in `seq 1 50`
do
curl --dump-header - -H "Content-Type: application/json" -H "Accept: application/json" -X POST -d '{
 "definitions": [
  {
   "af": 4,
   "query_class": "IN",
   "query_type": "A",
   "query_argument": "'$i'-courier.push.apple.com",
   "description": "apple-push-fin",
   "use_probe_resolver": true,
   "resolve_on_probe": true,
   "set_nsid_bit": false,
   "protocol": "UDP",
   "udp_payload_size": 512,
   "retry": 0,
   "skip_dns_check": false,
   "include_qbuf": false,
   "include_abuf": true,
   "prepend_probe_id": false,
   "set_rd_bit": false,
   "set_do_bit": false,
   "set_cd_bit": false,
   "type": "dns"
  }
 ],
 "probes": [
  {
   "tags": {
    "include": [],
    "exclude": []
   },
   "type": "area",
   "value": "WW",
   "requested": 1000
  }
 ],
 "is_oneoff": true,
 "bill_to": "REDACTED"
}' https://atlas.ripe.net/api/v2/measurements/?key=REDACTED
done
