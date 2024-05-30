#!/usr/bin/bash

echo ">>> Convolyzer <<<"

# Settings

date_to_use=$(date +%Y%m%d)
log_directory=logs
log_filename=${log_directory}/log_${date_to_use}.txt

# Create logs directory
mkdir $log_directory

echo "Use log file: $log_filename"

# Run the bot and redirect output
python main.py >> $log_filename 2>&1