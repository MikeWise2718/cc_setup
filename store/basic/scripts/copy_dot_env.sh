#!/bin/bash

# Environment File Copy Script (TEMPLATE)
# This script copies .env files from a source location to your project.
#
# CUSTOMIZATION REQUIRED:
# 1. Update SOURCE_DIR to point to your .env source location
# 2. Update destination paths to match your project structure
# 3. Adjust file checks based on your environment file needs
# 4. Remove this script if you don't use .env files
#
# See store/CUSTOMIZATION_GUIDE.md for more details

# TODO: Customize these paths for your project
SOURCE_DIR="../your-env-source"  # Replace with your source directory
BACKEND_ENV_PATH="backend/.env"   # Replace with your backend .env path (or remove if not needed)

# Check and copy root .env file
if [ -f "$SOURCE_DIR/.env" ]; then
    cp "$SOURCE_DIR/.env" .env
    echo "Successfully copied $SOURCE_DIR/.env to .env"
else
    echo "Warning: $SOURCE_DIR/.env does not exist"
fi

# Check and copy backend .env file (customize or remove if not needed)
if [ -f "$SOURCE_DIR/$BACKEND_ENV_PATH" ]; then
    mkdir -p "$(dirname "$BACKEND_ENV_PATH")"
    cp "$SOURCE_DIR/$BACKEND_ENV_PATH" "$BACKEND_ENV_PATH"
    echo "Successfully copied $SOURCE_DIR/$BACKEND_ENV_PATH to $BACKEND_ENV_PATH"
else
    echo "Warning: $SOURCE_DIR/$BACKEND_ENV_PATH does not exist"
    # Note: Changed to warning instead of error - adjust based on your needs
fi

echo "Environment file copy complete. Review and customize paths in this script."