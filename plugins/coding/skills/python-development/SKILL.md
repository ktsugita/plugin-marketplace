---
name: python-development
description: Python のコードの作成・編集、パッケージ管理、型チェック、テスト実行を行うときに使用する。Python 3.12 以降のバージョン別構文と、uv、ruff、ty、pytest のツールチェーンの指針を含む。
license: MIT
---

Python 環境でコードの設計、実装、テストを行う際は以下のガイドラインに従ってください。
Python を扱う場合は常に **uv** を使用します。

## uv の導入（未インストール時）

uv のインストールおよびバージョン管理には **mise** を使用します。

```bash
mise use uv
```

mise の導入と使い方は、`mise` スキルが使える場合はそれに従います。使えない場合は mise の公式ドキュメント（https://mise.jdx.dev/）を参照します。

## ツールチェーンとコマンド対応表

すべての環境操作、パッケージ管理、スクリプト実行は `uv` を経由し、品質ツールには `ruff`、`ty`、`pytest` を統一して使用します。

| 操作 | 推奨コマンド | 旧コマンドやアンチパターン |
|------|--------------|-----------------------------|
| プロジェクト初期化 | `uv init <project-name>` | `mkdir app && cd app && pip init` |
| パッケージ追加 | `uv add <pkg>` | `pip install <pkg>` |
| 開発用パッケージ追加 | `uv add --dev <pkg>` | `pip install <pkg>` / `poetry add -D` |
| パッケージ削除 | `uv remove <pkg>` | `pip uninstall <pkg>` |
| 依存関係や環境の同期 | `uv sync` | `pip install -r requirements.txt` / `pip install -e .` |
| 仮想環境作成 | `uv venv` | `python -m venv .venv` |
| Pythonバージョン管理 | `uv python install <ver>` / `uv python pin <ver>` | `pyenv install 3.x` / `pyenv local 3.x` |
| スクリプト実行 | `uv run <script.py>` | `python <script.py>` (手動での仮想環境アクティベート) |
| テスト実行 | `uv run pytest` | `pytest` / `python -m unittest` |
| リンターとフォーマッター | `uv run ruff check --fix .` / `uv run ruff format .` | `flake8` / `black` / `isort` |
| 型チェック | `uv run ty check .` | `mypy` / `pyright` (新規プロジェクトでの採用) |
| 単発CLIツール実行 | `uvx <tool>` | `pipx run <tool>` |

- `uv run` はプロジェクトの環境でコマンドを実行します。`uv run ruff` などを使う前に、品質ツールを dev 依存に入れてください（`uv add --dev ruff ty pytest`）。dev 依存に入れない場合は `uvx ruff`、`uvx ty check` を使います。
- ty は beta の間（版が 0.0.x の間）、診断を含めて版ごとに破壊的変更がありえます。現在の状態は ty のリリースノート（https://github.com/astral-sh/ty/releases）で確かめます。dev 依存に入れて版を `uv.lock` で固定してください。既存のプロジェクトで mypy や pyright を使っている場合は、そちらを尊重します。

### 他ツールとの連携

タスクランナーと非秘密の環境変数管理には `mise` を使用します。

## mise と hk との連携

mise でタスクを、hk で git フックを管理するプロジェクトでは、ruff、ty、pytest を次の形で呼び出します。

| 方針 | 理由 |
|---|---|
| ruff、ty、pytest は dev 依存に入れ、版は `uv.lock` だけで固定する。mise の `[tools]` には入れない | 版の出どころが1か所になり、手元、フック、CI で版がずれないため。pytest と ty はプロジェクトの venv で import を解決するため、venv の外に置けない。 |
| ruff と ty の呼び出しは `hk.pkl` を正本にし、pytest は mise タスク `test` を正本にする | ステージしたファイルへの絞り込み、fix、再ステージを hk に任せられるため。pytest はファイル単位で絞る対象ではない。 |
| hk の Builtins（`ruff_format`、`ruff`、`ty`）を Group にまとめ、`prefix` で `uv run --locked --` を前に付ける | Builtins は PATH 上の素の `ruff` や `ty` を呼ぶため。Builtins の定義を書き写さずに、`uv.lock` の版で動かせる。 |
| `uv run` には、フック、タスク、CI のすべてで `--locked` を明示する | 何も付けない `uv run` は lock を取り直して `uv.lock` を書き換えることがあり、フックの stash や再ステージと干渉するため。`--locked` なら、lock が `pyproject.toml` とずれたときに書き換えずに失敗する。 |
| ty は `{{files}}` を渡さず、プロジェクト全体を検査する | 型エラーは変更していないファイルにも及ぶため。`Builtins.ty` は `ty check {{files}}` で、渡したファイルの診断しか出さない。 |
| pre-commit では ruff format、ruff check の fix、ty を走らせ、pytest は pre-push で走らせる | ruff の既定の `--fix` は safe fix だけを適用する。pytest はコミットごとに走らせるには遅いことが多い。 |
| 人と CI の入口を `mise run check` にそろえる | 手元で `mise run check` が通れば CI も通るという対応を保つため。 |

