---
name: python-development
description: Python のコードの作成・編集、パッケージ管理、型チェック、テスト実行を行うときに使用する。Python 3.12 以降のバージョン別構文と、uv、ruff、ty、pytest のツールチェーンの指針を含む。
license: MIT
---

# Python 開発ガイドライン

プロジェクトに既存の仕組み（mypy、pyright、独自タスクなど）がある場合はそれを尊重します。新規導入や標準構成では、パッケージ・環境管理に `uv`、品質管理に `ruff`・`ty`・`pytest`、タスクと git フックに `mise` と `hk` を使います。

- `pyproject.toml`、`hk.pkl`、`mise.toml` を新規に設定・編集するときは、`references/toolchain.md` を読みます。
- `.env` と `mise.toml` による環境変数・秘密情報の管理は、`references/env-vars.md` を読みます。
- Python バージョン固有の新構文・標準ライブラリを使うときや、非推奨・削除された API を確認するときは、対象バージョン（`pyproject.toml` の `requires-python` や `.python-version`）のリファレンスを読みます。
  - Python 3.12: `references/python-3.12.md`
  - Python 3.13: `references/python-3.13.md`
  - Python 3.14: `references/python-3.14.md`
  - Python 3.15: `references/python-3.15.md`

## ツールチェーンの要点

- **uv の徹底**: `uv` 本体は `mise use uv` で入れます。Python 本体の管理（`uv python install` / `pin`）、依存追加（`uv add`、`uv add --dev ruff ty pytest`）、同期（`uv sync`）、実行（`uv run`）はすべて `uv` を経由し、`pip` や手動の venv 有効化は使いません。単一ファイルで完結するスクリプトには PEP 723 のインラインメタデータ（`# /// script`）を使います。
- **版の固定と `--locked`**: `ruff`、`ty`、`pytest` は mise の `[tools]` ではなく uv の dev 依存に入れ、`uv.lock` で固定します（`ty` は 0.0.x の間、版ごとに診断や挙動が変わりうるため）。フック、mise タスク、CI で実行する `uv run` には `--locked` を付け、`uv.lock` の意図しない書き換えを防ぎます。
- **mise と hk との役割分担**:
  - `ruff` と `ty` は `hk.pkl`（`prefix = List("uv", "run", "--locked", "--")` つきの Group）を正本にします。`ty` は変更ファイルだけでなくプロジェクト全体を検査するよう `{{files}}` を外します。
  - `pytest` はファイル単位で絞らないため、mise タスク `test`（`uv run --locked pytest`）を正本にし、`pre-push` フックと `mise run check` から呼びます。具体的な設定例は `references/toolchain.md` にあります。
- **環境変数の分離**: API キーやトークンなどの秘密情報は `.env`（`.gitignore` で除外し、`.env.example` のみコミット）に置き、非秘密の設定は `mise.toml` の `[env]` に置きます。

## 品質検証

変更をコミットまたは PR にする前に、プロジェクトに `mise` と `hk` のタスクがあれば `mise run fix` と `mise run check` を実行します。タスクがなければ `uv run ruff format .`、`uv run ruff check --fix .`、`uv run ty check .`、`uv run pytest` を順に実行して通ることを確かめます。
