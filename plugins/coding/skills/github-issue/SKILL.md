---
name: github-issue
description: gh issue のコマンドを実行する前に、必ず使用する。Issue を探す、読む、作る、コメントする、閉じる、PR と結びつけるとき、または GitHub に不慣れな利用者が Issue の書き方や扱いで迷ったときに使う。
license: MIT
---

# GitHub Issue の案内

## 操作の段階と前提

- 読み取り（`gh issue list`、`gh issue view`、`gh issue status`、`--search`、`gh label list`）はすぐ実行します。
- 書き込み（`gh issue create`、`comment`、`edit`、`close`、`reopen`）は他の人に見えるため、送り先のリポジトリと内容（タイトル、本文、変更項目）を示して確認を取ってから実行します。`delete`、`transfer`、`lock`、`pin` は使いません。
- リポジトリの規約（`.github/ISSUE_TEMPLATE/`、`CONTRIBUTING.md`、`AGENTS.md`、`docs/agents/`）があればそれに従います。
- 書き込みの前に `gh auth status` と送り先（`gh repo view --json nameWithOwner --jq .nameWithOwner`）を確かめます。未ログイン時の `gh auth login` は対話式のためコマンドを提示するだけにし、秘密が出る `gh auth token` や `--show-token` は使いません。

## 場面ごとの手順

### 探す、読む

- 検索は `gh issue list --search "<キーワード>" --state all` で閉じた Issue も含めて探します。
- `gh issue view <番号> --comments` はコメントだけを出し本文を出さないため、両方読むときは `gh issue view <番号>` も実行します。

### 作る

1. 既存の Issue を検索し、同じ話題があれば新規作成ではなく既存へのコメントを提案します。
2. テンプレートがあればそれに沿い、なければバグは「何が起きたか / 期待した動き / 再現手順 / 環境」、要望は「背景 / やりたいこと / 完了の条件」で下書きします。言語は既存の Issue に合わせます。
3. 下書きからトークン、パスワード、鍵などの認証情報を取り除き、送り先・タイトル・本文を示して確認を取ります。
4. 複数行の本文が崩れたり対話プロンプトで止まったりしないよう、一時ファイルを使って `gh issue create --title "<タイトル>" --body-file <ファイル>` で作成します。
5. 範囲が大きすぎるときは分割を提案します。`mattpocock-skills` が入っていれば `/mattpocock-skills:to-tickets` を案内し、入っていなければ手動で分けます。

### コメントする、閉じる、PR と結びつける

- コメントは下書きを示して確認を取り、`gh issue comment <番号> --body-file <ファイル>` で投稿します。
- 紐づく PR があり、PR のベースがデフォルトブランチなら、PR 本文の `Closes #番号`（または `Fixes`、`Resolves`）による自動クローズに任せます。デフォルトブランチ以外向けの PR や閉じない関連づけには `Refs #番号` を使います（PR 本文の作成は `github-pr` スキル）。
- PR なしで直接閉じるときは、確認を取って `gh issue close <番号> --reason "<種別>" --comment "<理由>"`（種別は `completed`、`"not planned"`、`duplicate`）を実行します。
- ラベル、担当、マイルストーン、プロジェクトは利用者が求めたときだけ設定し、ラベルは `gh label list` にあるものから選びます。メンテナーがラベルで状態を管理する場合、`mattpocock-skills` が入っていれば `/mattpocock-skills:triage` を使い、入っていなければ `docs/agents/triage-labels.md` などの規約に従って `gh issue edit` で付け替えます。
