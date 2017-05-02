#!/bin/bash
# NOTE: We anonymize MAC and IP addresses of the original .pcap files with the command below.
# You can obtain the original pcap files from us in case you need to.
# tcpreplay version: 4.2.2 (build git:v4.2.2)
mkdir -p rewritten/
for i in *pcapng
do
    RANDOM=`date +%N` # seeds the PRNG
    echo $RANDOM
    outfile=`echo ${i##*:}_rewritten.pcapng`
    echo $i $outfile
    # this does (a) unify the enet type to ethernet and (b) replaces MAC and IP addresses
    tcprewrite --dlt=enet --enet-dmac=01:02:03:04:05:06,06:05:04:03:02:01 \
    --enet-smac=06:05:04:03:02:01,01:02:03:04:05:06 --seed=$RANDOM -i $i -o rewritten/${i}_rewritten.pcapng
    #tcprewrite -i $i -o rewritten/$outfile --enet-mac-seed=$RANDOM --seed=$RANDOM
done
