#!/bin/bash

# Phase 2 実装ファイルのコミットスクリプト

echo "🚀 Committing Phase 2 implementation..."

cd /home/yn441611/projects/orchestrix

# ファイルをステージング
git add src/core/collaboration/
git add src/scheduler/
git add src/analytics/
git add src/api/

# ステータス確認
echo ""
echo "📋 Files to be committed:"
git status --short
echo ""

# コミット
echo "💾 Creating Phase 2 commit..."
git commit -m "feat: Phase 2 - Collaboration patterns, Scheduler, Analytics, and FastAPI

Implemented core collaboration patterns:
- Pipeline: Sequential agent collaboration (A→B→C)
- Parallel: Multi-agent parallel execution with best selection
- Fallback: Automatic agent switching on failure

Implemented task scheduler:
- Celery Beat integration for scheduled tasks
- Natural language to cron expression parsing
- Task validation and next run time calculation

Implemented log analytics:
- Execution history analysis (success rate, cost, performance)
- Agent and model performance tracking
- Error pattern detection and clustering
- Trend analysis and recommendations

Implemented FastAPI endpoints:
- Tasks API: CRUD operations, execution history
- Agents API: List, details, toggle, cost estimation
- Analytics API: Summary, performance, error analysis, trends

Tech Stack:
- FastAPI for REST API
- Celery Beat for scheduling
- pandas & scikit-learn for analytics
- YAML-based agent configuration

Files added:
- src/core/collaboration/pipeline.py
- src/core/collaboration/parallel.py
- src/core/collaboration/fallback.py
- src/scheduler/task_scheduler.py
- src/analytics/log_analyzer.py
- src/api/main.py
- src/api/dependencies.py
- src/api/routes/tasks.py
- src/api/routes/agents.py
- src/api/routes/analytics.py
"

echo ""
echo "✅ Commit created!"
echo ""

# プッシュ
if git remote get-url origin > /dev/null 2>&1; then
    echo "📤 Pushing to remote repository..."
    git push
    echo ""
    echo "🎉 Phase 2 complete!"
else
    echo "❌ No remote repository configured."
    echo "To push, run: git remote add origin <your-repo-url> && git push"
fi
