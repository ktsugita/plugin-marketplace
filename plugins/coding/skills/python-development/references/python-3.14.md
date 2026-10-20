# Python 3.14 開発ガイド

Python 3.14 環境を対象とするコード開発での構文と機能のガイドラインです。
Python 3.12 および 3.13 で導入された構文に加えて、以下の最新機能を適用します。

## 設定

`pyproject.toml` の `requires-python` で対象バージョンを指定します（Ruff の `target-version` は書かない。理由は SKILL.md を参照）。

```toml
[project]
requires-python = ">=3.14"
```

## 構文および機能の適用指針

### 1. アノテーションの遅延評価 (PEP 649 / 749)

Python 3.14 では型注釈が自動的に遅延評価（PEP 649 / 749）されます。
循環参照の回避を目的とした `from __future__ import annotations` の記述は不要です。

```python
# from __future__ import annotations のインポートは不要


class Node:

    def __init__(self, parent: Node | None = None) -> None:
        self.parent = parent
```

### 2. テンプレート文字列 (PEP 750)

SQL クエリ、HTML、シェルコマンドなど、構造化処理やエスケープが必要な文字列生成には、生の f-strings ではなくテンプレート文字列（`t"..."`）と専用プロセッサを使用してください。

| アンチパターン（インジェクションリスク） | 推奨パターン |
|------------------------------------------|--------------|
| `query = f"SELECT * FROM users WHERE id = {user_id}"` | `query = sql_processor(t"SELECT * FROM users WHERE id = {user_id}")` |

### 3. サブインタプリタによる並列処理 (PEP 734)

CPU 負荷の高いタスクを並列実行する場合、GIL の影響を受けずプロセスの生成コストを抑えられる `concurrent.interpreters` (PEP 734) を優先してください。

| アンチパターン | 推奨パターン |
|----------------|--------------|
| `import multiprocessing` による重いプロセス起動 | `import concurrent.interpreters` によるサブインタプリタ並列処理 |

### 4. 例外処理と制御フローの変更 (PEP 758 / 765)

PEP 758 により、`as` 節を使わない場合に限り、`except` 節で複数の例外型を括弧なしで書けます（`except ValueError, TypeError:`）。`as` 節を使う場合は、従来どおり括弧が必要です（`except (ValueError, TypeError) as e:`）。
また PEP 765 により、`finally` ブロックから制御を抜けるジャンプ（`return` や `break`、`continue`）は、3.14 から `SyntaxWarning` になります。エラーにはなりませんが、書かないでください。
`finally` ブロックにはリソース解放処理のみを記述してください。

| アンチパターン | 推奨パターン |
|----------------|--------------|
| `try:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`do_something()`<br>`finally:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`return True  # PEP 765 で SyntaxWarning` | `try:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`return do_something()`<br>`finally:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`cleanup()` |

### 5. データ圧縮とシリアライズ (PEP 784 `compression.zstd`)

高速な圧縮や展開が必要なデータ処理には、外部パッケージや `gzip` の代わりに標準ライブラリの `compression.zstd` モジュールを使用してください（`import zstd` で読み込まれるのは標準ライブラリではありません）。

```python
from compression import zstd

compressed = zstd.compress(data)
decompressed = zstd.decompress(compressed)
```

### 6. フリー・スレッディングの公式サポート (PEP 779)

3.13 で実験的機能だったフリー・スレッディング（GIL を無効にしたビルド）は、3.14 で公式サポートになりました。ただし既定のビルドではありません。使う場合はフリー・スレッディング対応の Python（`python3.14t`、uv では `uv python install 3.14t`）を明示して導入し、依存する拡張モジュールがフリー・スレッディングに対応していることを確かめてください。
