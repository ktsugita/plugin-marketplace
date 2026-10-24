---
name: mise
description: mise で、Node.js・Ruby・Go などのランタイムと CLI ツールの管理、`mise.toml` のタスクの定義と実行、環境変数の設定を行うときに使用する。
license: MIT
---

ランタイム管理、CLIツール管理、タスクランナー、環境変数管理には常に `mise` を使ってください。`nvm`、`rbenv`、`asdf`、`direnv`、`make` などの個別ツールではなく `mise` で一元管理します。

## miseがインストールされていない場合

まず以下でインストールしてください：

```bash
# macOS / Linux
curl -fsSL https://mise.run | sh

# Windows（Scoop を推奨）
scoop install mise
# Scoop を使わない場合は winget
# winget install jdx.mise
```

## コマンドリファレンス

### ランタイム・ツール管理

| やりたいこと | 従来のコマンド | mise コマンド |
|---|---|---|
| プロジェクトにツールを追加・バージョン固定 | `nvm use <版>`, `asdf set node <版>` | `mise use node@<版>` |
| グローバルにツールをインストール | `nvm install <版>`, `asdf set --home ruby <版>` | `mise use -g ruby@<版>` |
| 設定ファイルから一括インストール | `asdf install` | `mise install` |
| インストール済み・有効なツール一覧確認 | `nvm ls`, `asdf current` | `mise ls`, `mise ls --current` |
| ワンショット実行（一時実行） | `npx <tool>`, `cargo run --` | `mise x <tool> -- <command>` |

### タスクランナー

| やりたいこと | 従来のコマンド | mise コマンド |
|---|---|---|
| 定義済みタスクの実行 | `npm run <task>`, `make <task>` | `mise run <task>` (短縮: `mise r <task>`) |
| 複数タスクの実行 | `npm run lint && npm run test` | `mise run lint ::: test` |
| タスク一覧の表示 | `make help`, `npm run` | `mise tasks` (短縮: `mise t`) |
| ファイル変更監視とタスク再実行 | `nodemon`, `chokidar-cli` | `mise watch <task>` |

※ `mise watch` には `watchexec` が必要です（`mise use -g watchexec@latest` で入れる）。

※ `npm install -g <cli>` や `cargo install <cli>` で開発ツールをグローバル導入せず、`mise use <tool>@latest` で `mise.toml` に定義し、解決した版を `mise.lock` で固定します（「ロックファイル」を参照）。チームメンバーや CI と、版とツール構成を再現できるためです。

※ `mise run lint test` と書くと、`test` は `lint` タスクへの引数になります。複数のタスクは `:::` で区切ります。`:::` で並べたタスクは並列に実行されることがあるため、順序が必要な場合は `depends` で定義します。

### 環境変数・設定管理

| やりたいこと | 従来のコマンド | mise コマンド |
|---|---|---|
| 環境変数の設定 | `export KEY=val` (direnv) | `mise set KEY=val` |
| 有効な環境変数の確認 | `env`, `direnv status` | `mise env` |
| 設定ファイルの信頼 | `direnv allow` | `mise trust` |

※ 通常は `mise run` や `mise install` が設定ファイルを自動で信頼します。`mise trust` は、`[env]` やテンプレートを含む設定で信頼を求められたときに使います。

## `mise.toml` の構成例

プロジェクトルートの `mise.toml` にツール、環境変数、タスクを宣言的に定義します。

```toml
[tools]
node = "<LTS の版>"
ruby = "<版>"
go = "<版>"
uv = "latest"
jactionlint = "latest"
hk = "latest"

[env]
DATABASE_URL = "postgres://localhost/mydb"
NODE_ENV = "development"
# 既存の .env ファイルをインポートする場合
_.file = ".env"

[tasks.build]
run = "npm run build"
description = "プロジェクトをビルドする"
sources = ["src/**/*.ts"]
outputs = ["dist/**/*.js"]

[tasks.lint]
run = "eslint src/"
description = "コードのリントを実行する"

[tasks.test]
run = "jest"
description = "テストを実行する"
depends = ["build"]

[tasks.ci]
description = "CI用タスク（ビルド・リント・テストを実行）"
depends = ["lint", "test"]
```

`<LTS の版>` や `<版>` には、書く時点の版を調べて入れます。

```bash
mise latest node@lts   # Node.js の最新の LTS
mise latest go         # 最新の安定版
mise ls-remote ruby    # 利用できる版の一覧
```

## ロックファイル

`mise.lock` は、`mise.toml` の `latest` などの指定を解決した版と、プラットフォームごとのダウンロード先と checksum を記録します。`mise.lock` はコミットします。

