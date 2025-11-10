#!/bin/bash

# Database Reset Script (TEMPLATE - OPTIONAL)
# This script resets your database to a known state for testing/development.
#
# This is OPTIONAL. Only needed if your project uses a database.
# Remove this script if not applicable to your project.
#
# CUSTOMIZATION REQUIRED:
# 1. Update DB_BACKUP_PATH and DB_PATH for your database location
# 2. Adjust reset logic for your database type (SQLite, PostgreSQL, MySQL, etc.)
# 3. Add any necessary database connection parameters
#
# See store/CUSTOMIZATION_GUIDE.md for examples

# TODO: Customize these paths for your database
DB_BACKUP_PATH="db/backup.db"    # Path to backup database file
DB_PATH="db/database.db"          # Path to active database file

echo "Starting database reset..."

# For SQLite (file-based database)
echo "Copying $DB_BACKUP_PATH to $DB_PATH..."
mkdir -p "$(dirname "$DB_PATH")"
cp "$DB_BACKUP_PATH" "$DB_PATH"

if [ $? -eq 0 ]; then
    echo "✓ Database reset successfully completed"
else
    echo "✗ Error: Failed to reset database"
    exit 1
fi

# Alternative examples for other database types:
#
# PostgreSQL:
# psql -U username -d database_name < backup.sql
#
# MySQL:
# mysql -u username -p database_name < backup.sql
#
# MongoDB:
# mongorestore --db database_name backup/
#
# Docker-based database:
# docker-compose down -v && docker-compose up -d