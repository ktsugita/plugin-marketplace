# Python ツールチェーンの設定例（pyproject.toml・hk.pkl・mise.toml）

プロジェクトに uv、ruff、ty、pytest、mise、hk を導入・設定するときの構成例です。

## `pyproject.toml`

プロジェクトのメタデータ、Ruff、pytest の設定を `pyproject.toml` に集約します。Ruff は `[tool.ruff]` の `target-version` を省略すると `requires-python` から推論するため、`target-version` は書きません。

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

- pytest 9 以降はネイティブの `[tool.pytest]` テーブルを使います（pytest 9 未満との互換が必要な場合のみ `[tool.pytest.ini_options]`）。
- 非同期テストがある場合は `uv add --dev pytest-asyncio` を入れ、`[tool.pytest]` に `asyncio_mode = "auto"` を追加します（未指定時は `strict`）。

## `hk.pkl` と `mise.toml` の連携

- ruff、ty、pytest は uv の dev 依存に入れ、版は `uv.lock` だけで固定します（mise の `[tools]` には入れません）。
- `hk.pkl` では Builtins（`ruff`、`ruff_format`、`ty`）を Group にまとめ、`prefix = List("uv", "run", "--locked", "--")` を付けます。
  - `prefix` を付けた Group には、文字列形式のコマンド（`check = "ruff check && ..."` など）のステップを入れられません。
  - `Builtins.ty` は既定で `{{files}}` のみを検査するため、型エラーの波及を見逃さないよう `check` を上書きしてプロジェクト全体を検査します。
- フック、タスク、CI のすべての `uv run` に `--locked` を付け、フック実行中の `uv.lock` の書き換えと再ステージの干渉を防ぎます。

`hk.pkl`（`amends` と `import` の URL は `hk init` が生成したものをそのまま使う）:

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

`mise.toml`:

```toml
[tasks.test]
run = "uv run --locked pytest"

[tasks.check]
run = ["hk check --all", "mise run test"]

[tasks.fix]
run = "hk fix --all"
```

- 個別のステップだけを走らせるときは、mise タスクを増やさずに `hk check -S ty` のように指定します。
- CI では `jdx/mise-action` で mise と uv を入れ（`setup-uv` は併用しない）、`mise run check` を実行します。
