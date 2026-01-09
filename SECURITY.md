# セキュリティ機能ドキュメント

## 概要

このアプリケーションには最低限のセキュリティ対策が組み込まれています。すべての対策は OWASP Top 10 のベストプラクティスに基づいています。

## 実装済みセキュリティ対策

### 1. 入力バリデーション（A3: Injection 対策）

#### メール検証
- RFC 5322 準拠のメールアドレスフォーマット検証
- 最大長: 254 文字
- 自動的に小文字に正規化

**使用例:**
```python
from app.core.validators import EmailValidator

email = EmailValidator.validate_email("User@EXAMPLE.COM")
# 結果: "user@example.com"
```

#### パスワード強度検証
必須要件:
- 最低 8 文字以上
- 大文字 1 文字以上（A-Z）
- 小文字 1 文字以上（a-z）
- 数字 1 文字以上（0-9）
- 特殊文字 1 文字以上（!@#$%^&* など）

**使用例:**
```python
from app.core.validators import PasswordValidator

try:
    password = PasswordValidator.validate_password("Weak123")
except ValueError as e:
    print(e)  # "Password must contain at least one special character"
```

#### SQL インジェクション対策
危険なキーワード検出:
- UNION, SELECT, INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, EXEC
- コメント記号（--、;、/*、*/）
- OR 条件パターン
- LIKE ワイルドカード

**使用例:**
```python
from app.core.validators import SQLInjectionValidator

try:
    SQLInjectionValidator.validate_input("admin'; DROP TABLE users; --")
except ValueError as e:
    print(e)  # "Invalid input detected (potential SQL injection)"
```

#### XSS（Cross-Site Scripting）対策
危険なHTMLタグ・属性検出:
- `<script>`, `<iframe>`, `<img>`
- `onerror=`, `onload=`, `onclick=` 属性

**使用例:**
```python
from app.core.validators import XSSValidator

try:
    XSSValidator.validate_input("<script>alert('XSS')</script>")
except ValueError as e:
    print(e)  # "Invalid input detected (potential XSS)"
```

### 2. 認証・認可（A01: Broken Access Control 対策）

#### JWT ベースの認証
- **トークン生成**: RS256 署名
- **有効期限**: 30 分（デフォルト）
- **クレーム**: Subject (sub) に ユーザーID を保持

**エンドポイント:**
```bash
# ログイン
curl -X POST http://localhost:3000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Password@123"}'

# レスポンス
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### パスワード管理
- **ハッシング**: bcrypt (cost=12)
- **ソルティング**: 自動的にランダムソルトを生成
- **平文保存禁止**: すべてのパスワードはハッシュされて保存

**使用例:**
```python
from app.core.security import hash_password, verify_password

# パスワードのハッシング
hashed = hash_password("Password@123")

# パスワード検証
is_valid = verify_password("Password@123", hashed)  # True
```

#### 保護エンドポイント
`Authorization` ヘッダーでJWT を指定:

```bash
curl -H "Authorization: Bearer <your-token>" \
  http://localhost:3000/api/v1/protected
```

### 3. セキュリティヘッダー（A05: Security Misconfiguration 対策）

すべてのレスポンスに以下のセキュリティヘッダーが自動付与されます：

| ヘッダー | 値 | 目的 |
|---------|-----|------|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | HTTPS 強制、1 年間 |
| `X-Content-Type-Options` | `nosniff` | MIME タイプスニッフィング防止 |
| `X-Frame-Options` | `DENY` | クリックジャッキング防止 |
| `X-XSS-Protection` | `1; mode=block` | レガシーXSS 保護 |
| `Content-Security-Policy` | ポリシー文字列（下記参照） | インラインスクリプト制限 |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | リファラー情報制限 |
| `Permissions-Policy` | 機能ごとの許可設定 | マイク・カメラなど制限 |

**Content-Security-Policy の詳細:**
```
default-src 'self'                          # デフォルトは同一オリジンのみ
script-src 'self' 'unsafe-inline'          # スクリプトは同一オリジンか インライン
style-src 'self' 'unsafe-inline'           # スタイルは同一オリジンかインライン
img-src 'self' data: https:                # 画像は同一オリジン、data:URL、HTTPS
connect-src 'self'                         # API 呼び出しは同一オリジンのみ
frame-ancestors 'none'                     # iframe での埋め込み禁止
base-uri 'self'                            # base タグは同一オリジンのみ
form-action 'self'                         # フォーム送信は同一オリジンのみ
```

### 4. CSRF（Cross-Site Request Forgery）対策

#### トークンベースCSRF 保護
- **トークン生成**: 32 バイト のランダムトークン
- **有効期限**: 1 時間
- **検証**: X-CSRF-Token ヘッダーで検証

**使用例:**
```python
from app.core.csrf import csrf_token_manager

