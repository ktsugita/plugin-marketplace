---
name: git-config
description: Git の設定（`git config`、`.git/config`、`~/.gitconfig`、`user.name` や `user.email` など）を読む、書くときは、コマンドを実行する前に必ず使用する。設定が効かない理由の調査、推奨設定の確認、設定に起因する Git の失敗（`git pull` の `Need to specify how to reconcile divergent branches`、`Filename too long`、改行の差分、シンボリックリンク、認証、WSL との食い違い）にも使用する。
license: MIT
---

# Git の設定の読み書きと診断

- 推奨設定の確認、新しい環境の整備、要設定のキーに一致する症状（`git pull` が `Need to specify how to reconcile divergent branches` で失敗する、など）のときは、`references/recommended-settings.md` を読みます。
- Windows や WSL の Git の問題（`Filename too long`、改行の差分、シンボリックリンク、認証、環境の取り違え）のときは、`references/windows.md` を読みます。

## 層と実効値

- 読み込み順は `system`、`global`、`local`（`.git/config`）、`worktree`（`extensions.worktreeConfig` が有効なときのみ）、`command`（`GIT_CONFIG_COUNT` 系の環境変数または `git -c`）で、後ろの層が勝ちます。複数値のキーは全層の値が有効です。
- `global` 層には `$XDG_CONFIG_HOME/git/config`（未設定なら `~/.config/git/config`）と `~/.gitconfig` の2ファイルがあり、両方あれば両方を読み、同じキーは `~/.gitconfig` が勝ちます。`--global` を付けた読み書きは1ファイルだけを対象にします。

## 読む

見たいキーを決め、範囲指定（`--global` など）を付けずに名指しで引きます。全キーの列挙（`git config list`、`--list`、`--get-regexp '.*'`）は、`--name-only` を付けても使いません。`url.<base>.insteadOf` など、キー名自体にトークンが入りうるためです。設定ファイル（`.git/config`、`~/.gitconfig`、include 先）も、ファイル読み取りツールでは開かず `git config` 経由だけで読みます（`.gitattributes` は直接読んでかまいません）。

- 単一のキー: `git config --show-origin --show-scope --get-all <key>`（単一値のキーの実効値は最後の行）
- キーの集合: `git config --show-origin --show-scope --get-regexp '^(key1|key2)$'`（キー名は小文字）

次のキーは、名前・層・出所だけを確かめ、値は取得しません。値が必要なときは、利用者が自分で実行するコマンドを提示するだけにします。

- 対象: `remote.*.url`、`pushurl`、`url.*`、`http.*`、`credential.*`、`sendemail.*`、名前に `password`・`token`・`secret` を含むキー
- 問い合わせ: `git config --show-origin --show-scope --name-only --get-regexp '^sendemail\.smtppass$'`（`--name-only` は `--get-all` と併用不可）

秘密が露出するため、`GIT_TRACE*`、`GIT_CURL_VERBOSE`、`git credential fill`、`gh auth token`、`gh auth status --show-token`、認証情報を伏せない `git remote -v`、`env` / `printenv` の全出力は使いません（`GIT_CONFIG_*` は変数名の有無だけを確かめます）。

## 診断

設定が効かないときは、まず対象キーの実効値と出所を上のコマンドで引き、原因が分からなければ次の点を確認します。

- 層どうしの衝突（`system` 層の値を `global` 層が上書きしている、など）。
- `scope` が `command` なら、`GIT_CONFIG_*` 環境変数の有無。
- `include` と `includeIf` の条件（`gitdir:` は末尾に `/` が必要。linked worktree では本体の `.git` に対して照合される。`worktree:` 条件は 2.56.0 以降）。
- 呼ばれている Git の実体と設定ファイルの場所（`git version`、`type -a git` または `Get-Command git -All`、`git var GIT_CONFIG_GLOBAL`、`git var GIT_CONFIG_SYSTEM`）。利用者の問題環境（WSL、PowerShell など）がいまのシェルと違うときは、推測せずその環境で実行するコマンドを提示します。
- 改行の問題なら属性（`git check-attr -a <path>`、`git ls-files --eol`）。

層の影響を切り分けるときは、読み取り専用のコマンドに限り、`GIT_CONFIG_GLOBAL` を実在する空ファイルに、`GIT_CONFIG_NOSYSTEM=1` に差し替えて実行できます（Windows の不具合を避けるため `NUL` や `/dev/null` は指しません）。

原因を特定できなかったときは、「異常なし」と誤解されないよう、確かめた項目と確かめなかった項目（秘密保護のため引かなかったキーや別環境の項目）を分けて報告します。

## 書く

### 層の扱いと許可キー

- `global` 層と `system` 層への書き込み（`gh auth setup-git`、`hk install --global`、`git lfs install`、`git credential-manager configure` を含む）は実行せず、コマンドを提示するだけにします。`worktree` 層は使わず、`extensions.worktreeConfig` の有効化も提案しません。
- `local` 層に書き込んでよいのは、次のキーだけです。
  `user.name`、`user.email`、`core.autocrlf`、`core.eol`、`core.longpaths`、`pull.ff`、`pull.rebase`、`fetch.prune`、`push.autoSetupRemote`、`merge.conflictStyle`
- 上記以外のキーは、外部コマンドの実行や認証経路の変更につながるため、`local` 層でも実行せずコマンドを提示するだけにします（`commit.gpgSign`、`tag.gpgSign`、`gpg.*`、`user.signingkey`、`core.sshCommand`、`core.hooksPath`、`core.fsmonitor`、`alias.*`、`filter.*`、`credential.*`、`url.*`、`remote.*.url`、`http.*`、エディタ・ページャなど）。
- 署名の失敗（`gpg failed to sign the data` など）では、署名設定を外さずにエラーの原因を報告します。

### `local` 層に書く手順

1. 現在の実効値と出所を確かめます。別の層から値が来ているときは出所を示し、利用者が「このリポジトリだけ」と望んだときだけ `local` 層で上書きします。
2. 実行するコマンド（古い Git でも動く `git config --local <key> <value>` または `--unset`）と、元に戻すコマンドを示して利用者の確認を取ります。`--all` や `--unset-all` を伴う場合は消える行をすべて示します（複数値キーへの書き込みが終了コード 5 で失敗しても、勝手に `--all` に切り替えません）。
3. 実行後に同じ問い合わせで実効値を確かめ、上位の環境変数などで上書きされていれば報告します。

状態を変える Git 操作で、承認なしに `git -c` や `GIT_CONFIG_*` を使って設定や認証経路を上書きしません（`-c commit.gpgsign=false`、`-c core.hooksPath=...` など）。
