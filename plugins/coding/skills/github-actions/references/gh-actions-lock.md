# gh-actions-lock の詳細

`SKILL.md` の原則3から参照される補足です。ロックファイルの対象外や版の制約を確かめるとき、CI に検証を組み込むときに読みます。コマンドの全体と findings の読み方は、公式スキル(`gh skill install github/gh-actions-lock`)に従います。

## ロックファイルの対象外

次のものは `actions.lock` に記録されません。

- ローカルの `./…` アクションと、その依存。同じリポジトリのアクションを固定したいときは、`gh actions-lock --migrate-local-actions` で `$/…` に書き換えます。
- 別のリポジトリの再利用可能ワークフロー(`jobs.<id>.uses`)。
- コンテナイメージ。`@sha256:` の digest がないものは、警告として報告されます。
- 浮動する参照(`main` や `v4`)が、履歴上の古い commit に固定されていても検出されません。ロックファイルの差分を見るか、完全なタグを指定します。

## 対応する環境と版

- github.com と、データ所在地指定の GitHub Enterprise Cloud(`*.ghe.com`)に対応しています。GitHub Enterprise Server には対応していません。
- gh-actions-lock は 1.0 より前の版で、フラグや挙動が変わりえます。迷ったときは `gh actions-lock --help` を正とします。

## 部分バージョンの書き換え

`gh actions-lock` は、初回の固定時に `uses:` の部分バージョン(`v4`)を、最も新しい完全なタグ(`v4.2.1`)へ書き換えます。書いたとおりに残すときは `--no-narrow` を付けます。2回目以降の実行で `uses:` を書き換えるかは、確認できていません。

## CI への組み込み

公式の [`verify-lockfile.yml`](https://github.com/github/gh-actions-lock/blob/main/.github/workflows/verify-lockfile.yml) を取り込み、次の点を直します。

- 実ファイルには `schedule:` がありません。タグの付け替えを検知するために、`on:` に `schedule:` を足します。
- 実ファイルは拡張を `--pin` で固定しています。最新の版に合わせます。
- 取り込んだあとに `gh actions-lock` を一度実行し、このワークフロー自身もロックファイルに記録します。
- `GITHUB_TOKEN` で読めるのは、公開アクションと、そのリポジトリ自身です。他の非公開リポジトリや内部リポジトリのアクションを使うときは、それを読めるトークンを渡します。

## Dependabot との関係

ロックファイルを導入済みのワークフローでは、Dependabot が同じ PR で `actions.lock` の該当エントリを再生成します。導入前のワークフローには触りません。再生成に失敗したときの PR 上の挙動は、確認できていません。`cooldown` は gh-actions-lock が `fresh-tag` の通知にだけ使い、固定を止めることはありません。
