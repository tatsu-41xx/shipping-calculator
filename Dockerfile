FROM python:3.11-slim

WORKDIR /app

# 必要なシステムパッケージのインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Pythonパッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコピー
COPY . .

# データディレクトリを確保
RUN mkdir -p /app/data

# Streamlitのポートを公開
EXPOSE 8501

# 環境変数の設定
ENV APP_PASSWORD="default_password"

# コンテナ起動時に実行するコマンド
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]