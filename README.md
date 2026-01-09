# ai-dev-advanced-exercises4

## プロジェクト概要

- スイーツ専門ECサイトの開発基盤リポジトリです。
- 要求特性: 高負荷対応、在庫のリアルタイム連携、拡張性の高いアーキテクチャ、将来的なAI機能連携を前提。
- 本リポジトリではまず開発ルール・テンプレ・CI・Lint/Formatの共通基盤を整備します（アプリ実装言語は今後追加）。

## 開発フロー

- ブランチ戦略
  - `main` : 本番リリース用ブランチ
  - `develop` : 開発統合ブランチ
  - `feature/ISxxx-<short>` : 機能開発ブランチ（例: `feature/IS015-cart`）
  - `fix/ISxxx-<short>` : 不具合修正ブランチ
  - `chore/ISxxx-<short>` : 事務・整備タスクブランチ

- PR運用
  - レビュー必須（最低1名）。
  - CI通過必須（Lint/Test/Buildのうち該当範囲）。
  - マージ方式は Squash 推奨。
  - PRタイトル規約: `[ISxxx] <簡潔な概要>`（例: `[IS015] カート追加`）。

- コミット規約（Conventional Commits 風）
  - `feat: <概要>` 新機能
  - `fix: <概要>` バグ修正
  - `chore: <概要>` ビルド/設定/整備
  - `docs: <概要>` ドキュメントのみ
  - `refactor: <概要>` 挙動変更なしの改善
  - `test: <概要>` テスト関連

## 命名規約（最低限）

- Issue ID: `ISxxx`（例: `IS001`）
- ブランチ名: `feature/IS001-setup-ci` のように `種別/IssueID-短い説明`。
- PRタイトル: `[IS001] リポジトリ初期設定` の形式。
- ラベル例: `priority:Must`, `priority:Should`, `priority:Could`, `type:bug`, `type:feature`, `type:chore` など。

## ローカル開発

本リポジトリは **Python (FastAPI)** ベースのアプリケーションです。ドキュメント用に Node.js も使用します。

### 必要なツール

以下のツールを事前にインストールしてください：

- **Git**: 2.30 以上
  - [公式サイト](https://git-scm.com/)からインストール
  - Windows: Git for Windows 推奨
- **Python**: 3.11 以上（3.12 推奨）
  - [公式サイト](https://www.python.org/)からダウンロード
  - バージョン確認: `python --version`
- **Node.js**: 18.x 以上（LTS 推奨、現在は 20.x を推奨）
  - [公式サイト](https://nodejs.org/)からダウンロード
  - バージョン確認: `node -v`
  - 用途: ドキュメント lint/format のみ
- **npm**: Node.js に同梱（7.x 以上）
  - バージョン確認: `npm -v`
- **エディタ**: VS Code 推奨
  - [公式サイト](https://code.visualstudio.com/)
  - 推奨拡張機能:
    - Python (Microsoft)
    - Pylance (Microsoft)
    - Ruff
    - Prettier - Code formatter
    - markdownlint
    - EditorConfig for VS Code

### セットアップ手順

1. **リポジトリをクローン**

```pwsh
git clone https://github.com/mshr1-create/ai-dev-advanced-exercises4.git
cd ai-dev-advanced-exercises4
```

2. **ブランチを確認・切り替え**

```pwsh
# develop ブランチに移動（開発のベース）
git checkout develop
git pull origin develop
```

3. **Python依存関係をインストール**

```pwsh
pip install -e ".[dev]"
```

4. **ドキュメント用依存関係をインストール**

```pwsh
npm i
```

5. **環境変数を設定**

```pwsh
# .env.example をコピーして .env を作成
cp .env.example .env
# 必要に応じて .env の値を編集
```

6. **動作確認**

```pwsh
# Python lint チェック
ruff check app tests

# Python format チェック
black --check app tests

# ドキュメント lint チェック
npm run lint
```

### 実行コマンド

```pwsh
# Python開発サーバー起動 (FastAPI)
uvicorn app.main:app --reload --port 3000

# Python lint
ruff check app tests

# Python format (自動修正)
black app tests

# Python type check
mypy app

# Python test
pytest

# Python test with coverage
pytest --cov=app --cov-report=html

# ドキュメント lint
npm run lint

# ドキュメント format
npm run format
```

### 環境変数

プロジェクトで使用する環境変数は `.env.example` を参照してください。

| 変数名   | 説明                               | デフォルト値 | 必須 |
| -------- | ---------------------------------- | ------------ | ---- |
| NODE_ENV | 実行環境（development/production） | development  | No   |
| PORT     | アプリケーションポート（将来用）   | 3000         | No   |

※ 現時点ではアプリ実装がないため、環境変数は使用されていません。

### トラブルシューティング

#### `npm i` で依存関係のインストールに失敗する

**症状**: `npm ERR!` エラーが出る

**対処法**:

1. Node.js のバージョンを確認（18.x 以上が必要）

```pwsh
node -v
```

2. npm キャッシュをクリア

```pwsh
npm cache clean --force
npm i
```

3. `node_modules` と `package-lock.json` を削除して再インストール

```pwsh
rm -r node_modules
rm package-lock.json
npm i
```

#### `npm run lint` で大量のエラーが出る

**症状**: Markdown や整形エラーが多数表示される

**対処法**:

1. 自動整形を実行

```pwsh
npm run format
```

2. 再度 Lint を実行

```pwsh
npm run lint
```

#### Git のブランチ操作でエラーが出る

**症状**: `error: Your local changes to the following files would be overwritten by checkout`

**対処法**:

1. 変更をコミットまたはスタッシュ

```pwsh
# コミットする場合
git add -A
git commit -m "chore: 作業中の変更を保存"

# 一時退避する場合
git stash
```

2. ブランチを切り替え

```pwsh
git checkout develop
```

#### Windows で改行コードの警告が出る

**症状**: `warning: LF will be replaced by CRLF`

**対処法**:

1. Git の autocrlf 設定を確認

```pwsh
git config --global core.autocrlf true
```

2. `.editorconfig` の設定に従うよう、エディタを設定（VS Code は自動対応）

#### 起動時に30分以上かかる場合

**対処法**:

1. インターネット接続を確認（npm レジストリへのアクセスが必要）
2. 企業プロキシ環境の場合、npm プロキシ設定を確認

```pwsh
npm config get proxy
npm config get https-proxy
```

3. Node.js を再インストール（破損している可能性）

## CI

- 対象: Pull Request 全て、`main`/`develop` への push。
- 実行内容:
  - Lint: `markdownlint` と `prettier --check`。
  - Test: 現状はダミー（将来、実装に応じて拡充）。
  - Build: 現状はダミー（将来、実装に応じて拡充）。
- Node をセットアップし、依存解決後に `npm run lint` → `npm test` → `npm run build` を順に実行します。

---

## 参考: フェーズ/優先度の使い分け

- 想定フェーズ: `Design` / `Implementation` / `Test` / `Release`
- 優先度: `Must` / `Should` / `Could`

## ライセンス

（プロジェクトの方針に合わせて別途定義）
