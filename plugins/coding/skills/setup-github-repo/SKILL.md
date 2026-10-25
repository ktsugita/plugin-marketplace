---
name: setup-github-repo
description: GitHub リポジトリの初期設定(Copilot のレビューを日本語にする指示、マージ設定、Dependabot、デフォルトブランチのルールセット)を整えるとき、`gh repo create` や設定を書き込むコマンドを実行する前に、必ず使用する。「新しいリポジトリを作る」「Copilot のレビューが英語で届く」と言われたとき、または既存のリポジトリの設定を点検するときにも使う。
license: MIT
---

# GitHub リポジトリの初期設定

新しいリポジトリや既存のリポジトリで、4つの初期設定の現状を読み取り、足りない項目だけを提案して整えます。

## 前提と確認

- 読み取り（`gh auth status`、`gh repo view`、`gh api` の GET）はすぐ実行します。対話式の `gh auth login` は提示だけにし、`gh auth token` や `--show-token` は使いません。
- 書き込み（`gh repo create`、`gh repo edit --visibility`、`gh api` の PATCH / POST / PUT、`.github/` のファイル追加と commit / push）は、送り先のリポジトリと変更内容を示して確認を取ってから実行します。
- 新しく作るときは、`gh repo create <名前> --private --clone` でまず非公開として作り、公開への切り替えを求められたときは `references/go-public.md` に従います。

## 手順

1. **権限を確かめる**: `gh api repos/<owner>/<repo> --jq .permissions.admin` が `true` でなければ、マージ設定とルールセットは書き込めないため、管理者への依頼文（「管理者の権限がない場合」）を示します。ファイルの追加（Copilot の指示と Dependabot）は PR で進められます。
2. **現状を読んで差分を示す**: 下の表の4項目を調べ、「済み」か「足りない」かを一覧にします。
3. **確認を取って順に適用する**: 適用の順は **ファイル → マージ設定 → ルールセット** です。ルールセットを最後にするのは、先に入れると初期ファイルを `main` に直接 push できなくなるためです。

| 項目 | 現状の読み方 | 適用 |
| :- | :- | :- |
| Copilot の日本語の指示 | `.github/copilot-instructions.md` に日本語の指示があるか | `references/copilot-instructions.md` を置く（`AGENTS.md` があれば矛盾しないよう調整する） |
| マージ設定 | `gh api repos/<owner>/<repo>` の `allow_squash_merge`、`allow_merge_commit`、`allow_rebase_merge`、`delete_branch_on_merge` | squash のみ許可し、マージ後にブランチを自動削除する |
| Dependabot | `.github/dependabot.yml` があるか（`.github/workflows/` がまだなければ見送る） | `references/dependabot.yml` を置く |
| ルールセット | `gh api repos/<owner>/<repo>/rulesets` に同名またはデフォルトブランチ対象のものがあれば、`rulesets/<id>` で `conditions`・`rules`・`bypass_actors` を `references/ruleset.json` と比較する | なければ POST で作成し、中身が違えば差分を示して PUT で更新する |

### マージ設定のコマンド

```sh
gh api -X PATCH repos/<owner>/<repo> \
  -F allow_squash_merge=true -F allow_merge_commit=false \
  -F allow_rebase_merge=false -F delete_branch_on_merge=true
```

### ルールセットの注意点

導入前に次の4点を伝えて確認を取ります。

- `main` への直接 push、force push、削除が禁止され、変更は PR 経由の squash マージに限定される。
- 必須承認数は 0 人のため、1人のリポジトリでも PR を通せばマージできる。

`--input` には、このスキルの `references/ruleset.json` の絶対パスを渡します（相対パスは対象リポジトリ基準で解決されるため）。

- 作成: `gh api -X POST repos/<owner>/<repo>/rulesets --input <ruleset.json の絶対パス>`
- 更新: `gh api -X PUT repos/<owner>/<repo>/rulesets/<id> --input <ruleset.json の絶対パス>`
- 非公開リポジトリでプラン制限（`403`）が返ったときは、再試行せず理由を伝えて見送ります。

## 管理者の権限がない場合

> `<owner>/<repo>` の設定をお願いします。マージ方法を squash だけにして、マージ後にブランチを削除する設定と、main への変更を PR に限るルールセットです。内容は `references/ruleset.json` にあります。

## 他のスキルへの案内

- commit と push は `git`、PR は `github-pr`、Issue は `github-issue`、CI のワークフローは `github-actions`。
- Issue のラベル、`AGENTS.md`、`GLOSSARY.md` の整備は、`mattpocock-skills` が入っていれば `setup-matt-pocock-skills` を使い、入っていなければこのスキルでは扱わないことを伝えます。
