#!/bin/bash

for i in *ipynb
do
    jupyter nbconvert --to html  $i
done
