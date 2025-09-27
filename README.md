# Confluence Document Retrieval Tool

PythonでConfluenceにアクセスして文書を取得するツールです。

## セットアップ

### 1. 依存関係のインストール

```bash
# 仮想環境の作成とアクティベート
python3 -m venv venv
source venv/bin/activate

# パッケージのインストール
pip install -r requirements.txt
```

### 2. 設定ファイルの作成

#### 方法A: config.yamlを使用する場合

```bash
cp config.yaml.example config.yaml
```

`config.yaml`を編集して実際の値を設定：

```yaml
confluence:
  base_url: "https://yourcompany.atlassian.net"
  username: "your-email@company.com"
  api_token: "your-api-token-here"

settings:
  output_dir: "output"
  default_limit: 50
```

#### 方法B: 環境変数を使用する場合

```bash
cp .env.example .env
```

`.env`を編集して実際の値を設定：

```bash
CONFLUENCE_URL=https://yourcompany.atlassian.net
CONFLUENCE_USERNAME=your-email@company.com
CONFLUENCE_API_TOKEN=your-api-token-here
```

### 3. API Tokenの取得

1. [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)にアクセス
2. "Create API token"をクリック
3. 適切な名前を入力してトークンを作成
4. 生成されたトークンをコピーして設定ファイルに記載

## 使用方法

### コマンドライン使用例

```bash
# 仮想環境をアクティベート
source venv/bin/activate

# ヘルプを表示
python confluence_client.py --help

# 全スペースを表示（設定ファイルから認証情報を読み込み）
python confluence_client.py

# 特定スペースのページ一覧
python confluence_client.py --space DEMO

# 特定ページをエクスポート
python confluence_client.py --page-id 123456

# 検索
python confluence_client.py --search "text ~ 'meeting'"

# コマンドラインで認証情報を指定（設定ファイルより優先）
python confluence_client.py --base-url https://example.atlassian.net --username user@example.com --token your-token --space DEMO
```

### プログラム内での使用

```python
from confluence_client import ConfluenceClient

# 設定ファイルから読み込み
from confluence_client import load_config
config = load_config()
client = ConfluenceClient(config['base_url'], config['username'], config['api_token'])

# または直接指定
client = ConfluenceClient(
    "https://yourcompany.atlassian.net",
    "your-email@company.com",
    "your-api-token"
)

# スペース一覧を取得
spaces = client.get_spaces()
for space in spaces:
    print(f"Space: {space['name']} (Key: {space['key']})")
```

## 機能

- ✅ スペース一覧の取得
- ✅ 特定スペース内のページ取得
- ✅ ページIDによる特定ページの取得
- ✅ CQLを使った検索
- ✅ ページのHTMLファイルエクスポート
- ✅ 設定ファイル対応（YAML/環境変数）

## テスト済み機能

このツールは以下の環境で動作確認済みです：

### 動作確認済み機能
- ✅ Confluence Cloud接続
- ✅ スペース一覧取得
- ✅ ページ一覧取得
- ✅ 個別ページエクスポート（HTMLファイル出力）
- ✅ 設定ファイル読み込み（.env形式）

### テスト例
```bash
# スペース一覧の取得
python confluence_client.py
# → Available spaces: hirokazu miyata (Key: ~71202037...)

# 特定スペースのページ取得
python confluence_client.py --space "~71202037..."
# → 概要, ミーティング議事録 等のページ一覧を取得

# ページエクスポート
python confluence_client.py --page-id 163842
# → output/2025-09-27 ミーティング議事録.html として出力
```

## ファイル構成

- `confluence_client.py` - メインのクライアントクラス
- `example_usage.py` - 使用例
- `config.yaml.example` - YAML設定ファイルのテンプレート
- `.env.example` - 環境変数ファイルのテンプレート
- `requirements.txt` - 必要なPythonパッケージ

## 注意事項

- 設定ファイル（`config.yaml`、`.env`）には機密情報が含まれるため、バージョン管理システムにコミットしないでください
- `.gitignore`に`config.yaml`と`.env`が含まれていることを確認してください