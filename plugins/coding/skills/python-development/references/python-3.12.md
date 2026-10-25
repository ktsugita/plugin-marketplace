# Python 3.12 開発ガイド

Python 3.12 環境を対象とするコード開発での構文と機能のガイドラインです。

## 設定

`pyproject.toml` の `requires-python` で対象バージョンを指定します（Ruff は `requires-python` から推論するため、`target-version` は書きません）。

```toml
[project]
requires-python = ">=3.12"
```

## 構文および機能の適用指針

### 1. 型パラメータ構文 (PEP 695)

ジェネリック関数、ジェネリッククラス、型エイリアスの定義には PEP 695 の型パラメータ構文を使用してください。
旧来の `TypeVar` や `Generic`、`TypeAlias` の明示的なインポートは不要です。

| 旧来の書き方（非推奨） | Python 3.12 推奨パターン |
|------------------------|--------------------------|
| `from typing import TypeVar, Generic`<br>`T = TypeVar("T")`<br>`def first(items: list[T]) -> T: ...` | `def first[T](items: list[T]) -> T: ...` |
| `class Stack(Generic[T]): ...` | `class Stack[T]: ...` |
| `from typing import TypeAlias`<br>`Point: TypeAlias = tuple[float, float]` | `type Point = tuple[float, float]` |

### 2. f-strings 構文制限の撤廃 (PEP 701)

f-strings 内の式で同じ引用符の再利用、複数行の式、バックスラッシュ文字、インラインコメントが記述可能になりました。
一時変数の定義や不自然なクォートの使い分けを避け、直接記述してください。

```python
# 内部でのダブルクォート再利用と辞書アクセス
summary = f"User: {user["name"]}, Roles: {", ".join(user["roles"])}"

# 式内部でのバックスラッシュや改行
formatted = f"Items:\n{
    "\n".join(item.strip() for item in items)
}"
```

### 3. メソッドオーバーライドの明示 (PEP 698)

基底クラスのメソッドをオーバーライドする際は、意図しないシグネチャ不整合やリファクタリング漏れを防ぐために `@override` デコレータを付与してください。

```python
from typing import override


class BaseService:

    def process(self, request_id: str) -> None:
        ...


class LoggingService(BaseService):

    @override
    def process(self, request_id: str) -> None:
        print(f"Processing: {request_id}")
        super().process(request_id)
```

### 4. シーケンスのバッチ処理 (`itertools.batched`)

シーケンスやイテラブルを固定長のチャンクに分割する処理には、自作ループやスライスではなく `itertools.batched` を使用してください。

```python
import itertools

records = [1, 2, 3, 4, 5, 6, 7]
for batch in itertools.batched(records, 3):
    # batch: (1, 2, 3), (4, 5, 6), (7,)
    process_batch(batch)
```
