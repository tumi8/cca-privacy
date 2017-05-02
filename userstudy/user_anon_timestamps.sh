#!/bin/bash

RANDOM=`date +%N` # seeds the PRNG
fixed_rand=$RANDOM
for i in *ts*
do
    ./user_anon_timestamp.py $i $fixed_rand > $i.anon
done
