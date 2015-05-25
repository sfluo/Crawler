#!/bin/sh

files=`ls *.json`
for jf in $files
do
	python -m json.tool $jf > "new_$jf"
	rm $jf
	mv "new_$jf" $jf
done



