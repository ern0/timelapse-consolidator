#!/bin/bash
clear

rm -f video.mp4

./process.py \
    --source data \
    --nth 30 \
    --workdir tmp \
    --result video.mp4

