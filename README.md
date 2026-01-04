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

本リポジトリでは、アプリ言語に依存しない共通ツールとして Node.js ベースの Lint/Format を採用しています（Markdown/YAML/JSON などの整形・検査に利用）。

- 前提
  - Node.js 18 以上（LTS 推奨）
  - npm

- セットアップ

```pwsh
npm i
```

- 実行コマンド

```pwsh
# 開発（現時点ではダミー）
npm run dev

# Lint（markdownlint + prettier チェック）
npm run lint

# Format（prettier で自動整形）
npm run format

# Test（将来のテスト追加までダミー）
npm test

# Build（将来のビルド追加までダミー）
npm run build
```

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
