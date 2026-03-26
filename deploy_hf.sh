#!/bin/bash
# deploy_hf.sh — Déploiement automatique sur HF Spaces

set -e

BRANCH_SOURCE=${1:-develop}

# Sauvegarder le vrai fichier pkl AVANT de changer de branche
cp ml_model/model_pipeline.pkl /tmp/model_pipeline.pkl

echo "🚀 Déploiement HF depuis '$BRANCH_SOURCE'..."

git checkout --orphan hf-deploy
git rm -rf .

git checkout "$BRANCH_SOURCE" -- app/ gradio_demo/ ml_model/ database/ Dockerfile requirements.txt

# Restaurer le vrai fichier binaire (remplace le pointeur LFS)
cp /tmp/model_pipeline.pkl ml_model/model_pipeline.pkl

cat > README.md << 'EOF'
---
title: Futurisys Attrition
emoji: 📊
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---
EOF

# Déclarer le pkl comme fichier LFS pour HF
git lfs track "*.pkl"

git add .gitattributes app/ gradio_demo/ ml_model/ database/ Dockerfile requirements.txt README.md
git commit -m "deploy: $(date +%Y-%m-%d) from $BRANCH_SOURCE"
git push hf hf-deploy:main --force

git checkout "$BRANCH_SOURCE"
git branch -D hf-deploy

echo "✅ Déploiement terminé !"
echo "👉 https://huggingface.co/spaces/BarbaraDI/futurisys-attrition"