`hk.pkl` の例です。`amends` と `import` の URL は、`hk init` が生成したものをそのまま使います。

```pkl
amends "package://github.com/jdx/hk/releases/download/v<hk の版>/hk@<hk の版>#/Config.pkl"
import "package://github.com/jdx/hk/releases/download/v<hk の版>/hk@<hk の版>#/Builtins.pkl"

local python = new Group {
  prefix = List("uv", "run", "--locked", "--")
  steps {
    ["ruff"] = Builtins.ruff
    // Group の子ステップは並行して走りうるので、ruff の fix の後に整形する
    ["ruff-format"] = (Builtins.ruff_format) {
      depends = "ruff"
    }
    ["ty"] = (Builtins.ty) {
      // {{files}} を外し、.py / .pyi が変わったときにプロジェクト全体を検査する
      check = new CommandSpec {
        command = new Command { argv = List("ty", "check") }
        effect = "read"
      }
    }
  }
}

hooks {
  ["pre-commit"] {
    fix = true
    stash = "git"
    steps { ["python"] = python }
  }
  ["pre-push"] {
    steps {
      ["test"] { check = "mise run test" }
    }
  }
  ["check"] { steps { ["python"] = python } }
  ["fix"] { fix = true; steps { ["python"] = python } }
}
```

`mise.toml` のタスクの例です。

```toml
[tasks.test]
run = "uv run --locked pytest"

[tasks.check]
run = ["hk check --all", "mise run test"]

[tasks.fix]
run = "hk fix --all"
```

- 個別のステップだけを走らせるときは、mise タスクを増やさずに `hk check -S ty` のようにステップを指定する。
- argv の `prefix` を付けた Group には、文字列で書いたコマンド（`check = "ruff check && ..."` など）のステップを入れられない。hk が設定の読み込みで失敗する。
- Builtins が文字列で持つコマンド（`Builtins.ruff` の `check_diff` など）は、argv の `prefix` の下では hk が使わない。代わりに、`hk check` では argv の `check` を、fix が有効なフック（pre-commit）と `hk fix` では `fix` を実行する。どちらの場合も、素の `ruff` が PATH から呼ばれることはない。
- フックの登録は `hk install --global --mise`（Git が 2.54 より古い場合は `hk install --mise`）で行う。hk の方針は、`hk` スキルが使える場合はそれに従う。使えない場合は hk の公式ドキュメント（https://hk.jdx.dev/）を参照する。
- CI では mise を入れて（GitHub Actions では `jdx/mise-action`）、`mise run check` を実行する。uv は mise の `[tools]` で入るので、別に `setup-uv` を使わない。

## 設定ファイルとメタデータ

### `pyproject.toml` の基本設定

プロジェクトのメタデータ、Ruff、テストの設定を `pyproject.toml` に集約します。
対象の Python バージョンは `requires-python` で指定します。Ruff は `[tool.ruff]` の `target-version` を書かなければ `requires-python` から推論するので、`target-version` は書きません。

```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "RUF"]

[tool.pytest]
testpaths = ["tests"]
```

- pytest 9 からはネイティブの `[tool.pytest]` テーブルを使えます。pytest 9 未満との互換が必要な場合だけ `[tool.pytest.ini_options]` を使います。
- 非同期テストがある場合は、`uv add --dev pytest-asyncio` で pytest-asyncio を入れてから、`[tool.pytest]` に `asyncio_mode = "auto"` を足します。`asyncio_mode` は pytest 本体ではなく pytest-asyncio の設定で、指定しなければ `strict` になります。

### 単一ファイルスクリプトのインラインメタデータ (PEP 723)

単一ファイルで完結するスクリプトには、依存関係と Python バージョン要件をスクリプトヘッダーに記述します。

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx",
#     "pydantic>=2.10",
# ]
# ///

import httpx


def main() -> None:
    ...