```toml
[settings]
lockfile = true
lockfile_platforms = ["<手元のプラットフォーム>", "<CI の runner のプラットフォーム>"]
```

- `lockfile = true` にすると、`mise install` や `mise use` が `mise.lock` を作って更新します。指定しない場合は、既存の `mise.lock` を読むだけで新しくは作りません。
- `lockfile_platforms` には、手元と CI の runner のプラットフォーム（`linux-x64`、`linux-arm64`、`macos-arm64`、`windows-x64` など）をすべて列挙します。指定しない場合は、musl と macOS を含むよく使う7つのプラットフォームと、今のプラットフォームが対象になります。
- エントリの足りないプラットフォームは、`mise lock --platform <プラットフォーム>,...` で補います。
- `minimum_release_age` は、公開から一定の時間が経っていない版を `latest` などの解決の対象から外し、改ざんされたリリースを避けるための設定です。既定は `24h` です。短くする場合は、その理由を持ってから設定します。
- `mise.lock` はツールのバックエンド（`aqua:`、`github:` など）も記録します。ロックしたツールは、ロックしたときのバックエンドから変わりません。入れ直しても変わりません。
- `mise doctor` などが、ツールのバックエンドが registry の推奨と違うと指摘した場合は、`mise backends switch -n <tool>` で切り替わる内容を確かめてから、`mise backends switch <tool>`（例: `mise backends switch hk`）で切り替えます。`mise.lock` のエントリを registry のバックエンドに書き換え、同じ版で lock し直し、入れ直します。`[tool_alias]` で警告だけを消さないでください。

※ グローバルの設定（`~/.config/mise/config.toml`）にも `lockfile_platforms` を書けます。プロジェクトの `mise.toml` に `lockfile_platforms` が無いと、グローバルの設定が使われ、`mise.lock` に CI の runner のプラットフォームのエントリが作られないことがあります。`mise.lock` を作る前に、`mise settings ls` でどの設定ファイルの値が効いているかを確かめ、プロジェクトの `mise.toml` に書いてください。

## 他ツールとの連携

各項の詳細は、記載のスキルが使える場合はそれに従います。使えない場合は、記載の公式ドキュメントを参照します。

### Python との連携

- `mise use uv` で `uv` を導入する
- Python ランタイム本体の取得（`uv python install`）やパッケージ管理（`uv add` / `uv sync`）は `uv` に任せる
- 詳細は `python-development` スキル（公式: https://docs.astral.sh/uv/）

### PowerShell との連携

- `pwsh` 本体は OS の標準的な方法（Windows は winget、Ubuntu は Microsoft のパッケージリポジトリからの apt）で入れる。手元、フック、CI で版を固定したいときだけ、`[tools]` に `powershell = "<最新の LTS の major.minor>"` を書き、`mise.lock` で固定する（`lts` は指定できず、`latest` は将来 LTS でない系列に動きうる）
- PSScriptAnalyzer と Pester は mise の `[tools]` に入れられない（PSGallery のバックエンドが無い）。`[tasks]` の `deps` から `Install-PSResource` で導入し、`[hooks]` の `postinstall` から呼ぶ
- 詳細は `powershell-development` スキル（公式: https://learn.microsoft.com/powershell/）

### Git フック（hk）との連携

- `mise use hk` で `hk` を導入する（`pkl` は不要）
- `mise.toml` の `[tasks]` に `lint` や `test` を定義し、`hk.pkl` のステップから `mise run <task>` を呼び出す
- Python の ruff と ty は mise タスクにせず、`hk.pkl` を正本にする。詳細は `python-development` スキルの「mise と hk との連携」
- 導入や移行の方針は `hk` スキル（公式: https://hk.jdx.dev/）

### GitHub Actions (CI) との連携

- CI 上では `jdx/mise-action` を利用して `mise.toml` に記述されたツールを一括セットアップする

```yaml
- uses: jdx/mise-action@<commit-sha> # vX.Y.Z
```

- キャッシュは既定で有効なので、`cache: true` の指定は不要。
- `mise.lock` があると、`mise-action` は自動で `mise install --locked` を実行する。runner のプラットフォームのエントリが `mise.lock` に無いと、インストールが失敗する。CI の runner のプラットフォームを `lockfile_platforms` に入れておく（上の「ロックファイル」を参照）。
- SHA の調べ方と、action のピン留め・更新の運用は `github-actions` スキル（公式: https://docs.github.com/en/actions/reference/security/secure-use）
