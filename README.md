# Orchestrix - AI Agent Orchestration Matrix

## 概要
Orchestrixは、複数のAIエージェントを統括し、24時間自動実行可能なオーケストレーションシステムです。

## 対応 AI エージェント

Orchestrix は以下の AI エージェントをサポートしています：

| エージェント | 特徴 | 主な用途 |
|-----------|------|---------|
| **Claude Code** | 高品質なコード生成、ファイル編集、Bash 実行 | 重要プロジェクト、複雑な実装 |
| **GLM (智谱AI)** | 超高速・超安価、中国語対応 | 日常開発、プロトタイピング |
| **MiniMax** | 最安価、高速な応答 | テスト・検証、小規模タスク |
| **Kimi (Moonshot AI)** | 8k コンテキスト、安価 | 長いコード解析、ドキュメント生成 |
| **Gemini CLI** | マルチモーダル（画像対応） | 画像を含むタスク |
| **Codex CLI** | GPT-4 ベース | レガシーコード対応 |

📖 **詳細な比較は [docs/AGENTS_COMPARISON.md](docs/AGENTS_COMPARISON.md) を参照**

## セットアップ

### 1. Python環境のセットアップ
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Dockerコンテナの起動
```bash
docker-compose up -d
```

### 3. データベースの初期化
```bash
# Alembicの初期化（まだの場合）
alembic init alembic

# マイグレーションの作成と適用
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 4. 環境変数の設定
`.env`ファイルに API キーを設定してください：

```bash
# Anthropic (Claude Code)
ANTHROPIC_API_KEY=sk-ant-xxx...

# OpenAI (GPT-4o)
OPENAI_API_KEY=sk-proj-xxx...

# GLM (智谱AI)
GLM_API_KEY=xxx...

# MiniMax
MINIMAX_API_KEY=xxx...

# Kimi (Moonshot AI)
KIMI_API_KEY=sk-xxx...

# Google Gemini
GOOGLE_API_KEY=xxx...
```

## テストの実行
```bash
pytest tests/unit/
```

## 次のステップ
Phase 1のコアモジュールを実装します。
