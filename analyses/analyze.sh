#!/bin/bash

DB="/data/apple-push/pcap-ap3-ap4/db/pcap-ap3-ap4.db"
DATE=$(eval date +%Y-%m-%d_%k-%M-%S)
#DIR="results/results_$DATE"
DIR="results/results"

chmod u+x scripts/*.sh
echo Running analysis $DATE
mkdir -p $DIR

#SCRIPTS=(0_count_certificates.sh 0_count_apple_certificates.sh 0_count_apple_certificates_desktop.sh 0_count_apple_certificates_mobile.sh 0_cert_issuer.sh)
FILES=scripts/*
for SCRIPT in $FILES
do
  CMD="$SCRIPT"
  echo Running $CMD
  eval $CMD $DB $DIR
  echo ""
done
