#!/bin/bash

rm ../Bee_imgs/f6.2*

for f in ../Bee_vids/2022_06_20_vids/f6.*.h; do
        echo "$f"
	echo "${f:0:47}"
        python /mnt/c/Users/lqmey/OneDrive/Desktop/Bee_Visit_Count/photoExtract.py "$f" "${f:0:47}"
done
echo 'saved'
