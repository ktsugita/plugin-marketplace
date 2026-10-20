---
name: git-config
description: Git の設定（`git config`、`.git/config`、`~/.gitconfig`、`user.name` や `user.email` など）を読む、書くときは、コマンドを実行する前に必ず使用する。設定が効かない理由の調査、推奨設定の確認、設定に起因する Git の失敗（`git pull` の `Need to specify how to reconcile divergent branches`、`Filename too long`、改行の差分、シンボリックリンク、認証、WSL との食い違い）にも使用する。
license: MIT
---

# Git の設定の読み書きと診断

Git の設定を読む、書く、効かない理由を調べるときの規則です。次の4つの語を、同じ意味で使います。

- **層**: 設定の置き場所。system 層、global 層、local 層（`.git/config`）、worktree 層。
- **実効値**: すべての層、環境変数、`git -c` を重ねたあとに、Git が実際に使う値。
- **出所**: 実効値を与えているファイルのパス、または `command line:`。
- **提示だけ**: コマンドを実行せず、利用者に示すだけにすること。

- 「設定を確認して」のような推奨設定の確認、新しい環境の整備、要設定のキーに一致する症状（`git pull` が `Need to specify how to reconcile divergent branches` で失敗する、など）のときは、最初に `references/recommended-settings.md` を読み、そこにある差分報告の形で答えます。
- Windows や WSL の Git の問題（`Filename too long`、改行の差分、シンボリックリンク、認証、環境の取り違え）のときは、`references/windows.md` を読みます。
- Git の公式ドキュメントは https://git-scm.com/docs/git-config です。

## 層と実効値

- 読み込み順は system、global、local、worktree、command で、後ろの層が勝ちます。複数値のキーは、全層の値がすべて有効です。
- global 層には `$XDG_CONFIG_HOME/git/config`（未設定なら `~/.config/git/config`）と `~/.gitconfig` の2ファイルがあり、両方あれば両方を読みます。同じキーは `~/.gitconfig` が勝ちます。
- `--global` を付けた読み書きは1ファイルだけを対象にします（`~/.gitconfig` が読めればそれ、なければ XDG 側）。
- scope が `command` の値は、`GIT_CONFIG_COUNT` 系の環境変数か `git -c` です。出力では両者を区別できません。
- worktree 層は `extensions.worktreeConfig` が有効なときだけ存在します。

## 読む

読み方は、見たいキーを先に決め、そのキーを名指しで引く問い合わせだけです。範囲指定（`--global` など）は付けません。全キーの列挙（`git config list`、`--list`、`--get-regexp '.*'`）は、どのキーがあるかを調べる目的でも、`--name-only` を付けても使いません。キー名にもトークンが入りうる（`url.<base>.insteadOf` など）ためです。

- 単一のキー: `git config --show-origin --show-scope --get-all <key>`
- キーの集合: `git config --show-origin --show-scope --get-regexp '^(key1|key2)$'`（名前は小文字。Git は変数名を小文字で出力します）

単一値のキーの実効値は、出力の最後の行です。

次の種類のキーは、名前、層、出所だけを示し、値を示しません。`remote.*.url`、`pushurl`、`url.*`、`http.*`、`credential.*`、`sendemail.*`、キー名に `password`、`token`、`secret` を含むもの。これらのキーは、`--name-only` を付けた `--get-regexp` に、アンカーと `.` のエスケープを付けたパターン（`'^sendemail\.smtppass$'`）を渡して引きます。`--name-only` は `--get-all` と組み合わせられません（終了コード 129）。値が必要なときは、利用者が自分で実行するコマンドを提示します。会話に出た秘密は取り消せないためです。

次の経路は、秘密が出るので使いません。

- `GIT_TRACE*`、`GIT_CURL_VERBOSE`
- `git credential fill`
- `gh auth token`、`gh auth status --show-token`
- `git remote -v` の素の出力（`://<userinfo>@` を隠した形だけ使います）
- `env`、`printenv` の全体（`GIT_CONFIG_*` は変数名の有無だけを確かめます）

設定ファイル（`.git/config`、`~/.gitconfig`、`~/.config/git/config`、include 先）は、ファイル読み取りツールで開かず、`git config` 経由だけで読みます。`.gitattributes` はリポジトリの内容なので、読んでかまいません。

## 診断

設定が効かない理由は、次の順に調べ、最初に当たった原因で止めます。

入口で3点を確かめます。

1. 呼ばれる Git の実体と版（`git version`、`type -a git` または `Get-Command git -All`）。
2. global 層と system 層のファイルの場所（`git var GIT_CONFIG_GLOBAL`、`git var GIT_CONFIG_SYSTEM`。エラーになる古い Git では、Git を更新するよう案内します）。
3. リポジトリの中か外か（`git rev-parse --is-inside-work-tree`）。

利用者が言う問題の環境（WSL、PowerShell など）がいまの shell と違うときは、その環境の値を推測せず、その環境で実行するコマンドを提示します。global 層の場所は OS ではなく環境変数で決まり、WSL は Windows と別の Git、別の global 層、別の system 層を持つためです。

調べる順序は次のとおりです。

1. 対象キーの実効値と出所（単一キーの問い合わせ）。
2. 層どうしの衝突（system 層の値を global 層が上書きしている、など）。
3. scope が `command` なら、環境変数か `git -c`。変数名の有無だけを確かめます。
4. `include` と `includeIf`。条件を確かめます（`gitdir:` は末尾に `/` が要る。linked worktree では本体の `.git` に対して照合される。`worktree:` 条件は 2.56.0 以降）。どの条件が効いたかは出力に出ません。
5. `GIT_CONFIG_GLOBAL`、`GIT_CONFIG_NOSYSTEM`、`GIT_CONFIG` の有無。
6. 別の環境や別の Git が呼ばれていないか（入口の結果と照らします）。
7. 改行の問題なら属性（`git check-attr -a <path>`、`git ls-files --eol`）。

