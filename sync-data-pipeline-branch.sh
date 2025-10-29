git fetch origin
git checkout -B data-pipeline origin/data-pipeline

# Pull the latest from main, but skip overwriting data/
git checkout origin/main -- . ':!data/'


# Commit only if there are changes
if ! git diff --cached --quiet; then
    git commit -am "Sync main into data-pipeline (preserving data/)"
    git push origin data-pipeline
else
    echo "No changes to merge"
fi

git checkout main