---
name: hk
description: git フック（pre-commit・pre-push）の管理ツールとして hk を選ぶ方針と、husky・lint-staged・pre-commit・lefthook などからの移行手順を定めるスキル。git フックを新しく導入するとき、既存のフック管理ツールを hk に置き換えるとき、または hk の公式スキル（hk-configure、hk-debug）を入れるときに使用する。
license: MIT
---

# hk を選ぶ方針、移行、公式スキルの導入

hk は jdx 製の git フック管理ツールで、フックで動かすチェックを `hk.pkl`（Pkl）に書きます。git フックの管理には `hk` を使います。`husky`、`lint-staged`、`pre-commit`（Python のツール）、`lefthook`、`.git/hooks` への直接記述は使いません。

このスキルが扱うのは、hk を選ぶ方針、他のツールからの移行、hk の公式スキルの導入です。`hk.pkl` の書き方と、フックの失敗の診断は扱いません。

**提示だけ**は `git-config` と同じ意味です（コマンドを実行せず、利用者に示すだけにすること）。

- hk の公式スキル `hk-configure`（設定の書き方）と `hk-debug`（フックの失敗や、ステップが意図せずスキップされたときの診断）が使える場合は、それに従う。入っていなければ、「公式スキルの導入」に従って入れる。
- 使えない場合は、hk の公式ドキュメント（https://hk.jdx.dev/）を参照する。

## 方針

| 方針 | 理由 |
|---|---|
| hk は mise で導入し、`mise.toml` に書く | Node.js や Python に依存せず、プロジェクトごとに同じ版を再現できるため。 |
| フックで使う linter や formatter も `mise.toml` に定義する（Python と PowerShell のツールは例外。「Python と PowerShell のツール」を参照） | CI や別の環境でツールが見つからずにフックが失敗するのを防ぐため。 |
| hk の公式スキルは、プロジェクトの `mise.toml` で `skills.auto_sync` と `skills.prune` を有効にしてリンクする | 公式スキルは hk の版ごとに取得され、hk を上げるとリンク先が変わるため。`auto_sync` があれば、hk を入れたり上げたりするたびに mise がリンクを張り直す。`prune` があれば、版が変わって無くなったスキルのリンクが残らない。 |
| フックは Git 2.54 以上では `hk install --global --mise` で登録する（global 層への書き込みなので、提示だけ）。Git が古い場合や、リポジトリ単位で入れる理由がある場合は `hk install --mise` で登録する | `--global` はマシンごとに一度で済み、hk の設定が無いリポジトリでは何もしないため。`--mise` は、フックを `mise x` 経由で動かし、シェルで mise を activate していない環境（GUI の Git クライアントなど）でも mise 管理のツールを見つけられるようにするため。 |
| 検証は `check`、書き換えは `fix` に分ける | `hk check` が既定ではファイルを書き換えず、意図しない差分がコミットに混ざらないようにするため。 |
| `--no-verify` を常用しない。フックが失敗したら `hk check` / `hk fix` で直してからコミットする | フックを通らない変更がコミットに混ざり、問題が CI や他の人の環境で初めて見つかるため。 |

mise の導入と `mise.toml` の書き方は、`mise` スキルが使える場合はそれに従います。使えない場合は mise の公式ドキュメント（https://mise.jdx.dev/）を参照します。

## Python と PowerShell のツール

- Python の ruff、ty、pytest は、uv の dev 依存に入れ、`uv.lock` で固定します。呼び出し方は、`python-development` スキルが使える場合はその「mise と hk との連携」に従います。使えない場合は hk の公式ドキュメント（https://hk.jdx.dev/）の `prefix` の説明を参照します。
- PowerShell の PSScriptAnalyzer と Pester は、hk の Builtins が無いので、ステップを自分で書き、`pwsh -File` のラッパーを呼びます。`pwsh` は OS の標準的な方法で入れ、2つのモジュールは宣言ファイルで固定します。呼び出し方は、`powershell-development` スキルが使える場合はその `references/toolchain.md` に従います。使えない場合は hk の公式ドキュメントを参照します。

## 新規導入

```bash
# 1. 公式スキルをリンクする設定を mise.toml に書き、.gitignore にリンクを加える（「公式スキルの導入」を参照）

# 2. hk を導入する（pkl CLI は不要。hk は Pkl の評価器を内蔵している）。公式スキルもリンクされる
mise use hk

# 3. プロジェクトのファイルから使われているツールを検出し、hk.pkl を生成する
hk init

# 4. 設定を検証する
hk validate

# 5. git フックとして登録する（Git 2.54 以上。提示だけ）
hk install --global --mise

# 6. 全ファイルに対して動作を確かめる
hk check --all
```

- `hk.pkl` の `amends` / `import` にある `Config.pkl` などの URL は、`hk init` が生成したものをそのまま使う。生成される URL は導入した hk の版に合っている。
- `hk install --global --mise` は `~/.gitconfig` に、マシンごとに一度だけ登録する。登録のときに mise の場所を記録するので、Git の実行時の `PATH` に mise が無くても動く。すでにグローバルに登録してあれば、手順 5 は不要。
- global 層への書き込みは、`git-config` スキルが使える場合はその規則に従い、提示だけにして、利用者に実行してもらう。使えない場合も同じ。
- Git が 2.54 より古い場合や、リポジトリ単位で入れる場合は、手順 5 で `hk install --mise` を使う。こちらは Git の実行時の `PATH` に mise が必要。リポジトリ単位の `hk install --mise` は、この手順のとおり実行してよい。local 層に `hook.*.command` が書かれる。
- グローバルとリポジトリ単位を併用しない（フックが二重に動く）。グローバルに登録してあると、`hk install` はリポジトリ単位の登録を飛ばす。リポジトリ単位からグローバルに切り替えるには、リポジトリで `hk uninstall` を実行してから、`hk install --global --mise` を提示だけにする。
- `hk check` と `hk fix` は、引数が無ければ変更のあるファイルだけを対象にする。全ファイルを対象にするには `--all` を付ける。

