#!/bin/bash

# Restore files from organized folders to original locations using a log file
# Usage: ./restore_files.sh [path_to_log_file]

LOG_FILE="${1:-}"

if [ -z "$LOG_FILE" ]; then
    echo "Usage: $0 <log_file>"
    echo "Example: $0 organize_log_20260718_193926.txt"
    exit 1
fi

if [ ! -f "$LOG_FILE" ]; then
    echo "Error: Log file not found at $LOG_FILE"
    exit 1
fi

echo "Restoring files using log: $LOG_FILE"

# Read each line and move files back
while IFS= read -r line; do
    # Skip comment lines or empty lines
    [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
    
    # Parse the source and destination
    pattern='^(.+) +-> +(.+)$'
    if [[ "$line" =~ $pattern ]]; then
        source="${BASH_REMATCH[1]}"
        destination="${BASH_REMATCH[2]}"
        
        # Extract just the filename from destination path
        filename=$(basename "$destination")
        
        # Create source directory if it doesn't exist
        mkdir -p "$(dirname "$source")"
        
        # Move file back to original location
        if [ -f "$destination" ]; then
            mv "$destination" "$source"
            echo "Restored: $filename -> $source"
        else
            echo "Warning: $destination not found, skipping"
        fi
    fi
done < "$LOG_FILE"

echo "Restoration complete!"
