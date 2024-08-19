#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Please specify the new version as an argument."
    echo "Usage: $0 <new_version>"
    exit 1
fi

NEW_VERSION=$1
FILE_NAME="src/edm_su_api/__init__.py"

if [ ! -f "$FILE_NAME" ]; then
    echo "File $FILE_NAME not found."
    exit 1
fi

# Create a temporary file
TMP_FILE=$(mktemp)

# Perform the replacement in the temporary file
sed "s/__version__ = \".*\"/__version__ = \"$NEW_VERSION\"/" "$FILE_NAME" > "$TMP_FILE"

# Check if the replacement was successful
if [ $? -eq 0 ]; then
    # Replace the original file with the temporary one
    mv "$TMP_FILE" "$FILE_NAME"
    echo "Version successfully updated to $NEW_VERSION in file $FILE_NAME"
else
    echo "An error occurred while updating the version."
    rm "$TMP_FILE"
    exit 1
fi

