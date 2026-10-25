# Python 3.15 開発ガイド

Python 3.15 環境を対象とするコード開発での構文と機能のガイドラインです。
Python 3.12、3.13、3.14 で導入された構文に加えて、以下の最新機能を適用します。

## 設定

`pyproject.toml` の `requires-python` で対象バージョンを指定します（Ruff は `requires-python` から推論するため、`target-version` は書きません）。

```toml
[project]
requires-python = ">=3.15"
```

## 構文および機能の適用指針

### 1. 明示的な遅延インポート (`lazy` / PEP 810)

起動時間が問題になるアプリケーションで、使う場面が限られる重いモジュールには、`lazy` ソフトキーワードを使ってください。インポートを先頭にまとめたまま、名前を最初に使うときまで読み込みを遅らせられます。

| アンチパターン | 推奨パターン |
|----------------|--------------|
| 起動時間のためだけに、インポートを関数の中へ散らす（コードが読みにくく、保守しにくくなる） | `lazy import json`<br>`lazy from pathlib import Path` |

```python
lazy import json
lazy from pathlib import Path

print("Starting up...")  # json と pathlib は、まだ完全には読み込まれていない

data = json.loads('{"key": "value"}')  # ここで json が読み込まれる
```

- `lazy` を使えるのは、モジュールのトップレベルだけです。関数、クラス本体、`try`/`except`/`finally` の中では `SyntaxError` になります。`lazy from module import *` と `lazy from __future__ import ...` も `SyntaxError` です。
- 遅延させたモジュールの読み込みに失敗したとき（モジュールが存在しない場合など）、例外が発生するのは、import 文ではなく、名前を最初に使った時点です。トレースバックには、名前を使った場所と、元の import 文の両方が含まれます。
- ソースを変えずに全体を遅延にするには、`-X lazy_imports=all` か環境変数 `PYTHON_LAZY_IMPORTS=all` を使います。

### 2. 不変の辞書 (`frozendict` / PEP 814)

設定値や定数のテーブルなど、作成後に変更しない辞書には、組み込みの `frozendict` を使ってください。キーと値がすべてハッシュ可能なら、`frozendict` 自体もハッシュ可能です。挿入順は保たれ、比較では順序を見ません。

```python
settings = frozendict(host="localhost", port=8080)
settings["port"] = 9090  # TypeError: 'frozendict' object does not support item assignment
```

`frozendict` は `dict` のサブクラスではありません（`object` を直接継承します）。`isinstance(arg, dict)` で受け付ける型を絞っているコードは、`isinstance(arg, (dict, frozendict))` にするか、`isinstance(arg, collections.abc.Mapping)` にしてください。

### 3. 番兵値 (`sentinel` / PEP 661)

`None` と区別したい「指定されていない」という目印には、`object()` の代わりに、組み込みの `sentinel` を使ってください。表示が簡潔で、コピーしても同一性が保たれます。比較には `is` を使います。

| アンチパターン | 推奨パターン |
|----------------|--------------|
| `_MISSING = object()` | `MISSING = sentinel("MISSING")` |

```python
MISSING = sentinel("MISSING")


def next_value(default: int | MISSING = MISSING) -> int:
    ...
```

- 型ヒントで `|` を使えます。
- 番兵値は、変数と同じ名前で作ります。pickle できるのは、モジュールのグローバルスコープに、番兵値の名前と同じ名前で置いたものと、クラススコープに、番兵値の修飾名（`Cls.NAME`）と同じ名前で置いたものです。関数の中で作ったものは pickle できません。
- `sentinel` はサブクラスにできません。

### 4. 既定のエンコーディングが UTF-8 に (PEP 686)

Python 3.15 の既定のエンコーディングは、システムの環境によらず UTF-8 です。`encoding` を指定しない `open("flying-circus.txt")` などの I/O が、UTF-8 になります。

ただし、Python の版をまたいで同じ動作にするため、`encoding` は常に明示してください。システムのロケールのエンコーディングが必要なときは、`encoding="locale"` を指定します。

| アンチパターン | 推奨パターン |
|----------------|--------------|
| `open("data.txt")` | `open("data.txt", encoding="utf-8")` |

以前の動作に戻すには、環境変数 `PYTHONUTF8=0` か `-X utf8=0` で、UTF-8 モードを無効にします。オプトインのエンコーディング警告を使うと、この変更の影響を受けるコードを見つけられます。

