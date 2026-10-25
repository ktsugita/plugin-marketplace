---
name: mise
description: mise で、Node.js・Ruby・Go などのランタイムと CLI ツールの管理、`mise.toml` のタスクの定義と実行、環境変数の設定を行うときに使用する。
license: MIT
---

# mise によるツール・タスク・環境変数管理

ランタイム管理、CLI ツール管理、タスクランナー、非秘密の環境変数管理は、プロジェクトルートの `mise.toml` に集約し、`mise.lock` で固定します。開発ツールは `npm install -g` や `cargo install` でグローバルに入れず、`mise use <tool>@<版>` でプロジェクトに定義します。

## 導入（未インストール時）

- macOS / Linux: `curl -fsSL https://mise.run | sh`
- Windows: `scoop install mise`（または `winget install jdx.mise`）

## タスク実行と定義の要点

- `<LTS の版>` などは書く時点の版を調べて指定します（`mise latest node@lts`、`mise latest go`、`mise ls-remote <tool>`）。
- 複数タスクの実行は `mise run lint ::: test` のように `:::` で区切ります。`mise run lint test` と書くと、`test` は `lint` タスクへの引数になります。`:::` で並べたタスクは並列に走りうるため、順序が必要な場合はタスク定義の `depends` を使います。
- `mise watch` には `watchexec` が必要です（`mise use -g watchexec@latest`）。

## ロックファイル（`mise.lock`）

`mise.lock` は解決した版、プラットフォームごとのダウンロード先、checksum、ツールのバックエンド（`aqua:`、`github:`、`packslip:` など）を記録します。`mise.lock` はリポジトリにコミットします。

```toml
[settings]
lockfile = true
lockfile_platforms = ["<手元のプラットフォーム>", "<CI の runner のプラットフォーム>"]
```

- `lockfile = true` が無いと、`mise install` や `mise use` は既存の `mise.lock` を読むだけで新しく作りません。
- `lockfile_platforms` には手元と CI runner の全プラットフォーム（`linux-x64`、`linux-arm64`、`macos-arm64`、`windows-x64` など）を明記します。プロジェクトの `mise.toml` に書かないとグローバル設定（`~/.config/mise/config.toml`）の `lockfile_platforms` が使われ、CI 用エントリが欠けて CI の `mise install --locked` が失敗することがあります。不足分は `mise lock --platform <platform>,...` で補えます。
- `minimum_release_age`（既定 `24h`）は公開直後の改ざんリリースを避ける設定です。短くするときは理由を確認してから設定します。
- 一度 `mise.lock` に記録されたバックエンドは、入れ直しても変わりません。`mise doctor` 等で推奨バックエンドとの不一致が出たときは、`[tool_alias]` で警告を消さず、`mise backends switch -n <tool>` で確かめてから `mise backends switch <tool>` で切り替えます。

## 他ツールとの連携

記載のスキルが使える場合はそれに従い、使えない場合は各公式ドキュメントを参照します。

- **Python (`python-development` スキル)**: `mise use uv` で `uv` を入れ、Python 本体とパッケージ・品質ツール（ruff、ty、pytest）は `uv` と `uv.lock` に任せます。
- **PowerShell (`powershell-development` スキル)**: `pwsh` は原則として OS 標準の方法で入れ、版を固定したいときだけ `[tools]` に `powershell = "<最新の LTS の major.minor>"` を書きます（`lts` は指定不可）。PSScriptAnalyzer と Pester は mise の `[tools]` に入れられないため、`[tasks.deps]` から `Install-PSResource` で入れ、`[hooks] postinstall` から呼びます。
- **Git フック (`hk` スキル)**: `mise use hk` で導入します（`pkl` CLI は不要）。
- **GitHub Actions (`github-actions` スキル)**: `jdx/mise-action` を使います。キャッシュは既定で有効であり、`mise.lock` があれば自動で `mise install --locked` が走ります。
