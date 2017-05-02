# Documentation of traceroute measurements

In the *global* and *germany* subdirectories you will find code to execture and analyze traceroute measurements from distributed vantage points towards APNs server infrastructure. 

The documentation will cover *germany* in detail, and just list the commands for *global* as it follows the same logic.

The resulting files are available as results.tar.xz in each folder.

## Execute measurements

Measurements are exectued against the IP address previsouly found in the RIPE Atlas DNS scans.

For Germany, a subset that replied to responds from Germany is used, hence there is a slight difference:

For Germany, run `apns-measure-traceroute-ips-germany.sh`  
For global, run `apns-measure-traceroute-ips-global.sh ../apns-random-ips-per-subnet`  

## Download & merge measurement results

`cd germany && ./get-results.sh apns-traceroute-german-measure-ids.txt`
The Ripe Atlas json files miss a '\n' at the end of file, hence concatenating does not properly work. jq fixes this:  
`cd germany && cat result-*.json | jq -c . > all_results.json`  


## Process results
Expect 1 min on an average laptop (speed picks up over time due to IP mapping caching):  
`./traceroutes_to_asn_ixp.py germany/all_results.json ixp_subnets_v4.csv routeviews-rv2-20160926-1200.pfx2as > germany/all_results.json.resultlog` 

The resulting Top-10 table at the end of the "resultlog" file is then used in the paper.
Please note that AS-714 (Apple) is ignored in the result, as all traceroute targets lie in this AS. It is not present in 100% of traces due to occasional packet loss/unresponsiveness/other problems. 
Please also note that the % do not add up to 100% as on traceroute can traverse several ASes. However, the conclusion what percentage of traces as certain AS can eavesdrop on is valid.


## Calculcate AS and Country Coverage for Global Measurement

The script `./extract_PRBID_IP_CC_ASN_from_RAJSON.py` takes a RIPE Atlas traceroute json file and outputs IP address, CC, and ASN for all probe IDs. 

We apply it to the merged all_results.json for efficiency:  
`./extract_PRBID_IP_CC_ASN_from_RAJSON.py all_results.json`  
`Writing output from 1959 probes to: all_results.json.prbid_ip_cc_asn`

We then get the 115 countries and 1116 ASes:  
`cut -d, -f3 all_results.json.prbid_ip_cc_asn | tail -n+2  | sort -u | wc -l`  
`115`  
`cut -d, -f4 all_results.json.prbid_ip_cc_asn | tail -n+2  | sort -u | wc -l`  
`1115`  



### Documentation for Global Measurement

`cd global && ./get-results.sh apns-traceroute-global-measure-ids.txt`
`cd global && cat result-*.json | jq -c . > all_results.json`  
Expect about 15 min on average laptop (speedup over runtime due to ip mapping caching): 
`./traceroutes_to_asn_ixp.py global/all_results.json ixp_subnets_v4.csv routeviews-rv2-20160926-1200.pfx2as > global/all_results.json.resultlog`


## Credits:


We use the [Ripe Atlas Cousteau](https://github.com/RIPE-NCC/ripe-atlas-cousteau) toolchain, in combination with [traiXroute](https://github.com/gnomikos/traIXroute/tree/master/database) and [CAIDA's pfx2as mapping](http://www.caida.org/data/routing/routeviews-prefix2as.xml).