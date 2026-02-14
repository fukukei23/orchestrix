#!/bin/bash

# Git setup and commit script for Orchestrix project

echo "🚀 Setting up Git repository..."

cd /home/yn441611/projects/orchestrix

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git branch -M main
else
    echo "✅ Git repository already initialized"
fi

# Configure git if needed
echo "🔧 Configuring git..."
git config user.name "Orchestrix Developer"
git config user.email "dev@orchestrix.ai"

# Add all files
echo "📝 Adding all files to git..."
git add .

# Check what will be committed
echo ""
echo "📋 Files to be committed:"
git status --short
echo ""

# Commit
echo "💾 Creating initial commit..."
git commit -m "feat: Initial commit - Orchestrix AI Agent Orchestration Matrix

- Project structure with core modules
- Phase 1 implementation:
  - complexity_analyzer.py: Task complexity scoring (0.0-1.0)
  - task_decomposer.py: Automatic task decomposition
  - cli_wrapper.py: Generic CLI wrapper for AI agents
  - agent_allocator.py: Intelligent agent allocation
  - master_orchestrator.py: Main orchestration logic
- Database models: Task, TaskDependency, Execution, Log, AgentConfig
- Docker setup: PostgreSQL 15 + Redis 7
- Configuration: requirements.txt, pytest.ini, docker-compose.yml
- Environment setup: .env template
- Documentation: README.md

Tech Stack:
- Backend: FastAPI + Celery + Redis + PostgreSQL
- LLM Strategy: GLM-4.7/Haiku/Sonnet 4.5 based on complexity
- Features: Git Worktree, DAG-based task scheduling, Analytics"

echo ""
echo "✅ Commit created!"
echo ""
echo "📊 Commit details:"
git log -1 --stat
echo ""

# Check if remote exists
if git remote get-url origin > /dev/null 2>&1; then
    echo "🔗 Remote repository already configured:"
    git remote -v
    echo ""
    echo "📤 Pushing to remote repository..."
    git push -u origin main
else
    echo "❌ No remote repository configured."
    echo ""
    echo "To add a remote repository, run:"
    echo "  git remote add origin <your-repository-url>"
    echo "  git push -u origin main"
fi

echo ""
echo "🎉 Setup complete! You can now continue on the web."
