#!/bin/bash
set -e

# Clone repo (fresh)
git clone https://x-access-token:${GH_PAT}@github.com/aaronzr1/classdore-scraper.git repo
cd repo
git checkout data-pipeline

echo "Starting -d job..."
python scraper.py -d

# Commit and push
git add data/data.json
git commit -m "Automated -d output for $(date -u +"%Y-%m-%d %H:%M:%S UTC")" || echo "No changes to commit"
git push origin data-pipeline

echo "Running upload step..."
python upload_to_redis.py data/data.json --skip-unchanged

echo "All done!"