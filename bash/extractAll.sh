#!/bin/bash
#set -x

eval "$(conda shell.bash hook)"
conda activate sleap
echo 'sleap enabled'


for f in ../Bee_vids/2022_06_22_vids/f3.*.mp4; do
	echo "$f"
	sleap-track $f \
		-m ../models/221122_135029.centroid.n=198 \
		-m ../models/221122_135029.centroid.n=198/221122_135029.centered_instance \
		--tracking.tracker simple \ 
	sleap-convert --format analysis -o "${f:0:${#f}}.predictions.analysis.h5.h" "$f.predictions.slp"
	python /mnt/c/Users/lqmey/OneDrive/Desktop/Bee_Visit_Count/photoExtract.py "$f.predictions.analysis.h5.h" "$f"
done

