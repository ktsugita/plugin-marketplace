# レビューの指摘への対応

レビューの指摘が来たときに読みます。指摘を一覧にして、1つずつ直し、対応したスレッドに返信して Resolve します。返信と Resolve（スレッドを「解決済み」にする操作）は、未解決のスレッドを目立たせるために行います。

## 1. 指摘を集める（すぐ実行）

PR の本文は `gh pr view <番号>`、PR 全体へのコメントとレビュー全体の要約は `gh pr view <番号> --comments` で読みます（`--comments` はコメントだけを出すので、両方を実行します）。インラインのレビュー指摘は `--comments` に出ないので、スレッド単位で取ります。`<owner>`、`<repo>`、`<番号>` を置き換えます。

```sh
gh api graphql --paginate -f query='query($endCursor:String){repository(owner:"<owner>",name:"<repo>"){pullRequest(number:<番号>){reviewThreads(first:50,after:$endCursor){pageInfo{hasNextPage endCursor}nodes{id isResolved comments(first:20){nodes{databaseId path line body author{login}}}}}}}}'
```

- `--paginate` と `pageInfo`、`after:$endCursor` で、全ページを取ります（50 件を超えるスレッドも漏れません）。
- `isResolved` が `false` のスレッドが対象です。
- スレッドの `id` が Resolve に、最初のコメントの `databaseId` が返信に使う番号です。

## 2. 一覧にして、1つずつ直す

1. 指摘を「修正が要る / 質問 / 提案」に分け、スレッドごとに1行で一覧にします。
2. 指摘が正しいかを、コードや公式の文書で確かめます。正しければ直し、正しくなければ、理由を添えて返信の下書きにします。
3. 最初の1つの対応を提案します。直したら `commit` します（`git`）。すべて直したら、まとめて `push` します（確認を取る）。

## 3. 返信と Resolve（push のあと）

1. スレッドごとに返信を下書きし、「スレッド、返信文、Resolve するか」の一覧にして見せ、**一括で確認を取ります**。
2. 確認が取れたら、返信してから Resolve します。

```sh
# 返信（<databaseId> は最初のコメントの番号）
gh api --method POST repos/<owner>/<repo>/pulls/<番号>/comments/<databaseId>/replies -f body="<返信文>"

# Resolve（<id> はスレッドの id）
gh api graphql -f query='mutation{resolveReviewThread(input:{threadId:"<id>"}){thread{isResolved}}}'
```

3. Resolve するのは、対応を push したスレッドだけです。質問への回答待ち、見送った提案、対応していないものは、Resolve せずに残します。
4. 直したスレッドの返信には、コミットの短い SHA と直した内容を書きます（認証情報や個人情報は除きます）。