# トークン生成
token = csrf_token_manager.generate_token()

# トークン検証
try:
    csrf_token_manager.verify_token(token)
    print("Valid CSRF token")
except HTTPException:
    print("Invalid or expired CSRF token")
```

### 5. レート制限（A14: Resource Exhaustion 対策）

クライアント IP ベースのレート制限:

| 制限 | 値 |
|-----|-----|
| 分単位 | 60 リクエスト/分 |
| 時単位 | 1000 リクエスト/時 |

**制限超過時:**
```json
{
  "detail": "Rate limit exceeded"
}
```
ステータスコード: 429 (Too Many Requests)

### 6. 相関ID（Correlation ID）による監査ログ

すべてのリクエスト・レスポンスに一意な相関ID を付与:
- **ヘッダー**: X-Correlation-ID
- **フォーマット**: UUID v4
- **ログ記録**: すべてのログエントリに自動含有
- **カスタマイズ**: クライアントから指定可能

**使用例:**
```bash
# カスタム相関ID を指定
curl -H "X-Correlation-ID: my-custom-id-123" \
  http://localhost:3000/api/v1/login

# レスポンスヘッダーに含まれる
# X-Correlation-ID: my-custom-id-123
```

## セキュリティテスト

29 個のセキュリティテストケースが実装されています：

```bash
# セキュリティテスト実行
pytest tests/test_security.py -v

# 結果: 29 passed
```

テスト項目:
- メール検証（有効・無効・正規化）
- パスワード検証（強度・要件チェック）
- SQL インジェクション検出
- XSS パターン検出
- ログイン認証
- ユーザー登録バリデーション
- 保護エンドポイントアクセス制御
- CSRF トークン生成・検証・期限切れ

## セキュリティベストプラクティス

### 本番環境での注意事項

1. **SECRET_KEY の変更**
   ```python
   # app/core/security.py
   SECRET_KEY = "your-secret-key-change-in-production"  # 環境変数から読み込む
   ```
   環境変数から読み込み、ファイルに保存しないこと

2. **HTTPS の使用**
   - 本番環境では必ず HTTPS を使用
   - HSTS ヘッダーが設定されている

3. **CORS の適切な設定**
   - `.env.example` でホワイトリストを管理
   - ワイルドカード `*` は使用しない

4. **データベース接続**
   - SQL パラメータ化クエリの使用
   - ORM（SQLAlchemy など）の使用推奨
   - このコードの SQL インジェクション対策は基本的な検出のみ

5. **環境変数管理**
   - `.env` ファイルは `.gitignore` に含める
   - 機密情報（API キー、DB パスワードなど）は環境変数に

6. **ロギング**
   - 本番環境では `LOG_JSON_FORMAT=true` でJSON ログを使用
   - ログ集約ツール（ELK Stack など）と連携

7. **監視・アラート**
   - レート制限超過の監視
   - 認証失敗の監視
   - 異常なバリデーションエラーの監視

## 参考資料

- [OWASP Top 10](https://owasp.org/Top10/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [RFC 7807 - Problem Details for HTTP APIs](https://tools.ietf.org/html/rfc7807)
- [RFC 5322 - Internet Message Format](https://tools.ietf.org/html/rfc5322)

## 今後の拡張

- OAuth 2.0 / OIDC 対応
- 2FA（Two-Factor Authentication）
- セッション管理の強化
- Database-backed CSRF トークン管理
- 分散レート制限（Redis ベース）
- セキュリティ監査ログの詳細化
