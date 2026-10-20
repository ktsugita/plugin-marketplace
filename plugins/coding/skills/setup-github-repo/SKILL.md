---
name: setup-github-repo
description: GitHub リポジトリの初期設定(Copilot のレビューを日本語にする指示、マージ設定、Dependabot、デフォルトブランチのルールセット)を整えるとき、`gh repo create` や設定を書き込むコマンドを実行する前に、必ず使用する。「新しいリポジトリを作る」「Copilot のレビューが英語で届く」と言われたとき、または既存のリポジトリの設定を点検するときにも使う。
license: MIT
---

# GitHub リポジトリの初期設定

新しいリポジトリを作る利用者を助けます。中心の読者は GitHub 初学者(Git の基本操作は一部分かるが、GitHub の Issue と Pull Request の運用に慣れていない利用者)です。

新しいリポジトリにも、すでにあるリポジトリにも使えます。まず現状を読み、足りないものだけを提案します。2 回実行しても、同じ結果になります。

次の2語を、この意味で使います。

- **確認を取る**: 実行するコマンド、変わること、戻せないことを示し、利用者の返事を待つこと。
- **差分**: 整えたい状態と、今の状態の違い。

## 準備と前提

- `gh auth status` で認証を確かめます。`gh auth login` は対話式なので、利用者が自分で実行するコマンドとして提示だけにします。秘密が出る `gh auth token` と `gh auth status --show-token` は、実行しません。
- 新しく作るときは、`gh repo create <名前> --private --clone` を、確認を取ってから実行します。非公開で作り、公開は準備ができてから切り替えます(`references/go-public.md`。利用者が「公開したい」と言ったときに読みます)。
- 既存のリポジトリでは、`gh repo view --json nameWithOwner --jq .nameWithOwner` で、送り先を利用者に見せます。
- 設定の読み取りと書き込みには、`gh api repos/<owner>/<repo>` を使います。

## 手順

1. **権限を確かめる(すぐ実行)**: `gh api repos/<owner>/<repo> --jq .permissions.admin` が `true` でなければ、設定とルールセットは書き込めません。ここで書き込みを止め、「管理者の権限がない場合」の依頼文を示します。ファイルの追加(Copilot の指示と Dependabot)は、権限がなくても PR で進められます。
2. **現状を読む(すぐ実行)**: 下の「項目」の表の「現状の読み方」で、4 つの項目の現状を集めます。
3. **差分を一覧にする**: 項目ごとに、「済み」か「足りない」かを 1 行で示します。足りない項目だけを、適用の候補にします。すべて済みなら、「すでに整っています」と伝えて終わります。
4. **確認を取って、1 項目ずつ適用する**: 適用の順は、ファイル、マージ設定、ルールセットです。ルールセットを最後にするのは、先に入れると、初期のファイルを main に直接 push できなくなるためです。

## 項目

| 項目 | 現状の読み方 | 適用 |
| :- | :- | :- |
| Copilot の日本語の指示 | `.github/copilot-instructions.md` があるか、日本語の指示が入っているか | `references/copilot-instructions.md` の文面を、`.github/copilot-instructions.md` に置く |
| マージ設定 | `gh api repos/<owner>/<repo>` の `allow_squash_merge`、`allow_merge_commit`、`allow_rebase_merge`、`delete_branch_on_merge` | squash だけを許し、マージ後にブランチを削除する(下の「マージ設定」) |
| Dependabot | `.github/dependabot.yml` があるか。`.github/workflows/` があるか | `references/dependabot.yml` を置く。ワークフローがまだないときは、見送る |
| ルールセット | `gh api repos/<owner>/<repo>/rulesets` の一覧に、同じ名前か、デフォルトブランチが対象のルールセットがあるか。あれば `gh api repos/<owner>/<repo>/rulesets/<id>` で中身を取って、`references/ruleset.json` と比べる | なければ作り、違えば更新する(下の「ルールセット」) |

### Copilot の日本語の指示

