#!/bin/bash

# ETL Pipeline Cron Setup Script
# This script helps configure the ETL pipeline to run automatically via cron

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_PATH="/usr/bin/python3"
CRON_FILE="$PROJECT_ROOT/config/crontab.etl"

echo "=== ETL Pipeline Cron Setup ==="
echo "Project root: $PROJECT_ROOT"
echo ""

# Check if Python is available
if ! command -v $PYTHON_PATH &> /dev/null; then
    echo "Error: Python not found at $PYTHON_PATH"
    echo "Please update PYTHON_PATH in this script"
    exit 1
fi

echo "Python found at: $PYTHON_PATH"
echo ""

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/logs"
echo "Created logs directory"

# Test the ETL pipeline
echo ""
echo "Testing ETL pipeline..."
cd "$PROJECT_ROOT"
$PYTHON_PATH scripts/run_etl_pipeline.py --test

if [ $? -eq 0 ]; then
    echo "ETL pipeline test successful"
else
    echo "Warning: ETL pipeline test failed"
    echo "Please check the pipeline configuration before setting up cron"
fi

# Ask user which schedule they want
echo ""
echo "Select cron schedule:"
echo "1) Daily at 5:00 AM UTC"
echo "2) Every 6 hours"
echo "3) Weekdays at 9:00 AM EST (14:00 UTC)"
echo "4) Custom schedule"
echo "5) Exit without setting up cron"

read -p "Enter choice (1-5): " choice

case $choice in
    1)
        CRON_LINE="0 5 * * * cd $PROJECT_ROOT && $PYTHON_PATH scripts/run_etl_pipeline.py >> logs/cron_output.log 2>&1"
        ;;
    2)
        CRON_LINE="0 */6 * * * cd $PROJECT_ROOT && $PYTHON_PATH scripts/run_etl_pipeline.py >> logs/cron_output.log 2>&1"
        ;;
    3)
        CRON_LINE="0 14 * * 1-5 cd $PROJECT_ROOT && $PYTHON_PATH scripts/run_etl_pipeline.py >> logs/cron_output.log 2>&1"
        ;;
    4)
        echo "Enter custom cron schedule (e.g., '0 5 * * *'):"
        read CUSTOM_SCHEDULE
        CRON_LINE="$CUSTOM_SCHEDULE cd $PROJECT_ROOT && $PYTHON_PATH scripts/run_etl_pipeline.py >> logs/cron_output.log 2>&1"
        ;;
    5)
        echo "Exiting without setting up cron"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "Adding to crontab:"
echo "$CRON_LINE"

# Add to crontab
(crontab -l 2>/dev/null | grep -v "run_etl_pipeline.py"; echo "$CRON_LINE") | crontab -

echo ""
echo "✓ Cron job added successfully"
echo ""
echo "To view your crontab: crontab -l"
echo "To edit your crontab: crontab -e"
echo "To remove the cron job: crontab -e and delete the line"
echo ""
echo "Logs will be saved to: $PROJECT_ROOT/logs/cron_output.log"
