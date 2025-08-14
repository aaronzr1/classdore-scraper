#!/bin/bash
set -e

echo "Starting -d job..."
python scraper.py -d

# Push updated data.json back to data-pipeline branch
if [ -f "data/data.json" ]; then
    echo "Pushing updated data.json to GitHub..."

    git config --global user.name "railway-bot"
    git config --global user.email "railway-bot@example.com"

    # Use PAT from Railway env variable
    git remote set-url origin https://x-access-token:${GH_PAT}@github.com/aaronzr1/classdore-scraper.git

    git fetch origin
    git checkout data-pipeline

    git add data/data.json
    git commit -m "Automated -d output for $(date -u +"%Y-%m-%d %H:%M:%S UTC")" || echo "No changes to commit"
    git push origin data-pipeline

    echo "data.json pushed successfully!"
else
    echo "data.json not found; skipping push."
fi

echo "Running upload step..."
python upload_to_redis.py data/data.json --skip-unchanged

echo "All done!"