```

### 環境変数と機密情報の管理（.env と mise.toml の使い分け）

秘密情報（API キー、DB パスワード、アクセストークン等）は `.env` に書き、必ず `.gitignore` に含めます。ダミー値を書いた `.env.example` だけをコミットします。非秘密情報（ログレベル、ポート番号等）は `mise.toml` の `[env]` に書きます。`.env` を Python から読む方法（`python-dotenv`、`pydantic-settings`）と例は、`references/env-vars.md` に従います。

### `.gitignore` の基本設定

Python プロジェクトでリポジトリに含めるべきではない仮想環境、バイトコード、各ツールのキャッシュ、機密情報は `.gitignore` で確実に除外してください（`uv init` 実行時にも初期生成されますが、不足がないか確認します）。

```gitignore
# 仮想環境
.venv/

# バイトコード・キャッシュ
__pycache__/
*.py[cod]
*$py.class

# 品質ツール・テスト・カバレッジのキャッシュ
.ruff_cache/
.pytest_cache/
.mypy_cache/
.coverage
htmlcov/

# ビルド成果物・パッケージング
dist/
build/
*.egg-info/

# 機密情報・環境変数（.env.example のみコミット対象とする）
.env
.env.*
!.env.example
```

## バージョン別リファレンスの参照

プロジェクトの `pyproject.toml` (`requires-python`) や `.python-version` を確認し、対象バージョンのリファレンスを読み込んで、該当する機能や記法を適用してください。

- **Python 3.12**: `references/python-3.12.md`
- **Python 3.13**: `references/python-3.13.md`
- **Python 3.14**: `references/python-3.14.md`
- **Python 3.15**: `references/python-3.15.md`

バージョン指定がない新規プロジェクトでは、最新の安定版またはプロジェクト要件に応じたバージョンを選択してください。

## 共通のモダン Python コーディング規約

全バージョンで共通して適用する設計原則およびコーディングパターンです。

### 1. 型注釈と組み込みジェネリクス

組み込みジェネリクス（`list`、`dict`、`tuple`）と `|` 演算子を使い、自身を返すメソッドの戻り値型には `typing.Self` を使います。

| アンチパターン | 推奨パターン |
|----------------|--------------|
| `from typing import Union`<br>`x: Union[int, str]` | `x: int \| str` |
| `from typing import List, Dict, Optional`<br>`x: Optional[List[str]]` | `x: list[str] \| None` |
| `def clone(self: T) -> T: ...` | `from typing import Self`<br>`def clone(self) -> Self: ...` |

### 2. データ構造の設計

不変な値オブジェクトには `@dataclass(frozen=True, slots=True)` を使用してください。
外部入力のバリデーションやシリアライズが必要なデータモデルには Pydantic V2 を使用してください。

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserConfig:
    user_id: str
    timeout_seconds: int = 30
```

### 3. パス操作とモダンイディオム

ファイルやディレクトリの操作には `pathlib.Path` のみを使用し、`os.path` や `os.mkdir` は使用しないでください。
内包表記や条件式で計算結果を再利用する場合は、代入式（セイウチ演算子 `:=`）を活用して重複計算を防いでください。

```python
from pathlib import Path

config_path = Path("config.json")
if config_path.exists():
    content = config_path.read_text(encoding="utf-8")
```

### 4. 構造的パターンマッチング (`match` - `case`)

複雑な `if-elif-else` や `isinstance` の連鎖、辞書の構造分解にはパターンマッチングを使用してください。

```python
match payload:
    case {"type": "text", "content": str(text)}:
        handle_text(text)
    case {"type": "image", "url": str(url)}:
        handle_image(url)
    case _:
        raise ValueError("Unknown payload format")
```

### 5. 非同期処理とタスク管理

非同期処理で複数のタスクを並行実行する際は、キャンセル伝播と例外安全性を確保するため `asyncio.TaskGroup` を使用してください。

```python
import asyncio


async def fetch_all(urls: list[str]) -> None:
    async with asyncio.TaskGroup() as tg:
        for url in urls:
            tg.create_task(fetch_url(url))
```

## テストと品質管理

### テスト規約

テストは `tests/` 配下に `test_*.py` として配置します。
`unittest.TestCase` は使用せず、純粋な関数テストと `pytest` フィクスチャを活用してください。
パラメータ化テストには `@pytest.mark.parametrize` を使用します。

```python
import pytest
from my_project.calculator import add


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (1, 2, 3),
        (-1, 1, 0),
        (0, 0, 0),
    ],
)
def test_add(a: int, b: int, expected: int) -> None:
    assert add(a, b) == expected
```

### 品質検証コマンド

変更をコミットまたはプルリクエストにする前に、対応表のコマンドを、`ruff format`、`ruff check --fix`、`ty check`、`pytest` の順に実行し、すべて通ってからコミットします。
プロジェクトが「mise と hk との連携」の形になっている場合は、`mise run fix` と `mise run check` で同じ検査を実行します。
