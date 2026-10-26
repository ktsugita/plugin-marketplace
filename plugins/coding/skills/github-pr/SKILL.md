---
name: github-pr
description: gh pr のコマンドを実行する前に、必ず使用する。PR を出す、CI の結果を見る、CI の失敗を読む、レビューの指摘に対応する、ベースの変更を取り込む、マージするとき、または GitHub に不慣れな利用者が PR の流れで迷ったときに使う。
argument-hint: "[create|feedback|response|close] [PR番号]"
license: MIT
---

# GitHub Pull Request の案内

## 操作の段階と前提

| 段階 | 操作 |
| :- | :- |
| すぐ実行する | `gh pr list` / `view` / `status` / `diff` / `checks`、`gh run view --log-failed`、`gh repo view`、レビュー指摘の読み取り（`gh api` の GET と GraphQL の query） |
| 説明してから実行する | `gh pr checkout` |
| 確認を取ってから実行する | `gh pr create`（`--draft` を含む）、`comment`、`review`、`edit`、`ready`、`update-branch`、`merge`（`--auto` を含む）、`close`、`reopen`、`revert`、`gh run rerun`、スレッドへの返信と Resolve |

- 確認では、送り先のリポジトリと操作の内容（タイトルと本文、ベースとヘッド、マージ方法など）を示します。
- リポジトリの規約（PR テンプレート、`CONTRIBUTING.md`、`AGENTS.md`）を先に確かめます。PR テンプレートは `git ls-tree -r --name-only origin/<ベース> | grep -i -E '(^|/)pull_request_template(\.md|/)'` で探します。
- 書き込み前に `gh auth status` と送り先（`gh repo view --json nameWithOwner --jq .nameWithOwner`）を確かめます。対話式の `gh auth login` は提示だけにし、`gh auth token` や `--show-token` は使いません。

## 呼び出しと場面ごとの手順

引数があるときは対応する節に進み、PR 番号が省略されたときは今のブランチの PR（`gh pr view --json number --jq .number`）を対象にします。

- `create`: 「PR を作る」
- `feedback`: `gh pr checks <番号>`（落ちていれば `references/ci-failure.md`）と `references/review-response.md` の「1. 指摘を集める」を読み取りだけで実行し、一覧にする
- `response`: `references/review-response.md` の「2. 一覧にして、1つずつ直す」から「3. 返信と Resolve」まで進める
- `close`: 「マージしたあと」（未マージなら削除せず「マージする」を提案する）

### PR を作る

1. 今のブランチがベース（`gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`）でないことと、ベースより先のコミット（`git log --oneline <ベース>..HEAD`）があることを確かめます。未 push なら `git` スキルの手順で push します。
2. 本文を下書きします。リポジトリに PR テンプレートがあればそれを使い、なければ `mattpocock-skills:pr` が入っているときはそのテンプレートで書きます。入っていないときは「概要 / 変更点 / 確認方法 / 関連 Issue（あれば）」の4項目で書きます。デフォルトブランチ向けで関連 Issue があれば `Closes #番号` を添えます（`github-issue` スキルを参照）。
3. 送り先、ベースとヘッド、タイトル、本文を示して確認を取り、一時ファイルを使って `gh pr create --title "<タイトル>" --body-file <ファイル> --base <ベース>` で作ります（利用者が下書きを求めたときだけ `--draft` を付けます）。

### ベースの変更を取り込む

`gh pr view <番号> --json mergeStateStatus,mergeable,baseRefName` で状態を確かめます。

- `BEHIND`: 確認を取って `gh pr update-branch <番号>` を実行し、手元は `git pull --ff-only origin <ブランチ名>` で追いつきます。
- `DIRTY`: 手元をその PR のブランチにし、`git fetch origin <ベース>` と `git merge origin/<ベース>` でコンフリクトを出してから、`git` スキルの `references/conflict.md` に従います。

### マージする

1. `gh pr view <番号> --json state,isDraft,reviewDecision,mergeStateStatus` と `gh pr checks <番号>` で、ドラフトでないこと、CI が通っていること、必要な承認があることを確かめます。
2. `gh repo view --json squashMergeAllowed,mergeCommitAllowed,rebaseMergeAllowed` で許可されたマージ方法を確かめ、確認を取って `gh pr merge <番号> --squash` などを実行します（`--admin` は使いません）。

### マージしたあと

1. `git switch <ベース>` と `git pull --ff-only` でベースを最新にし、`git fetch --prune` で参照を整えます。
2. squash マージしたブランチは `git branch -d` が拒否します。`git branch -D` は未 push の commit を失うため、`gh pr view <番号> --json state,headRefOid` で `MERGED` と PR の最終 commit を取り、ローカルブランチの先頭（`git rev-parse <ブランチ名>`）と一致するときだけ、確認なしで `git branch -D <ブランチ名>` を実行します。一致しないときは未 push の commit があるので、内容を示して確認を取ります。リモートブランチの削除はリポジトリの自動削除設定に任せ、このスキルでは行いません。

## 他のスキルへの案内

- ブランチ・commit・push・コンフリクト解消は `git`、Issue は `github-issue`、`.github/workflows/` の不具合は `github-actions`、認証設定は `git-config`、Copilot レビューの日本語化は `setup-github-repo`。
