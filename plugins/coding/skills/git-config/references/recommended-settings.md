# 推奨設定と差分報告

層、実効値、出所、提示だけの意味は、`SKILL.md` に従います。

差分の報告を出すのは、利用者が「設定を確認して」「新しい環境を整えたい」と頼んだときか、症状が要設定のキーに一致したときだけです。`git config` に触れるたびに、自分から報告しません。

## 推奨設定

区分は2つです。**要設定**は、未設定だと動作が止まる、環境の取り違えが起きるなど、実害があるキーです。**任意**は好みの問題で、理由を添えた提案として示し、未設定を異常と呼びません。層はどれも global 層です。

| 区分 | キー | 推奨値 | 理由 |
|---|---|---|---|
| 要設定 | `pull.ff` | `only` | fast-forward のときだけ進み、分岐したら止まるので、意図しない merge コミットや履歴の書き換えが起きません。`pull.rebase` より優先して fast-forward のみになるので、system 層に `pull.rebase false` が残っていても矛盾しません |
| 要設定 | `init.defaultBranch` | `main` | Git 3.0 で既定が `master` から `main` に変わります。未設定だと `git init` のたびに hint が出ます |
| 要設定 | `user.name`、`user.email` | 利用者のもの（推奨値は持たない） | 未設定だと commit が失敗する場合があります（ホスト名にドメインがないと終了コード 128）。未設定のときだけ報告します |
| 要設定 | `core.autocrlf` | Windows は `true`、WSL・Linux・macOS は `input` | 環境ごとに改行をそろえるためです。下の注記を読みます |
| 任意 | `core.editor` | 推奨値は持たない（環境依存） | `GIT_EDITOR`、`VISUAL`、`EDITOR` も無いと、Git for Windows は `vim` に落ちます。3つの環境変数とも無く、未設定のときだけ知らせます |
| 任意 | `fetch.prune` | `true` | 削除済みブランチの追跡参照が溜まりません |
| 任意 | `push.autoSetupRemote` | `true` | 新しいブランチの最初の `git push` が失敗せず、`--set-upstream` を案内されません |
| 任意 | `merge.conflictStyle` | `zdiff3` | コンフリクトで共通祖先が見えます |

`core.autocrlf` の推奨値は、Pro Git の設定側の推奨です。`.gitattributes` に `eol=` か `-text` があるファイルには効きません。`* text=auto` だけでは作業ツリーの改行は固定されず、利用者の `core.autocrlf` が効きます。作業ツリーの改行まで固定するのは `eol=` か `-text` です。

次のキーは、リストに入れません。

- `push.default`: すでに `simple` が既定です。
- `help.autocorrect`: `immediate` は誤字のコマンドをそのまま実行します。
- `rerere.enabled`、`diff.algorithm`: 推奨する根拠を確かめられていません。
- 署名のキーと認証のキー: 署名は `SKILL.md` の規則に従い、認証は `references/windows.md` で扱います。

## 版の確認

差分を報告する前に `git version` を確かめます。古い Git なら、キーごとの対応版は調べず、先に Git の更新を案内します。更新できない環境(Ubuntu の標準の Git など)では、設定が効かないキーがありうることを伝え、効くかどうかは `git config --get` の結果で確かめます。

Git 3.0 での既定の変更は、公式の BreakingChanges（https://git-scm.com/docs/BreakingChanges）で確かめます。時期は未定です。

## 差分の取得

推奨のキーをすべて、キーの集合の問い合わせに渡します。

```sh
git config --show-origin --show-scope --get-regexp '^(pull\.ff|init\.defaultbranch|user\.name|user\.email|core\.autocrlf|core\.editor|fetch\.prune|push\.autosetupremote|merge\.conflictstyle)$'
```

出力には層ごとの全行が出ます。単一値のキーの実効値は、最後の行です。値を出さない種類のキーはリストに入れていないので、この出力には出ません。

## 差分報告の形

1. 差分があるキーだけを表にします（キー、実効値と出所、推奨値、区分、理由）。一致したキーは一覧せず、「一致: N 個」とだけ書きます。
2. 「この Git では使えない」キーを、別に1行で示します。
3. 直すコマンドは、global 層向けのものを提示だけにします（例: `git config --global pull.ff only`）。リポジトリ単位の `user.email` の上書きだけは、`SKILL.md` の「local 層に書く手順」に従います。
4. system 層の値が実効値のときは、「未設定」と書かず、「system 層に値がある」と出所を示します。Git for Windows のインストーラは、system 層に `pull.rebase`、`init.defaultBranch`、`core.autocrlf` などを書きます。
