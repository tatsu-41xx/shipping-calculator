# 送料シミュレーター

## 概要
このアプリケーションは、3PL事業者向けに全国への配送料金を事前に見積もるためのシミュレーションツールです。出荷実績がないクライアントに対して、地域別人口分布に基づいた予測配送数と総送料を計算します。

## 機能
- 荷物サイズと想定される全国総出荷個数に基づく送料シミュレーション
- 地域別人口分布を考慮した出荷数の予測
- 地域別送料と総送料の計算
- パスワード保護による機密データの保護

## 使い方
1. アプリケーションを起動し、ログイン画面でパスワードを入力
2. 「荷物サイズ」を選択（60cm～180cm、コンパクト、ゆうパケットから選択）
3. 「想定される全国総出荷個数」を入力
4. 「計算」ボタンをクリックしてシミュレーション結果を表示

## インストール方法

### Dockerを使用する場合（推奨）
```bash
# リポジトリをクローン
git clone https://github.com/yourusername/shipping-calculator.git
cd shipping-calculator

# .envファイルの作成
cp .env.example .env
# エディタで.envファイルを開き、パスワードを設定

# Dockerでアプリケーションを起動
docker-compose up -d

# ブラウザで http://localhost:8501 にアクセス
```

### Dockerを使用しない場合
```bash
# リポジトリをクローン
git clone https://github.com/yourusername/shipping-calculator.git
cd shipping-calculator

# 必要なパッケージをインストール
pip install -r requirements.txt

# 環境変数の設定（.envファイルを作成するか、直接設定）
cp .env.example .env
# エディタで.envファイルを開き、パスワードを設定

# アプリケーションの起動
streamlit run app.py
```

## デプロイ方法
このアプリケーションはStreamlit Cloudにデプロイすることができます：

1. GitHub上でこのリポジトリをフォークまたはクローン
2. [Streamlit Cloud](https://streamlit.io/cloud)にログイン
3. 「New app」ボタンをクリック
4. リポジトリとブランチを選択
5. メインファイルパスとして「app.py」を設定
6. 「Advanced settings」でシークレット変数として「APP_PASSWORD」を設定
7. 「Deploy」ボタンをクリック

## 注意事項
- このアプリケーションは人口分布に基づいた予測であり、実際の出荷パターンは顧客の業種や商品特性によって異なる場合があります
- 送料データは定期的に更新する必要があります
  - サンプルは2025年3月時点のヤマト運輸の料金を参考にしています。
- パスワードは安全に管理し、定期的に変更することをお勧めします

## ライセンス
MIT License