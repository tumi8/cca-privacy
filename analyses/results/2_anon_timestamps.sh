#!/bin/bash

for i in 2_*csv
do
    ./2_anon_timestamp.py $i > $i.anon
done
