#!/bin/bash
set -e

echo "Starting -d job..."
python main.py -d

echo "Running upload step..."
python upload_to_redis.py

echo "All done!"