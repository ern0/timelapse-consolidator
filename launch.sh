#!/bin/bash
clear

IMAGE_DIR=result

true ./extract_iframes_from_mp4.py \
    -n 200 \
    data/20210203AM/Csoka7-20210203-051151-1612325511.mp4 \
    $IMAGE_DIR

true ./delete_dark_images.py $IMAGE_DIR

./collect_selected_images.py \
    --fps 25 \
    $IMAGE_DIR \
    result.mp4
