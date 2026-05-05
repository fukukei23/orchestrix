# Orchestrix - AI Agent Orchestration Matrix

<!-- English: A multi-AI-agent orchestration system that coordinates Claude Code, GLM, MiniMax, Kimi, Gemini, and Codex through a unified API with 24/7 automated task execution. Built with FastAPI, PostgreSQL, Redis, and Celery for production-grade reliability. -->

複数のAIエージェントを統括し、24時間自動実行可能なオーケストレーションシステム。

---

## 対応 AI エージェント

| エージェント | 特徴 | 主な用途 |
|-----------|------|---------|
| **Claude Code** | 高品質なコード生成、ファイル編集、Bash実行 | 重要プロジェクト、複雑な実装 |
| **GLM (智谱AI)** | 超高速・超安価、中国語対応 | 日常開発、プロトタイピング |
| **MiniMax** | 最安価、高速な応答 | テスト・検証、小規模タスク |
| **Kimi (Moonshot AI)** | 8k コンテキスト、安価 | 長いコード解析、ドキュメント生成 |
| **Gemini CLI** | マルチモーダル（画像対応） | 画像を含むタスク |
| **Codex CLI** | GPT-4 ベース | レガシーコード対応 |

> 詳細な比較は [docs/AGENTS_COMPARISON.md](docs/AGENTS_COMPARISON.md) を参照

---

## アーキテクチャ

```
                    ┌─────────────────────────────────────┐
                    │        Frontend (React + Electron)    │
                    │   Zustand / Tailwind / Lucide Icons   │
                    └────────────────┬────────────────────┘
                                     │ HTTP (axios)
                    ┌────────────────▼────────────────────┐
                    │         FastAPI (REST API)            │
                    │   /api/v1/tasks                       │
                    │   /api/v1/agents                      │
                    │   /api/v1/analytics                   │
                    │   /api/v1/executions                  │
                    │   /api/v1/auth                        │
                    └────────┬───────────────┬────────────┘
                             │               │
                ┌────────────▼──┐     ┌──────▼──────────┐
                │  PostgreSQL   │     │     Redis        │
                │  (SQLAlchemy) │     │  (Celery Broker) │
                └───────────────┘     └──────┬──────────┘
                                             │
                                    ┌────────▼──────────┐
                                    │  Celery Worker     │
                                    │  (非同期タスク実行) │
                                    └────────┬──────────┘
                                             │
                    ┌────────────────────────▼────────────────────┐
                    │               LLM Layer                      │
                    │  Claude / GLM / MiniMax / Kimi / Gemini / GPT │
                    └─────────────────────────────────────────────┘
```

### モジュール構成

```text
src/
  api/            # FastAPIエンドポイント（routes, dependencies）
  agents/         # エージェント固有ロジック（CLIラッパー）
  auth/           # JWT認証
  core/           # オーケストレーションコア
    task_decomposer.py      # タスク分解
    complexity_analyzer.py  # 複雑度分析
    agent_allocator.py      # エージェント割り当て
    master_orchestrator.py  # 全体制御
    collaboration/          # エージェント間連携
  database/       # SQLAlchemyモデル・接続管理
  llm/            # LLMクライアント（Claude / OpenAI）
    llm_factory.py           # ファクトリ
    claude_client.py         # Anthropic SDK
    openai_client.py         # OpenAI SDK
  scheduler/      # Celeryタスク定義
  security/       # レート制限（slowapi）
  analytics/      # 分析・統計

frontend/         # React + Vite + Electron
  src/            # UIコンポーネント
  electron.js     # デスクトップアプリラッパー
```

---

## 技術スタック

### バックエンド

| レイヤー | 技術 |
|---------|------|
| Webフレームワーク | FastAPI 0.109 / Uvicorn |
| ORM | SQLAlchemy 2.0 / Alembic |
| データベース | PostgreSQL 15 |
| タスクキュー | Celery 5.3 / Redis 7 |
| LLMクライアント | Anthropic SDK / OpenAI SDK |
| 認証 | python-jose (JWT) / passlib (bcrypt) |
| レート制限 | slowapi |
| データ分析 | pandas / scikit-learn / scipy |
| 設定管理 | pydantic-settings / python-dotenv |

### フロントエンド

| レイヤー | 技術 |
|---------|------|
| UI | React 18 / TypeScript |
| 状態管理 | Zustand |
| スタイリング | Tailwind CSS / Emotion |
| ルーティング | React Router v6 |
| デスクトップ | Electron 29 |
| テスト | Vitest / Testing Library |

---

## セットアップ

### 前提条件

- Python 3.12+
- Docker & Docker Compose
- Node.js 18+（フロントエンド開発時）

### 1. バックエンドの起動

```bash
# リポジトリをクローン
git clone https://github.com/fukukei23/orchestrix.git
cd orchestrix

# Dockerコンテナを起動（PostgreSQL + Redis + API + Celery）
docker-compose up -d
```

これで以下が立ち上がる:
- APIサーバー: http://localhost:8000
- APIドキュメント: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6380

### 2. データベースの初期化

```bash
# コンテナ内でマイグレーションを実行
docker-compose exec api alembic upgrade head

# 初期マイグレーションが未作成の場合
docker-compose exec api alembic revision --autogenerate -m "Initial migration"
docker-compose exec api alembic upgrade head
```

### 3. 環境変数の設定

`.env`ファイルを作成:

```bash
# LLM API キー（使用するエージェントのみ設定すればよい）
ANTHROPIC_API_KEY=sk-ant-xxx...
OPENAI_API_KEY=sk-proj-xxx...
GLM_API_KEY=xxx...
MINIMAX_API_KEY=xxx...
KIMI_API_KEY=sk-xxx...
GOOGLE_API_KEY=xxx...

# データベース
DATABASE_URL=postgresql://orchestrix:orchestrix_dev@postgres:5432/orchestrix
REDIS_URL=redis://redis:6379/0
```

### 4. フロントエンド（開発時のみ）

```bash
cd frontend
npm install
npm run dev          # Vite開発サーバー
npm run electron     # Electronデスクトップアプリ
```

---

## API エンドポイント

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/` | API情報 |
| GET | `/health` | ヘルスチェック |
| POST | `/api/v1/auth/login` | ログイン |
| CRUD | `/api/v1/tasks` | タスク管理 |
| CRUD | `/api/v1/agents` | エージェント設定 |
| GET | `/api/v1/analytics` | 分析データ |
| CRUD | `/api/v1/executions` | 実行履歴 |

> 起動後 `http://localhost:8000/docs` でSwagger UIが利用可能

---

## テストの実行

```bash
# ユニットテスト
pytest tests/unit/

# カバレッジ付き
pytest --cov=src tests/
```

---

## デプロイガイド

### Docker Composeによる本番構成

`docker-compose.yml` をベースに以下を変更:

```yaml
# 本番向けの変更例
environment:
  - ENVIRONMENT=production
  - DEBUG=False
  - DATABASE_URL=postgresql://user:pass@db-host:5432/orchestrix
```

### セキュリティ上の注意

- 本番では `allow_origins=["*"]` を特定ドメインに制限
- JWT秘密鍵を環境変数から注入
- Redisのパスワードを設定
- slowapiによるレート制限を有効化

---

## 関連リソース

| 文書 | 説明 |
|------|------|
| [docs/AGENTS_COMPARISON.md](docs/AGENTS_COMPARISON.md) | エージェント比較表 |
| [docker-compose.yml](docker-compose.yml) | コンテナ構成定義 |
| [requirements.txt](requirements.txt) | Python依存関係 |

---

## License

MIT
