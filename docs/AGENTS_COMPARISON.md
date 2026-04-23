# AI エージェント比較表

Orchestrix で使用可能な AI エージェントとコスト比較

## エージェント一覧

| エージェント | CLI コマンド | デフォルトモデル | 入力コスト(1k) | 出力コスト(1k) | 主な機能 | 有効化 |
|-----------|--------------|---------------|----------------|----------------|---------|--------|
| **Claude Code** | `claude` | claude-sonnet-4.5 | $3.00 | $15.00 | コード、ファイル編集、Bash | ✅ |
| **GLM (智谱AI)** | `glm` | glm-4-flash | $0.20 | $0.60 | コード、中国語対応 | ✅ |
| **MiniMax** | `minimax` | abab6.5s-chat | $0.15 | $0.30 | コード、中国語対応 | ✅ |
| **Kimi (Moonshot AI)** | `kimi` | moonshot-v1-8k | $0.30 | $0.80 | コード、中国語対応 | ✅ |
| **Codex CLI** | `codex` | gpt-4 | $30.00 | $60.00 | コード、ファイル編集 | ✅ |
| **Gemini CLI** | `gemini` | gemini-1.5-pro | $1.25 | $5.00 | コード、マルチモーダル | ✅ |

## コスト比較（推定）

タスクサイズ: 10k 入力トークン + 5k 出力トークン

| エージェント | 入力コスト | 出力コスト | 合計コスト |
|-----------|-----------|-----------|----------|
| Claude Code | $30.00 | $75.00 | **$105.00** |
| GLM | $2.00 | $3.00 | **$5.00** |
| MiniMax | $1.50 | $1.50 | **$3.00** |
| Kimi | $3.00 | $4.00 | **$7.00** |
| Codex CLI | $300.00 | $300.00 | **$600.00** |
| Gemini CLI | $12.50 | $25.00 | **$37.50** |

## 用途推奨

### 高品質・重要タスク
- **Claude Code**: 最も品質が高いが、コストも高い
- **GPT-4o (OpenAI)**: 高品質なコード生成

### コスト重視・日常開発
- **MiniMax**: 最も安価、日常的なコード生成に最適
- **GLM**: 安価で高速、中国語プロジェクトに最適
- **Kimi**: 安価で 8k コンテキスト

### バランス重視
- **Gemini**: マルチモーダル（画像処理）対応

## API キー設定

`.env` ファイルに以下の API キーを設定してください：

```bash
# Anthropic (Claude Code)
ANTHROPIC_API_KEY=sk-ant-xxx...

# OpenAI (GPT-4o)
OPENAI_API_KEY=sk-proj-xxx...

# OpenCLAW
OPENCLAW_API_KEY=xxx...

# GLM (智谱AI)
GLM_API_KEY=xxx...

# MiniMax
MINIMAX_API_KEY=xxx...

# Kimi (Moonshot AI)
KIMI_API_KEY=sk-xxx...

# Google Gemini
GOOGLE_API_KEY=xxx...
```

## エージェントの有効化

`config/agents.yaml` で各エージェントの `enabled` を `true` または `false` に変更して有効化を管理できます。
