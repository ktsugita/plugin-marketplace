# Python 3.13 開発ガイド

Python 3.13 環境を対象とするコード開発での構文と機能のガイドラインです。
Python 3.12 で導入された構文（PEP 695 型パラメータなど）に加えて、以下の機能を適用します。

## 設定

`pyproject.toml` の `requires-python` で対象バージョンを指定します（Ruff の `target-version` は書かない。理由は SKILL.md を参照）。

```toml
[project]
requires-python = ">=3.13"
```

## 構文および機能の適用指針

### 1. 厳格な型絞り込み (`typing.TypeIs` / PEP 742)

型ナローイングを行うユーザー定義関数には、`TypeGuard` に代わり `TypeIs` を優先して使用してください。
`TypeIs` は真の場合だけでなく偽の場合の型絞り込みも型チェッカーに正しく伝播させます。

| アンチパターン | 推奨パターン |
|----------------|--------------|
| `from typing import TypeGuard`<br>`def is_str(val: object) -> TypeGuard[str]:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`return isinstance(val, str)` | `from typing import TypeIs`<br>`def is_str(val: object) -> TypeIs[str]:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`return isinstance(val, str)` |

### 2. 非推奨 API の宣言 (`warnings.deprecated` / PEP 702)

将来廃止予定の関数やクラスには `@warnings.deprecated` デコレータを付与してください。
型チェッカー（`ty` や `pyright`）およびランタイム実行時に適切な警告を出力させます。

```python
from warnings import deprecated


@deprecated("Use fetch_user_by_id instead")
def get_user(user_id: int) -> dict[str, str]:
    ...
```

### 3. レガシー標準ライブラリの排除 (PEP 594)

Python 3.13 では長年非推奨だった以下の標準ライブラリが完全に削除されました。
これらへの依存や古いコードのインポートは行わないでください。

- 削除されたモジュール（19 個）：`aifc`、`audioop`、`cgi`、`cgitb`、`chunk`、`crypt`、`imghdr`、`mailcap`、`msilib`、`nis`、`nntplib`、`ossaudiodev`、`pipes`、`sndhdr`、`spwd`、`sunau`、`telnetlib`、`uu`、`xdrlib`
- 代替策：HTTP 処理には `httpx` や `urllib.parse`、シェル実行には `subprocess` や `shutil` を使用してください。

### 4. フリー・スレッディング対応（実験的機能 / PEP 703）

GIL を無効化したビルド（free-threaded Python）でマルチスレッド処理を行う場合は、スレッドセーフティに注意してください。
共有データ構造へのアクセスには明示的なロック（`threading.Lock`）を適用してください。