### 5. 内包表記でのアンパック (PEP 798)

リスト、集合、辞書の内包表記とジェネレータ式で、`*` と `**` によるアンパックを使えます。複数のイテラブルや辞書を 1 つにまとめるために、ネストした内包表記や `itertools.chain`、`itertools.chain.from_iterable` を使っていた箇所は、これに置き換えてください。

| アンチパターン | 推奨パターン |
|----------------|--------------|
| `[x for L in lists for x in L]` | `[*L for L in lists]` |
| `{k: v for d in dicts for k, v in d.items()}` | `{**d for d in dicts}` |

```python
lists = [[1, 2], [3, 4], [5]]
flat = [*L for L in lists]  # [1, 2, 3, 4, 5]

sets = [{1, 2}, {2, 3}, {3, 4}]
union = {*s for s in sets}  # {1, 2, 3, 4}

dicts = [{"a": 1}, {"b": 2}, {"a": 3}]
merged = {**d for d in dicts}  # {'a': 3, 'b': 2}
```

### 6. 型付けの新機能

- **`TypedDict` の `closed` / `extra_items` (PEP 728)**: `TypedDict` は既定では「開いて」いて、クラス本体で定義したキー以外も持てます。`closed=True` を指定すると、定義したキー以外を許しません。`extra_items` に型を指定すると、定義していないキーを、その型の値として許します。`extra_items` は `closed` と同時には使えません。

  ```python
  class ClosedPoint(TypedDict, closed=True):
      x: int
      y: int


  class ExtraItemsPoint(TypedDict, extra_items=int):
      x: int
      y: int


  point: ExtraItemsPoint = {"x": 1, "y": 2, "anything": 3}  # OK
  ```

- **`TypeForm` (PEP 747)**: 型式そのもの（`int`、`str | None`、`list[int]` など）を値として受け取る関数の引数に、`TypeForm[T]` で注釈します。実行時には `TypeForm(x)` は `x` をそのまま返します。

  ```python
  from typing import Any, TypeForm


  def cast[T](typ: TypeForm[T], value: Any) -> T: ...
  ```

### 7. プロファイリング (PEP 799)

組み込みのプロファイラは、新しい `profiling` パッケージにまとまりました。

- `profiling.tracing`: 決定的な関数呼び出しのトレースです。`cProfile` から移りました。`cProfile` は互換のために残ります。
- `profiling.sampling`: 統計的なサンプリングプロファイラ（Tachyon）です。実行中のプロセスを、コードの変更や再起動なしに、低いオーバーヘッドで調べられます。

```bash
python -m profiling.sampling run script.py
python -m profiling.sampling attach 12345   # 実行中のプロセスの PID
```

`profile` モジュールは非推奨で、Python 3.17 で削除される予定です（2026-10、What's New In Python 3.15 で確認）。`profiling.tracing` に移してください。

### 8. 削除された API と非推奨の API

状態と削除の時期は、Python 3.15 の時点のものです（2026-10、What's New In Python 3.15 で確認）。

| 対象 | 状態 | 対処 |
|------|------|------|
| `typing.ByteString`、`collections.abc.ByteString` | `__all__` から削除。インポートすると `DeprecationWarning`。Python 3.17 で削除予定 | 使わない |
| `NamedTuple("Point", x=int, y=int)`（キーワード引数の形式） | 未対応 | クラス形式、または関数形式 |
| `TypedDict("TD")`、`TypedDict("TD", None)`（フィールドなし） | 未対応 | `class TD(TypedDict): pass`、または `TypedDict("TD", {})` |
| `sre_compile`、`sre_constants`、`sre_parse` | 削除 | 使わない |
| `glob.glob0()`、`glob.glob1()` | 削除 | `glob.glob()` の `root_dir` 引数 |
| `pathlib.PurePath.is_reserved()` | 削除 | `os.path.isreserved()` |
| `importlib` の `Loader.load_module()` | 削除 | `exec_module()` |
| `profile` | 非推奨。Python 3.17 で削除予定 | `profiling.tracing` |
| `re.match()`、`re.Pattern.match()` | ソフト非推奨（削除の予定はない） | 新しいコードでは `re.prefixmatch()`、`re.Pattern.prefixmatch()` |
