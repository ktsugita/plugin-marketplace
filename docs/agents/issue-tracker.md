# Issue tracker: GitHub

このリポジトリの Issue と仕様は GitHub Issues で管理する。操作はすべて `gh` CLI で行う。

## 操作

- **Issue を作る**: `gh issue create --title "..." --body "..."`。本文が複数行のときは heredoc を使う。
- **Issue を読む**: `gh issue view <number> --comments`。コメントは `jq` で絞り込み、ラベルもあわせて取得する。
- **Issue を一覧する**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'`。必要に応じて `--label` と `--state` で絞り込む。
- **Issue にコメントする**: `gh issue comment <number> --body "..."`
- **ラベルを付ける・外す**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **閉じる**: `gh issue close <number> --comment "..."`

リポジトリは `git remote -v` から推測する。clone の中で実行すれば、`gh` が自動で判別する。

## PR を要望の受付口として扱うか

**PR を要望の受付口として扱う: no。** _(外部からの PR を機能要望として扱う場合は `yes` にする。`/triage` がこのフラグを読む。)_

`yes` にした場合、PR も Issue と同じラベルと状態で扱う。操作は `gh pr` の対応するコマンドを使う。

- **PR を読む**: `gh pr view <number> --comments`。差分は `gh pr diff <number>`。
- **トリアージ対象の外部 PR を一覧する**: `gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments` を実行し、`authorAssociation` が `CONTRIBUTOR`、`FIRST_TIME_CONTRIBUTOR`、`NONE` のものだけを残す(`OWNER`、`MEMBER`、`COLLABORATOR` は除く)。
- **コメント・ラベル・クローズ**: `gh pr comment`、`gh pr edit --add-label` / `--remove-label`、`gh pr close`。

GitHub は Issue と PR で番号を共有する。`#42` のように番号だけが書かれている場合は、どちらかを判別できない。まず `gh pr view 42` を試し、失敗したら `gh issue view 42` を使う。

## スキルが「Issue tracker に公開する」と言うとき

GitHub の Issue を作る。

## スキルが「該当するチケットを取得する」と言うとき

`gh issue view <number> --comments` を実行する。

## Wayfinding の操作

`/wayfinder` が使う。**マップ**は 1 つの Issue で、その配下の**子** Issue がチケットになる。

- **マップ**: ラベル `wayfinder:map` を付けた 1 つの Issue。本文に Notes / Decisions-so-far / Fog を置く。作成は `gh issue create --label wayfinder:map`。
- **子チケット**: GitHub のサブ Issue としてマップに紐づけた Issue(`gh api` でサブ Issue の endpoint を呼ぶ)。サブ Issue が有効でないときは、マップ本文のタスクリストに子を加え、子の本文の先頭に `Part of #<map>` と書く。ラベルは `wayfinder:<type>`(`research`、`prototype`、`grilling`、`task`)。着手したら、進める編集者を assignee にする。
- **ブロック関係**: GitHub 標準の **issue dependencies** を使う。UI で見える正式な表現である。ブロック関係の追加は `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`。`<blocker-db-id>` はブロックする側の数値の **database id** で、取得は `gh api repos/<owner>/<repo>/issues/<n> --jq .id`。`#number` と `node_id` は使えない。GitHub は `issue_dependencies_summary.blocked_by` を返す(未解決のブロッカーだけを数える。着手可否の判断に使う)。dependencies が使えないときは、子の本文の先頭に `Blocked by: #<n>, #<n>` の行を置く。すべてのブロッカーが閉じていれば、そのチケットは着手できる。
- **着手可能なチケットの検索**: マップの未クローズの子(`gh issue list --state open`。マップのサブ Issue またはタスクリストに限る)から、未解決のブロッカー(`issue_dependencies_summary.blocked_by > 0`、または `Blocked by` の行に未クローズの Issue がある)か assignee があるものを除く。残ったうち、マップの並びで先頭のものを選ぶ。
- **着手の宣言**: `gh issue edit <n> --add-assignee @me`。セッションで最初に行う書き込みにする。
- **解決**: `gh issue comment <n> --body "<answer>"` を実行し、`gh issue close <n>` で閉じる。そのうえで、マップの Decisions-so-far に文脈へのリンク(gist と URL)を追記する。