## 公式スキルの導入

hk を mise の packslip のバックエンド（`packslip:github.com/jdx/hk`。`mise use hk` の既定）で入れると、公式スキル `hk-configure` と `hk-debug` が hk の版ごとに一緒に取得されます。取得されたスキルは `mise skills ls` で確かめられます。これをハーネスが読むディレクトリにリンクします。

1. プロジェクトの `mise.toml` に次を書く。

   ```toml
   [settings.skills]
   auto_sync = true
   prune = true
   ```

2. `.gitignore` に、リンクと、mise がリンクの状態を記録するファイルを加える。リンクは各自の mise のインストール先を指すので、コミットすると他の環境では壊れる。プロジェクトスキルを置くリポジトリもあるので、ディレクトリごとではなく名前で除外する。

   ```
   .claude/skills/hk-configure
   .claude/skills/hk-debug
   .claude/skills/.mise-skills.json
   ```

3. hk を入れる（`mise use hk`、または `mise install`）。`auto_sync` により、hk が入ったときに `.claude/skills` にリンクされる。hk を上げたときも張り直される。

- hk がすでに手元に入っていて何もインストールされなかったとき（別のプロジェクトで同じ版を入れていた場合など）は、リンクされない。リンクが無ければ `mise skills sync` を一度実行する。すでに hk を使っているプロジェクトに公式スキルを入れるときも、手順 1 と 2 のあとに `mise skills sync` を実行する。
- `mise skills ls` に公式スキルが出ないときは、hk が packslip 以外のバックエンドで `mise.lock` に記録されている。`mise.lock` は記録したバックエンドを保つので、入れ直しても `mise skills sync` を実行しても packslip には変わらない。`mise backends switch -n hk` で切り替わる内容を確かめてから、`mise backends switch hk` で packslip に切り替える（`mise.lock` を書き換え、hk を入れ直す）。
- Claude Code と GitHub Copilot CLI は `.claude/skills` を読む。Antigravity CLI を使う場合は、リンク先がハーネスによって人ごとに違うので、プロジェクトの `mise.toml` ではなく、各自の `mise.local.toml` かグローバルの設定で `skills.dir = ".agents/skills"` にする。`.gitignore` には、そのディレクトリで同じ名前を除外する。

mise の `[settings.skills]` の詳細は、mise の公式ドキュメント（https://mise.jdx.dev/dev-tools/packslip-resources.html）を参照します。

## 既存ツールからの移行

1. 「公式スキルの導入」の手順 1 と 2 を行ってから、`mise use hk` で hk を導入する。
2. `hk.pkl` を作る。
   - `pre-commit`（`.pre-commit-config.yaml`）からは、`hk migrate pre-commit --output hk.migrated.pkl` で変換し、内容を確かめてから `hk.pkl` にする。hk の builtin にできないフックは、元の `.pre-commit-config.yaml` を読んで prek か pre-commit で実行するステップとして残る（どちらを使うかは `--runner prek|pre-commit` で選ぶ）。そのようなステップは、できるだけ hk のステップに書き換える。
   - `husky`、`lint-staged`、`lefthook` には変換コマンドが無い。`hk init` で `hk.pkl` を生成し、既存の設定にある処理を1つずつステップに移す。
   - hk v1 の `hk.toml`、`hk.yaml`、`hk.yml`、`hk.json` は hk v2 で読めなくなった。`hk.pkl` に書き直す。プロジェクトの `.hkrc.pkl` は `hk.local.pkl` に、ホームの `~/.hkrc.pkl` は `~/.config/hk/config.pkl` に移す（2026-10、hk 2.5.0 の移行ガイドで確認）。
3. `hk validate` で設定を検証する。
4. 既存のツールが登録したフックを外す（`pre-commit uninstall`、`lefthook uninstall`。husky が設定した `core.hooksPath` は `git config --unset core.hooksPath`。外部コマンドを実行させるキーなので、利用者に示して実行してもらう。`git-config` スキルが使える場合はその規則に従う）。hk は Git 2.54 以上では `.git/hooks/` を使わないため、外さないと古いフックが並んで動き続ける。
5. 既存の設定を削除する（`.husky/`、`.pre-commit-config.yaml`、lefthook の設定ファイル（`lefthook.yml`、`.lefthook.yml`、`lefthook-local.yml` など）、`package.json` の `lint-staged` の設定と `prepare` スクリプトなど）。ただし、`hk.pkl` に prek か pre-commit で実行するステップが残っている場合は、`.pre-commit-config.yaml` を消さず、そのツールも `mise.toml` に定義する。
6. 「新規導入」の手順 5 でフックを登録する（提示だけ）。
7. `hk check --all` を実行し、移行前と同じ検証が通ることを確かめる。

移行前のコマンドとの対応は次のとおりです。

| やりたいこと | 移行前 | hk |
|---|---|---|
| フックの登録 | `npx husky init`、`pre-commit install` | 「新規導入」の手順 5 |
| フックの解除 | `pre-commit uninstall` | `hk uninstall`（グローバルの登録は `hk uninstall --global`。マシンのすべてのリポジトリから外れるので、提示だけ） |
| 全ファイルへのフックの実行 | `pre-commit run --all-files` | `hk run pre-commit --all`（検証だけなら `hk check --all`） |
| 全ファイルの自動修正 | `npx prettier --write .` など | `hk fix --all` |
| ステージしたファイルに対するフックの手動実行 | `npx lint-staged` | `hk run pre-commit` |
