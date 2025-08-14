#!/bin/bash
set -e

echo "Starting -d job..."
python scraper.py -d

# Commit and push changes
echo "Pushing updated data.json to GitHub..."
git config --global user.name "railway-bot"
git config --global user.email "railway-bot@example.com"

# Use token to authenticate
git remote set-url origin https://x-access-token:${GH_PAT}@github.com/aaronzr1/classdore-scraper.git

git add data/data.json
git commit -m "Automated -d output for $(date -u +"%Y-%m-%d %H:%M:%S UTC")" || echo "No changes to commit"
git push

echo "Running upload step..."
python upload_to_redis.py data/data.json --skip-unchanged

echo "All done!"