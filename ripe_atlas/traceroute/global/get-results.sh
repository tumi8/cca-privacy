#!/bin/bash

if [[ ! -s $1 ]]; then echo "Please give new-line separated file with measurement IDs to download as argument!" ; exit 1 ; fi

for i in `cat $1`
do
	echo $i
	curl 'https://atlas.ripe.net/api/v2/measurements/'$i'/results?format=txt' -o result-$i.json
done
