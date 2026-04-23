#!/bin/bash

# Phase 3 Frontend 完了版のコミットスクリプト

echo "🚀 Committing Phase 3 (Complete Frontend)..."

cd /home/yn441611/projects/orchestrix

# ファイルをステージング
git add frontend/

# ステータス確認
echo ""
echo "📋 Files to be committed:"
git status --short
echo ""

# コミット
echo "💾 Creating Phase 3 commit..."
git commit -m "feat: Phase 3 (Complete Frontend) - All pages, styling, and build config

Added missing pages:
- src/pages/Agents.tsx - Full agent management page
- src/pages/Analytics.tsx - Complete analytics dashboard
- src/pages/Settings.tsx - Comprehensive settings page

Added styling and configuration:
- src/index.css - Complete TailwindCSS custom styles
- tailwind.config.js - TailwindCSS configuration
- vite.config.ts - Vite build configuration

Total additions: ~800 lines across 5 new files"

echo ""
echo "✅ Commit created!"
echo ""

# プッシュ
if git remote get-url origin > /dev/null 2>&1; then
    echo "📤 Pushing to remote repository..."
    git push
    echo ""
    echo "🎉 Phase 3 complete! Orchestrix frontend is ready."
else
    echo "❌ No remote repository configured."
    echo "To push, run: git remote add origin <your-repo-url> && git push"
fi
