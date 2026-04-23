#!/bin/bash

# Phase 3 実装ファイルのコミットスクリプト

echo "🚀 Committing Phase 3 implementation..."

cd /home/yn441611/projects/orchestrix

# ファイルをステージング
git add frontend/
git add tests/unit/
git add src/scheduler/worker.py

# ステータス確認
echo ""
echo "📋 Files to be committed:"
git status --short
echo ""

# コミット
echo "💾 Creating Phase 3 commit..."
git commit -m "feat: Phase 3 - Frontend, Unit Tests, and Celery Worker

Implemented Frontend (Electron + React):
- React TypeScript application with React Router
- Zustand state management for global state
- TailwindCSS for styling with Lucide icons
- Dashboard page with statistics and recent executions
- Tasks page with CRUD operations and task execution
- Agents page for managing AI agent configurations
- Analytics page for execution history and performance metrics
- Settings page for configuration management
- Electron main process and build configuration
- Responsive design with mobile support

Implemented Unit Tests:
- test_complexity_analyzer.py: 100% coverage of complexity scoring
- test_task_decomposer.py: Task decomposition with DAG building
- Tests for simple, medium, and complex tasks
- Context and dependency handling tests
- Edge cases and boundary condition tests

Implemented Celery Worker:
- Async task execution with Celery
- Task execution orchestration
- Task scheduling with cron expressions
- Log analysis background jobs
- Health check endpoints
- Error handling and logging

Tech Stack:
- React 18 with TypeScript
- Zustand for state management
- React Router for navigation
- TailwindCSS for styling
- Electron for desktop application
- Celery for async task processing
- pytest for unit testing

Files added:
- frontend/package.json, tsconfig.json, electron-builder.json
- frontend/public/index.html
- frontend/src/App.tsx, index.tsx
- frontend/src/state/store.ts
- frontend/src/components/Layout.tsx
- frontend/src/pages/Dashboard.tsx, Tasks.tsx
- tests/unit/test_complexity_analyzer.py
- tests/unit/test_task_decomposer.py
- src/scheduler/worker.py

Total additions: ~1500 lines across 13 files
"

echo ""
echo "✅ Commit created!"
echo ""

# プッシュ
if git remote get-url origin > /dev/null 2>&1; then
    echo "📤 Pushing to remote repository..."
    git push
    echo ""
    echo "🎉 Phase 3 complete!"
else
    echo "❌ No remote repository configured."
    echo "To push, run: git remote add origin <your-repo-url> && git push"
fi