- Copilot のレビューが、英語になったり日本語になったりするときに、効く手段です。ファイルがあると、Copilot のレビューは日本語になります。
- Copilot CLI は `AGENTS.md` も読み、結合して扱います。優先順位は定められていません。`AGENTS.md` が既にあるときは、中身を読み、指示が矛盾しないようにします。
- 指示は短く保ちます。文面を足すときも、1 段落にします。
- 書いたファイルは、`git` の手順で commit します。新しいリポジトリなら、ルールセットを入れる前に、main に直接 push できます。すでにルールセットがあるリポジトリでは、ブランチを切って PR にします(`github-pr`)。

### マージ設定

確認を取って、次を書き込みます。

```sh
gh api -X PATCH repos/<owner>/<repo> \
  -F allow_squash_merge=true -F allow_merge_commit=false \
  -F allow_rebase_merge=false -F delete_branch_on_merge=true
```

squash だけにするのは、PR 1 つが main の 1 コミットになり、履歴を追いやすいためです。マージ後にブランチを自動で消すので、後片付けの手間が減ります。

### ルールセット

main への変更を、PR 経由に限ります。一人のリポジトリでは、手順が 1 つ増えます。初学者には、PR を出す流れを一通り経験できる利点があります。利用者が「全部やって」と言ったときも、次の 4 点を必ず伝えて、入れるかどうかを利用者に決めてもらいます。

- main に、直接 push できなくなる。
- マージは、PR を通して squash だけでできる。承認は 0 人でよいので、一人でも詰まらない。
- リポジトリの管理者は、PR を通せば、承認なしでマージできる。
- main の履歴の書き換え(force push)と、main の削除が、禁止される。間違えた commit を force push で消す復旧は使えなくなり、`git revert` で打ち消す形になる。

一覧は概要しか返さないので、「済み」かどうかは、`rulesets/<id>` で取った中身で判断します。`references/ruleset.json` と比べるのは、条件(`conditions`)、ルール(`rules`)、バイパス(`bypass_actors`)の 3 つです。`id` や `updated_at` など、サーバーが足す項目は比べる対象に入りません。名前だけが同じで中身が違うときは、新しく作らず、違いを示して、更新するかを確かめます。

`--input` には、この skill の `references/ruleset.json` の絶対パスを渡します(相対パスは、コマンドを実行する対象リポジトリの作業ディレクトリ基準で解決され、ファイルが見つかりません)。

- なければ、`gh api -X POST repos/<owner>/<repo>/rulesets --input <ruleset.json の絶対パス>` で作ります。
- 中身が違えば、`gh api -X PUT repos/<owner>/<repo>/rulesets/<id> --input <ruleset.json の絶対パス>` で更新します。
- 一致していれば、何もしません。

プランによっては、非公開のリポジトリにルールセットを作れません(`403` で、プランの案内が返ります)。その場合は、再試行せず、理由を伝えて見送ります。

CI のチェックを必須にする設定は、CI ができてから `github-actions` と相談して、ルールセットに足します。

## 管理者の権限がない場合

設定とルールセットは、書き込まずに止まります。管理者への依頼文を、そのまま送れる形で示します。

> `<owner>/<repo>` の設定をお願いします。マージ方法を squash だけにして、マージ後にブランチを削除する設定と、main への変更を PR に限るルールセットです。内容は `references/ruleset.json` にあります。

## 確認を取る操作

| 段階 | 操作 |
| :- | :- |
| すぐ実行する | `gh auth status`、`gh repo view`、`gh api` の GET(設定、ルールセット、ファイルの有無の読み取り) |
| 確認を取ってから実行する | `gh repo create`、`gh repo edit --visibility`(公開範囲の変更)、`gh api` の PATCH、POST、PUT(設定とルールセットの書き込み)、`.github/` のファイルの作成と変更、それらの commit と push |

確認では、送り先のリポジトリと、変わる項目を見せます。

## 他の skill への案内

- commit と push は `git`、PR は `github-pr`、Issue は `github-issue`。
- CI のワークフローは `github-actions`。Dependabot の対象に使う GitHub Actions を、新しく書くときも同じです。
- Issue のラベル、`AGENTS.md`、`GLOSSARY.md` の準備は、`mattpocock-skills` の `setup-matt-pocock-skills` が扱います。
