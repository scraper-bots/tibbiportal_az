#!/bin/bash
# Cleanup script to remove progress CSV files and keep only the complete data

echo "Cleaning up progress files..."
rm -f doctors_data_progress_*.csv
rm -f doctors_data_interrupted.csv
rm -f doctors_data_error.csv

echo "✓ Progress files removed"
echo "Keeping only: doctors_data_complete.csv"

ls -lh doctors_data_complete.csv 2>/dev/null || echo "Note: doctors_data_complete.csv not found yet (scraper may still be running)"
