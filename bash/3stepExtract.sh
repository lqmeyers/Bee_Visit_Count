#!/bin/bash
set -x

eval "$(conda shell.bash hook)"
conda activate sleap
echo 'sleap enabled'


for f in ../Bee_vids/2022_06_20_vids/f6.*; do
	echo $f
	sleap-track $f \
		-m ../models/221122_135029.centroid.n=198 \
		-m ../models/221122_135029.centroid.n=198/221122_135029.centered_instance \
		--tracking.tracker simple \ 
done
echo 'tracked'

for f in ../Bee_vids/2022_06_20_vids/f6.*.slp; do
	echo $f
        echo "${f:0:-3}analysis.h5.h"
        sleap-convert --format analysis -o "${f:0:-3}analysis.h5.h" "$f"
done
echo 'converted'


for f in ../Bee_vid/2022_06_20_vids/f6.*.h; do
	echo $f
	python /mnt/c/Users/lqmey/OneDrive/Desktop/Bee_Visit_Count/photoExtract.py "$f" "${f:0:47}"
done 
echo 'saved' 
