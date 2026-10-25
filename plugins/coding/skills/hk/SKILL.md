---
name: hk
description: git フック（pre-commit・pre-push）の管理ツールとして hk を選ぶ方針と、husky・lint-staged・pre-commit・lefthook などからの移行手順を定めるスキル。git フックを新しく導入するとき、既存のフック管理ツールを hk に置き換えるとき、または hk の公式スキル（hk-configure、hk-debug）を入れるときに使用する。
license: MIT
---

# hk を選ぶ方針、移行、公式スキルの導入

git フックの管理には `hk`（設定ファイルは `hk.pkl`）を使い、`mise.toml` で版を管理します。

- `hk.pkl` の書き方は `hk-configure` スキル、フックの失敗やスキップの診断は `hk-debug` スキルに従います（入っていなければ下の「公式スキルの導入」で入れ、使えない場合は https://hk.jdx.dev/ を参照します）。

## 方針

- **ツールの定義**: `hk` とフックで使う linter・formatter は `mise.toml` に定義します（`pkl` CLI は不要。`hk` が Pkl 評価器を内蔵しています）。ただし Python の ruff・ty・pytest は `uv.lock`（`python-development` スキルを参照）、PowerShell の PSScriptAnalyzer・Pester は `psresources.psd1`（`powershell-development` スキルを参照）で固定します。
- **検証と修正の分離**: 検証は `hk check`（変更ファイルのみ、全ファイルは `--all`）、書き換えは `hk fix` に分けます。フック失敗時は `--no-verify` で飛ばさず、`hk check` / `hk fix` で直します。
- **フックの登録**: Git 2.54 以上では `hk install --global --mise`（`global` 層への書き込みのため、コマンドを利用者に提示するだけ。`mise` の絶対パスが記録されます）、古い Git やリポジトリ単位で入れる場合は `hk install --mise` を使います（リポジトリ単位の登録では Git 実行時の `PATH` に `mise` 本体が必要です）。`--mise` により、GUI クライアントなどシェルで mise を有効化していない環境でも mise 管理のツールが動きます。グローバル登録とリポジトリ単位登録は二重実行になるため併用しません（リポジトリ単位から切り替えるときは先に `hk uninstall` を実行します）。

## 公式スキルの導入

`mise use hk`（既定の `packslip:github.com/jdx/hk` バックエンド）で入れると、公式スキル `hk-configure` と `hk-debug` が一緒に取得されます。

1. `mise.toml` に次を書きます。
   ```toml
   [settings.skills]
   auto_sync = true
   prune = true
   ```
2. `.gitignore` にリンクと管理ファイルを追加します（プロジェクト固有のスキルを消さないよう、ディレクトリ全体ではなく名前で指定します。Antigravity CLI を使う人は各自の `mise.local.toml` 等で `skills.dir = ".agents/skills"` に合わせます）。
   ```gitignore
   .claude/skills/hk-configure
   .claude/skills/hk-debug
   .claude/skills/.mise-skills.json
   ```
3. `mise use hk`（導入済みなら `mise skills sync`）を実行してリンクを張ります。
   - `mise skills ls` に出ないときは、`mise.lock` に packslip 以外のバックエンドが記録されています。`mise backends switch -n hk` で確かめてから `mise backends switch hk` で切り替えます。

## 新規導入と既存ツールからの移行

1. 「公式スキルの導入」の 1〜3 を行い、`mise use hk` で `hk` を入れます。
2. `hk.pkl` を用意し、`hk validate` で検証します（`amends` / `import` の URL は `hk init` が生成した版をそのまま使います）。
   - 新規、または `husky`・`lint-staged`・`lefthook` からの移行: `hk init` で生成し、既存設定の処理をステップに移します。
   - `pre-commit`（`.pre-commit-config.yaml`）からの移行: `hk migrate pre-commit --output hk.migrated.pkl` で変換して確認します。Builtins にできないフックは `prek` または `pre-commit` ランナーのステップとして残るため、可能な限り hk のステップに書き換えます（残す場合は `.pre-commit-config.yaml` を残し、ランナーも `mise.toml` に定義します）。
   - hk v1（`hk.toml` / `hk.yaml` / `hk.json`）からの移行: `hk.pkl` に書き直し、`.hkrc.pkl` は `hk.local.pkl` に、`~/.hkrc.pkl` は `~/.config/hk/config.pkl` に移します。
3. 既存ツールのフック登録を外し（`pre-commit uninstall`、`lefthook uninstall`、husky の `core.hooksPath` は `git-config` スキルに従い `git config --unset core.hooksPath` を提示）、不要になった旧設定ファイルを削除します。Git 2.54 以上では `hk` が `.git/hooks/` を使わないため、旧フックを外さないと二重に動き続けます。
4. フックを登録し、`hk check --all` が通ることを確かめます。
