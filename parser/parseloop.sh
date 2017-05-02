#!/bin/bash
MAX_PAR=10

DATADIR=$2
FILES=(${DATADIR}/result*.pcap*)
FILE_COUNTER=0
PROC_COUNTER=0

CMD="Parser.py"

function COUNT_RUNNING_PROC()
{
	read PROC_COUNTER <<< $(ps ax | grep "$CMD" | wc -l)
	((PROC_COUNTER--))
}

echo 
echo "Total number of files to process: ${#FILES[@]}"

while [ $FILE_COUNTER -lt ${#FILES[@]} ]; do 
	COUNT_RUNNING_PROC
	#echo "Current processes $PROC_COUNTER"
	if [ $PROC_COUNTER -lt $MAX_PAR ]; then
		echo "Processing file #$FILE_COUNTER: ${FILES[$FILE_COUNTER]}"
		#echo "Writing log to ${FILES[$FILE_COUNTER]}.log"
		echo "Running $CMD ${1} ${FILES[$FILE_COUNTER]} ${3} ${4}"
		$CMD ${1} ${FILES[$FILE_COUNTER]} ${3} ${4} 1> /dev/null 2> /dev/null &
		((FILE_COUNTER++))		
	else
		#echo "No CPU available, sleeping for 5s"		
		sleep 5 
	fi
done

echo "All ${#FILES[@]} files processing" 

COUNT_RUNNING_PROC;
while [ $PROC_COUNTER -gt 0 ];
do 	
	COUNT_RUNNING_PROC;
	echo "$PROC_COUNTER processes running" 
	sleep 1;
done


echo "All ${#FILES[@]} files finished processing"
