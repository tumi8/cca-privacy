# DNS Resolution Documentation

The aim of these scripts is to globally resolve the APNs DNS names using Ripe Atlas, and then to select one random target IP address per subnet.

## Create Measurement

The measurements are created by running `atlas-measure.sh`. Please insert your API Key before usage.

These resulting IDs can be manuelly inspected, for example under this link:
[https://atlas.ripe.net/measurements/5500065/](https://atlas.ripe.net/measurements/5500065/)

All resulting Ripe Atlas IDs are stored in the file `apns-dns-measure-ids.txt`.

## Download Measurement Results

*Please note that the results from the download and parse measurement results steps are contained in ripe-atlas-dns-responses.tar.bz2 as well*

The publicly available measurement results are then downloaded using `./get-results.sh apns-dns-measure-ids.txt`.

You can check that all files are correct by running `sha512sum -c dns-results-json.sha512`.

## Parse Measurement Results

The measurement results are json-encoded and need some processing into plain-text for our purposes. This is done using  
`for i in result-55000*json ; do ./parse-results.py $i > $i.parsed.txt; done`

This uses the [Ripe Atlas Cousteau](https://github.com/RIPE-NCC/ripe-atlas-cousteau) toolchain.

## Extract IP addresses

From here, we filtered the resulting files `*parsed.txt`for `IN A` records, converted all results to lowercase, and extracted unique IP addresses left. 
From these unique IP addresses, we selected one random IP address per /24 subnet.

## Final Result

The final IP addresses can be found in the file `random-ips-per-subnet.txt`.
Please note that precisely reproducing this is difficult as we have used local true randomness instead of a seeded PRNG. 
However, you can validate that every /24 is present with one valid IP address.