層の影響を切り分けるときは、読み取り専用のコマンドに限り、`GIT_CONFIG_GLOBAL` を実在する空のファイルに、`GIT_CONFIG_NOSYSTEM=1` に差し替えて実行できます。`NUL` や `/dev/null` は指しません（Windows の Git の不具合は `references/windows.md`）。

報告は次の順に書きます。

1. 原因の層と出所（パスはそのまま示します）。
2. 実効値（値を出さない種類のキーは名前と出所だけ）。
3. 根拠（どの問い合わせの出力のどの行か）。
4. 直すコマンドの提示（「書く」の規則に従います）。

原因を特定できなかったときは、確かめた項目と、確かめなかった項目（秘密が出るので引かなかったもの、別の環境にあるもの）を報告します。「異常なし」と読まれないためです。

## 書く

### 書いてよいキー

local 層に書いてよいのは、次のキーだけです。

`user.name`、`user.email`、`core.autocrlf`、`core.eol`、`core.longpaths`、`pull.ff`、`pull.rebase`、`fetch.prune`、`push.autoSetupRemote`、`merge.conflictStyle`

このリストにないキーは、local 層でも提示だけにします（承認を取っても実行しません）。外部コマンドを実行させたり、認証の経路を変えたりできるキーが多く、版ごとに増えるためです。判断に迷いやすい代表は、次のとおりです。

- `commit.gpgSign` と署名のキー（`tag.gpgSign`、`gpg.*`、`user.signingkey`）。`commit.gpgSign=true` を local 層に置くだけで、引数なしの `git commit` が `gpg.program` を呼びます。
- `core.sshCommand`、`core.hooksPath`、`core.fsmonitor`、`alias.*`、`filter.*`、`credential.helper`、エディタとページャの指定。
- `url.*.insteadOf`、`remote.*.url`、`http.*`、`credential.*`。

署名は、エラーや質問があったときだけ扱います。失敗したときのエラーメッセージ（`gpg failed to sign the data`、`Couldn't load public key <path>` など）を読んで原因を報告し、署名を外す操作はしません。署名に失敗すると、コミットは作られません。

### 層の選び方

- リポジトリの中で、利用者が層を指定しないときは local 層に書きます。`--local` を必ず付けます。
- リポジトリの外、または「全部のリポジトリで」「自分の環境で」と言われたときは、global 層向けのコマンドを提示するだけにします。
- 実効値が別の層から来ているときは、まず出所を示します。利用者が「このリポジトリだけ」と言ったときだけ、local 層で上書きします。
- system 層は、利用者が明示したときだけ、コマンドを提示します。worktree 層は使わず、`extensions.worktreeConfig` の有効化も提案しません（`--local` の値は全 worktree で共有されます）。

### local 層に書く手順

1. 実効値と出所を示します（単一キーの問い合わせ）。
2. 実行するコマンドと、元に戻すコマンド（以前の値の再設定、または `--unset`）を示します。
3. 利用者への確認ツール（Claude Code では `AskUserQuestion`、GitHub Copilot CLI では `ask_user`、Antigravity CLI では `ask_question`）で、「実行する」「修正する」「中止する」を示して承認を取ります。
4. 実行の直前に、書き込みとは別のコマンドで実効値を取り直し、承認時と同じであることを確かめます。書き込みと同じ呼び出しに `&&` でつなぎません（つなぐと、値が変わっていても書き込みが止まりません）。違っていたら書かずに、今の実効値と出所を示して手順 2 からやり直します（元に戻すコマンドも、今の値に合わせて更新してから、承認を取り直します）。
5. 実行後に、同じ問い合わせで実効値を確かめます。意図した値でなければ（環境変数や `-c` の上書きなど）報告します。

確認ツールを使えない場合や、質問に自動で回答されるモードでは、実行せずにコマンドを提示して終了します。

`--all`、`--unset-all`、`--value=` を伴う操作は、消える行をすべて列挙して承認に含めます。複数値のキーへの書き込みが終了コード 5 で失敗しても、`--all` に切り替えません。

### 書き込みの手段

- 書くのは `git config` コマンドだけです。設定ファイルをファイル編集ツールで書き換えません。
- コマンドは、古い Git でも動く形（`git config --local <key> <value>`、`--unset`、`--get-all`）で書きます。サブコマンド形式（`set`、`get`、`list`）は 2.46.0 で入りました。
- `git -c` と `GIT_CONFIG_*` は、読み取り専用の確認と診断の隔離に使います。状態を変える操作では、承認なしに設定を上書きするために使いません（`-c commit.gpgsign=false`、`-c url.*.insteadOf=...`、`-c core.hooksPath=...` など）。認証に失敗したときも、別の経路に切り替えません。利用者が明示的に頼んだ一回限りの上書きは、内容を示して実行します。
- global 層や system 層に書くことが目的のコマンド（`gh auth setup-git`、`hk install --global`、`git lfs install`、`git credential-manager configure` など）は、`git config --global` と同じ扱いで、提示だけにします。local 層に書くことが目的のコマンドは、そのツールのスキルの手順に従います。`init`、`clone`、`remote add`、`branch -u` のような通常の Git 操作は、この規則の対象外です。
