---
name: git
description: git の書き込み系コマンド（clone、switch、add、commit、push、pull、merge、reset、restore など）を実行する前に、必ず使用する。GitHub に不慣れな利用者が Git で迷ったり失敗したときにも使う。
argument-hint: "[start|commit|push|sync|undo|conflict|auth]"
license: MIT
---

# Git の基本の案内

Git の書き込み操作の安全基準と、GitHub 初学者が迷いやすい場面の手順を定めます。

## 操作の段階

基準は、作業ツリーの変更とコミットが保たれるかです。迷えば確認を取る側に倒します。

| 段階 | 操作 |
| :- | :- |
| すぐ実行する | `status`、`diff`、`log`、`show`、`branch`（一覧）、`remote`（名前だけ）、`reflog`、`gh auth status` |
| 説明してから実行する | `clone`、`fetch`、`pull --ff-only`、`switch`、`switch -c`、`add`、`commit`、`restore --staged`、`stash`（退避だけ）、`merge`（ローカルへの取り込み）、`revert` |
| 確認を取ってから実行する | 作業を失う・履歴を書き換える操作（`reset`、`restore <パス>`、`clean`、`rebase`、`commit --amend`、`branch -D`、`branch -f`、`stash drop` / `clear`、`merge --abort`、`rebase --abort`、`switch -f`）と、外に出る操作（`push`、`push --force-with-lease`） |

- 依頼が明確なときは、「すぐ実行する」「説明してから実行する」段階の操作を依頼の範囲で進めます。利用者が迷っている・エラーで止まっているときは、次の一手を1つずつ理由を添えて提案します。
- 「確認を取ってから実行する」操作は、実行するコマンド、変わること、戻せない範囲を示し、利用者の返事を待ってから実行します。
- `push --force` は使わず、履歴の書き換えが必要な理由を説明したうえで `--force-with-lease` で確認を取ります。

## 前提

- リポジトリの規約（`AGENTS.md`、`CONTRIBUTING.md`、`commit-msg` フック、`git log`）があればそれに従います。規約がなければ、コミットメッセージは日本語の Conventional Commits（`feat`、`fix`、`docs`、`refactor`、`test`、`chore`）にし、AI ツールの帰属行は付けません。
- 設定の読み書きと診断は `git-config` スキルに従います。対話式の `gh auth login` と `gh auth setup-git` は実行せず、コマンドを提示するだけにします。URL 内のトークンを避けるため、素の `git remote -v` や `gh auth token` は使いません。

## 呼び出しと場面ごとの手順

引数（動詞）があるときは対応する節に進み、ないときは現在の状態から判断します。

- `start`: 「始める」
- `commit`: 「変更を見て commit する」
- `push`: 「push する」
- `sync`: 「push が拒否された」
- `undo`: `references/undo.md`（`main` に直接 commit した場合は「`main` に直接 commit した」）
- `conflict`: `references/conflict.md`
- `auth`: 「認証のエラー」

### 始める

- 保存先のディレクトリを伝えて `git clone <URL>` を実行し、`main` に直接 commit しないよう `git switch -c <ブランチ名>` で作業ブランチを切ります（Issue があれば `12-fix-typo` のように番号を含めます）。

### 変更を見て commit する

1. `git status`、`git diff`、`git diff --staged` で変更内容を確かめます。
2. 対象ファイルを `git add <パス>` でステージします。`.env`、鍵、トークンを含むファイルや差分はステージせず、すでにステージ・コミットされていたら `references/undo.md` に従います。
3. 複数行や特殊文字のエスケープ漏れを防ぐため、必要なら `.git/COMMIT_EDITMSG.tmp` などの一時ファイルを使って `git commit -F <ファイル>` でコミットし、終了後に一時ファイルを削除します。フックに止められたときは出力を読んで原因を直します。

### push する

- 送り先のブランチと送るコミット（`git log --oneline @{upstream}..HEAD`、上流がなければ `git log --oneline -5`）を示して確認を取ります。上流が未設定の初回は `git push -u origin <ブランチ名>` を使います。

### `main` に直接 commit した、ブランチを切り忘れた

1. `git fetch` のあと、`git log --oneline origin/main..HEAD` で未 push のコミットを確かめます。すでに push 済みなら履歴を書き換えず、リポジトリの管理者に相談するよう案内します。
2. `git switch -c <新しいブランチ名>` でコミットを新しいブランチに移します。
3. コミットが新しいブランチに残ることを伝え、確認を取ってから `git branch -f main origin/main` で `main` を戻します。

### push が拒否された

- `non-fast-forward`（または `fetch first`）で拒否されたら、`git fetch` のあと `git log --oneline HEAD..origin/<ブランチ名>` でリモート側の差分を示し、`git pull --ff-only origin <ブランチ名>` を試みます（初回 push 時は上流が未設定のため `origin <ブランチ名>` を明示します）。
- `--ff-only` が失敗したら、`git merge origin/<ブランチ名>` で取り込みます。コンフリクトが出たら `references/conflict.md` を読みます。

### 認証のエラー

- `Authentication failed`、`could not read Username`、`Permission denied`、`403` が出たら、URL 全体を出さずにスキームだけを確かめます（bash: `git remote get-url origin | grep -o -E '^(https://|ssh://|git@)'`、PowerShell: `(git remote get-url origin) -replace '^(https://|ssh://|git@).*','$1'`）。
- `https://` なら `gh auth status` を確かめ、未ログインなら `gh auth login` と `gh auth setup-git` を提示します。ログイン済みで `403` なら書き込み権限がないため、権限の依頼またはフォークからの PR を案内します。
- SSH で `Permission denied (publickey)` なら、`ssh -T git@github.com` の結果を確認して鍵の登録を案内します。credential helper や WSL との食い違いは `git-config` スキルに従います。

## 他のスキルへの案内

- PR の作成・CI 確認・レビュー対応・マージは `github-pr`、Issue の操作は `github-issue`、`.github/workflows/` の編集は `github-actions`。
