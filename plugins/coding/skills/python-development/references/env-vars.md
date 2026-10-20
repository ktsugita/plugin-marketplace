# 環境変数と機密情報の管理（.env と mise.toml の使い分け）

秘密と非秘密の使い分けの規則は、`SKILL.md` に従います。Python から `.env` を読むときは、`python-dotenv`（`uv add python-dotenv`）または `pydantic-settings`（`uv add pydantic-settings`）を使います。

## `python-dotenv` による読み込み例

スクリプトやシンプルなアプリケーションのエントリポイントで `load_dotenv()` を呼び出します。

```python
import os
from dotenv import load_dotenv

# .env ファイルから環境変数をロード（既存の環境変数は上書きしない）
load_dotenv()

api_key = os.getenv("API_KEY")
```

## `pydantic-settings` による型安全な設定管理例

設定項目が多く型検証やデフォルト値が必要な場合は `pydantic-settings` を使用します。

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    api_key: str
    log_level: str = "INFO"
    port: int = 8000


settings = Settings()
```

## `mise.toml` での設定例

```toml
[env]
LOG_LEVEL = "INFO"
APP_PORT = "8000"
# ローカル開発時に .env の内容を mise 経由でも自動読み込みする場合
_.file = ".env"
```
