#!/bin/bash

RANDOM=`date +%N` # seeds the PRNG with nanoseconds part of timestamp
fixed_rand=$RANDOM
for i in *.ts *ts.daytime
do
    if [[ -s $i ]] # check that file actually exists
    then
      ./user_anon_timestamp.py $i $fixed_rand > $i.anon
    fi
done
