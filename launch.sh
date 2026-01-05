#!/bin/bash
clear

./process.py \
    --source data \
    --nth 30 \
    --workdir tmp \
    --result result.mp4
