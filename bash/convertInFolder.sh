#!/bin/bash

eval "$(conda shell.bash hook)"
conda activate sleap

echo "sleap enabled"


for f in ../Bee_vids/2022_06_20_vids/*.slp; do
	echo $f
	echo "${f:0:-3}analysis.h5.h"
	sleap-convert --format analysis -o "${f:0:-3}analysis.h5.h" "$f"
done



