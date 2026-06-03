---
title: 概要
nav_order: 1
---

# Orchestrix

> 📂 **[GitHub リポジトリ →](https://github.com/fukukei23/orchestrix)**{: .btn .btn-blue } — ソースコード・API詳細はこちらから

**24時間自動実行可能なマルチAIエージェントオーケストレーションシステム。**

Claude Code、GLM、MiniMax、Kimi、Gemini、Codex を統一APIで制御し、複雑度に応じた自動タスク分配を行う。

## 対応AIエージェント

| エージェント | 特徴 | 主な用途 |
|-----------|------|---------|
| **Claude Code** | 高品質・ファイル編集・Bash実行 | 重要プロジェクト |
| **GLM (智谱AI)** | 超高速・超安価・中国語対応 | 日常開発 |
| **MiniMax** | 最安価・高速応答 | テスト・検証 |
| **Kimi (Moonshot)** | 8kコンテキスト | 長いコード解析 |
| **Gemini CLI** | マルチモーダル対応 | 画像含むタスク |
| **Codex CLI** | GPT-4ベース | レガシーコード対応 |

## アーキテクチャ

```
Frontend(React+Electron) → FastAPI(REST) → PostgreSQL + Redis/Celery → LLM Layer
                               /api/v1/tasks
                               /api/v1/agents
                               /api/v1/analytics
```

## 技術スタック

| カテゴリ | 技術 |
|---|---|
| API | FastAPI |
| データベース | PostgreSQL (SQLAlchemy) |
| タスクキュー | Redis + Celery |
| フロントエンド | React + Electron |
| テスト | pytest (194 tests, 81% coverage) |

---

> 👉 各機能の詳細はサイドバーの **機能ショーケース** をご覧ください。
