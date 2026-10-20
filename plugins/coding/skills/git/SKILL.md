---
name: git
description: git の書き込み系コマンド（clone、switch、add、commit、push、pull、merge、reset、restore など）を実行する前に、必ず使用する。GitHub に不慣れな利用者が Git で迷ったり失敗したときにも使う。
argument-hint: "[start|commit|push|sync|undo|conflict|auth]"
license: MIT
---

# Git の基本の案内

GitHub 初学者（Git の基本操作は一部分かるが、GitHub の Issue と Pull Request の運用に慣れていない利用者）が Git を使うのを助けます。

操作は3段階で扱います。読み取りはすぐ実行し、ローカルで戻せる操作は一言添えて実行し、作業を失う操作と外に出る操作は確認を取ってから実行します。

次の3語を、この意味で使います。

- **確認を取る**: 実行するコマンド、変わること、戻せないことを示し、利用者の返事を待つこと。
- **区切り**: 作業の節目（clone した、commit した、push が拒否された、など）。
- **提示だけ**: コマンドを実行せず、利用者に示すだけにすること。

## 呼び出しと動詞

呼び出しに動詞（引数）が付いているときは、次の表の節に進みます。動詞が付いていないときは、「区切りと次の一手」に従います。表にない動詞のときは、この一覧を示して選んでもらいます。どの動詞でも、「準備と前提」と「操作の段階」が先に効きます。

| 動詞 | 進む節 |
| :- | :- |
| `start` | 「始める」 |
| `commit` | 「変更を見て commit する」 |
| `push` | 「push する」 |
| `sync` | 「push が拒否された」 |
| `undo` | `references/undo.md`（`main` に直接 commit した場合は、「`main` に直接 commit した」の節） |
| `conflict` | `references/conflict.md` |
| `auth` | 「認証のエラー」 |

## 準備と前提

- リポジトリの規約（`AGENTS.md`、`CONTRIBUTING.md`、`commit-msg` フック、`git log` の履歴）を先に読みます。規約があれば、この skill の既定より規約に従います。
- 準備の確認は、最初の書き込み操作の直前に、必要なものだけ行います。`commit` の前に `git config user.name` と `git config user.email`（1キーずつ読む）。`push` の前に `gh auth status`。
- 足りないとき、Git の設定は `git-config` に任せます。`gh auth login` と `gh auth setup-git` は対話式なので、利用者が自分で実行するコマンドとして提示だけにします（Claude Code では `! gh auth login` と入力すると、その場で実行できます。それ以外のツールでは、別のターミナルで実行してもらいます）。
- リモートの名前は `git remote`、認証の状態は `gh auth status` で確かめます。素の `git remote -v`、`gh auth token`、`gh auth status --show-token` は、URL に埋め込まれた token などの秘密が出るので避けます。

## 区切りと次の一手

次の一手は1つだけ、理由を1文つけて提案します。実行は、利用者が頷いてからです。頷きが覆うのは、「説明してから実行する」段階までの操作です。「確認を取ってから実行する」段階の操作は、その操作の直前に、あらためて確認を取ります。

| 区切り | 次の一手 |
| :- | :- |
| clone した | 作業用のブランチを切る（「始める」へ）。 |
| ブランチを切った、または変更した | 変更を見て `add` と `commit` をする（「変更を見て commit する」へ）。 |
| commit した | `push` する（「push する」へ）。 |
| push した | PR を作る（`github-pr` へ）。 |
| `main` に直接 commit した、ブランチを切り忘れた | 「`main` に直接 commit した」へ。 |
| push が拒否された | 「push が拒否された」へ。 |
| commit や push がフックに止められた | フックの出力を読んで原因を直す。`commit-msg` なら、メッセージを規約に合わせる。 |
| コンフリクトが出た | `status` でファイルを確認し、`references/conflict.md` を読む。 |
| 変更を捨てたい、または戻したい | `references/undo.md` を読む。 |

迷いや失敗のしるし（エラー出力の貼り付け、「分からない」「どうすれば」、同じ操作の繰り返し、用語の取り違え）があるときは、説明を厚くします。用語は初出で1文だけ説明し、利用者がその用語を正しく使っているなら省きます。

## 操作の段階

段階の基準は、作業ツリーの変更とコミットが残るかです。表にない操作も、この基準で判断し、迷えば確認を取る側に倒します。

| 段階 | 操作 |
| :- | :- |
| すぐ実行する | `status`、`diff`、`log`、`show`、`branch`（一覧）、`remote`（名前だけ）、`reflog`、`gh auth status` |
| 説明してから実行する（何をするかを一言添える） | `clone`、`fetch`、`pull --ff-only`、`switch`、`switch -c`、`add`、`commit`、`restore --staged`、`stash`（退避だけ）、`merge`（ローカルへの取り込み）、`revert` |
| 確認を取ってから実行する | 作業を失う・履歴を書き換える: `reset`、`restore <パス>`、`clean`、`rebase`、`commit --amend`、`branch -D`、`branch -f`、`stash drop` / `clear`、`merge --abort`、`rebase --abort`、`switch -f`。外に出る: `push`（`--force-with-lease` を含む） |

