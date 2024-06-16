#!/bin/zsh

# Path to the file
filepath="/Users/xhulioskenderi/Desktop/CryptoP/openai-quickstart-python/scrapper/config_file.txt"

# Check if file exists
if [[ -f $filepath ]]; then
    # Get the file's age in days
    file_age=$(($(date +%s) - $(date -r "$filepath" +%s) / 86400))

    # Check if the file is older than 31 days
    if (( file_age > 31 )); then
        echo "Deleting file $filepath which is $file_age days old."
        rm $filepath
    else
        echo "File $filepath is $file_age days old, not older than 31 days, not deleting."
    fi
else
    echo "File $filepath does not exist."
fi

