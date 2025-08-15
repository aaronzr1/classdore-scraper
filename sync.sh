git fetch origin
git checkout -B data-pipeline origin/data-pipeline
git merge origin/main --allow-unrelated-histories --no-edit || echo "No changes to merge"
git push origin data-pipeline
git checkout main