- コミットしていない変更が消える `restore <パス>` は、確認を取ります。
- `push --force` は勧めません。必要に見えるときは、原因を説明し、`--force-with-lease` を確認の段階で提案します。

## 場面ごとの手順

### 始める

- `git clone <URL>`。置き先のディレクトリを、先に伝えます。
- 続けて、`main` に直接 commit しないよう `git switch -c <ブランチ名>` で作業用のブランチを切ります。
- ブランチ名は、短い英小文字とハイフンで、内容が分かるものにします。Issue があれば番号を含めます（例: `12-fix-typo`）。

### 変更を見て commit する

1. `git status`、`git diff`、`git diff --staged` で、何が変わったか（`add` 済みの変更を含む）を見せます。
2. `git add <パス>` でファイルを1つずつ選びます。`.env`、鍵、トークンらしきファイルは、`add` せずに理由を説明します。`add` 済みの差分（`git diff --staged`）に、トークンやパスワードらしき文字列がないかも見ます。見つけたときは `references/undo.md` を読みます。
3. メッセージの既定は、日本語の Conventional Commits です（例: `feat: ログイン画面にパスワード表示の切り替えを足す`）。種類は `feat`、`fix`、`docs`、`refactor`、`test`、`chore`。1行目で何を変えたかを書き、本文で理由を書きます。メッセージは、変更の背景と内容だけで終えます（AI ツールの帰属行は付けません）。
4. メッセージを `.git/` 配下の一時ファイル（例: `.git/COMMIT_EDITMSG.tmp`）に書き、何をするかを説明してから `git commit -F <ファイル>` で実行します。成功しても、フックに止められても、一時ファイルを削除します（特殊文字のエスケープ漏れや作業ツリーの汚損を防ぐため）。止められたときは、「区切りと次の一手」の表に従います。

### push する

- `push` は確認を取ります。送り先のブランチと、送るコミットを `git log --oneline @{upstream}..HEAD`（上流がなければ `git log --oneline -5`）で見せます。
- 最初の `push` は `git push -u origin <ブランチ名>` です。`push.autoSetupRemote` が有効なら、`git push` だけで通ります。

### `main` に直接 commit した、ブランチを切り忘れた

1. `git fetch` で `origin/main` を最新にしてから、`git log --oneline origin/main..HEAD` で、push していないコミットを見せます。push 済みなら、ここで止まり、履歴を書き換えずに、リポジトリの管理者に相談するよう案内します。
2. `git switch -c <新しいブランチ名>` を実行します（コミットは新しいブランチについてきます）。
3. `main` の指す先を戻します。`git branch -f main origin/main` は確認を取ります。コミットは新しいブランチに残ることを、先に伝えます。

### push が拒否された

- `rejected` と `non-fast-forward`（または `fetch first`）は、リモートに手元にないコミットがある、という意味です。
- `git fetch` のあと、`git log --oneline HEAD..origin/<ブランチ名>` で、手元にないコミットを見せます。`git pull --ff-only origin <ブランチ名>` で進めれば、それで済みます。初回の `push` の拒否では上流が未設定で、引数なしの `git pull` は「追跡情報がない」で失敗するので、必ず `origin <ブランチ名>` を付けます。
- `--ff-only` が失敗したら、手元とリモートの両方に新しいコミットがあります。`git merge origin/<ブランチ名>` で取り込みます（説明してから実行）。コンフリクトが出たら `references/conflict.md` を読みます。

### 認証のエラー

- `Authentication failed`、`could not read Username`、`Permission denied`、`403` が出たら、まずリモートの方式を見分けます。URL には token が埋まっていることがあるので、URL 全体を出力させず、先頭の方式だけを取り出します。bash なら `git remote get-url origin | grep -o -E '^(https://|ssh://|git@)'`、PowerShell なら `(git remote get-url origin) -replace '^(https://|ssh://|git@).*','$1'` です。
- https なら、`gh auth status` で見分けます。ログインしていなければ、`gh auth login` と `gh auth setup-git` を、利用者が自分で実行するコマンドとして提示だけにします。ログインしているのに `403` なら、そのリポジトリへの書き込み権限がありません。リポジトリの管理者に権限を頼むか、フォークして PR を出す流れを案内します。
- ssh で `Permission denied (publickey)` なら、鍵が登録されていないか、エージェントに読み込まれていません。`ssh -T git@github.com` の結果を見せて、鍵の登録を案内します。
- 認証情報の設定そのものの不具合（credential helper、WSL との食い違い）は、`git-config` に任せます。

## 他の skill への案内

- PR の作成、CI の確認、レビュー対応、マージは `github-pr`。
- Issue の読み方と作り方は `github-issue`。
- ワークフロー（`.github/workflows/`）の編集や、CI の定義の不具合は `github-actions`。
