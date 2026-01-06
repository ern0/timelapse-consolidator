@echo off
cls

del /q video.mp4 2>nul

python process.py ^
    --source data ^
    --nth 30 ^
    --workdir tmp ^
    --result video.mp4
