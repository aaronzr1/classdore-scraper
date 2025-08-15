#!/bin/bash
set -e

# Clone repo (fresh if needed)
if [ -d "repo" ]; then
    cd repo
    git checkout data-pipeline
    git pull origin data-pipeline
else
    git clone https://x-access-token:${GH_PAT}@github.com/aaronzr1/classdore-scraper.git repo
    cd repo
    git checkout data-pipeline
fi

last_commit_msg=$(git log -1 --pretty=%B)
last_commit_author_email=$(git log -1 --pretty=%ae)

if [[ "$last_commit_msg" == Automated\ -l\ output* ]] && \
   [[ "$last_commit_author_email" == "actions@github.com" ]]; then
    echo "Running -d job..."
else
    echo "Skipping -d job because last commit was not from a GitHub Actions -l run."
    exit 0
fi

# Set git identity
git config user.name "Railway CI"
git config user.email "ci@railway.app"

# if [ -f "UPLOAD_ONLY" ]; then
#     echo "UPLOAD_ONLY file found. Skipping -d job..."
# else
#     echo "Starting -d job..."
#     python scraper.py -d
# fi

# Commit and push
git add data/data.json
git commit -m "Automated -d output for $(date -u +"%Y-%m-%d %H:%M:%S UTC")" || echo "No changes to commit"
git push origin data-pipeline


echo "Running upload step..."
python upload_to_redis.py data/data.json --skip-unchanged

echo "All done!"