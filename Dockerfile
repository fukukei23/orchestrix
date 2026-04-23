FROM python:3.12-slim

WORKDIR /app

# システム依存関係をインストール
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ソースコードをコピー
COPY . .

# デフォルトコマンド
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
