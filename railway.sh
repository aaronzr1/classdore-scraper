#!/bin/bash
set -e

echo "Starting -d job..."
python main.py -d

echo "Running upload step..."
python upload.py

echo "All done!"