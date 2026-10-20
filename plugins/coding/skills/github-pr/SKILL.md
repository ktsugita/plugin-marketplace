---
name: github-pr
description: gh pr のコマンドを実行する前に、必ず使用する。PR を出す、CI の結果を見る、CI の失敗を読む、レビューの指摘に対応する、ベースの変更を取り込む、マージするとき、または GitHub に不慣れな利用者が PR の流れで迷ったときに使う。
argument-hint: "[create|feedback|response|close] [PR番号]"
license: MIT
---

# GitHub Pull Request の案内

GitHub 初学者（Git の基本操作は一部分かるが、GitHub の Issue と Pull Request の運用に慣れていない利用者）が PR を出してマージするまでを助けます。

操作は3段階で扱います。読み取りはすぐ実行し、ローカルで戻せる操作は一言添えて実行し、作業を失う操作と外に出る操作は確認を取ってから実行します。

次の3語を、この意味で使います。

- **確認を取る**: 実行するコマンド、変わること、戻せないことを示し、利用者の返事を待つこと。
- **区切り**: 作業の節目（push した、PR を作った、CI が落ちた、など）。
- **兆候**: 迷いや失敗のしるし。エラー出力の貼り付け、「分からない」「どうすれば」、同じ操作の繰り返し、用語の取り違え。

**提示だけ**は `git-config` と同じ意味です（コマンドを実行せず、利用者に示すだけにすること）。

## 呼び出しと動詞

呼び出しに動詞（引数）が付いているときは、次の表の節に進みます。動詞が付いていないときは、「区切りと次の一手」に従います。表にない動詞のときは、この一覧を示して選んでもらいます。どの動詞でも、「準備と前提」と「確認を取る操作」が先に効きます。`feedback`、`response`、`close` の対象の PR は、動詞のあとの番号、なければ今のブランチの PR（`gh pr view --json number --jq .number`）です。

| 動詞 | 進む節 |
| :- | :- |
| `create` | 「PR を作る」 |
| `feedback` | CI とレビューの指摘を、読み取りだけで集めて一覧にする。CI は `gh pr checks <番号>` で見て、落ちていれば `references/ci-failure.md`。指摘は `references/review-response.md` の「1. 指摘を集める」 |
| `response` | `references/review-response.md` の「2. 一覧にして、1つずつ直す」から「3. 返信と Resolve」まで。対応したスレッドは、返信と Resolve まで進める（返信文の一覧に、一括で確認を取る） |
| `close` | 「マージしたあと」。ローカルのブランチの削除まで進める（`git branch -D` は確認を取る）。マージ済みでなければ、削除せず、「マージする」を提案する |

## 準備と前提

- リポジトリの決まりを先に読みます（読み取りだけ）: PR テンプレート、`CONTRIBUTING.md`、`AGENTS.md`。PR テンプレートは、`git ls-tree -r --name-only origin/<ベース> | grep -i -E '(^|/)pull_request_template(\.md|/)'` で探します（ルート、`docs/`、`.github/` の `pull_request_template.md` と、複数あるときの `PULL_REQUEST_TEMPLATE/` が対象です）。あれば、この skill の既定より先に従います。
- 最初の書き込みの直前に、`gh auth status` で認証を、`gh repo view --json nameWithOwner --jq .nameWithOwner` で送り先のリポジトリを確かめます。`gh auth login` は対話式なので、利用者が自分で実行するコマンドとして提示だけにします。認証情報の設定そのものの不具合は、`git-config` に任せます。
- `gh auth token` と `gh auth status --show-token` は、秘密が出るので避けます。

## 区切りと次の一手

次の一手は1つだけ、理由を1文つけて提案します。実行は、利用者が頷いてからです。頷きが覆うのは、「説明してから実行する」段階までの操作です。「確認を取ってから実行する」段階の操作は、その操作の直前に、あらためて確認を取ります。

| 区切り | 次の一手 |
| :- | :- |
| push した | レビューを受けるために、PR を作る。 |
| PR を作った | 待つ。作った直後は CI が終わっておらず、Copilot のレビューも届いていない。URL を示し、「CI が失敗したり、コメントがついたり、マージされたりしたら知らせてください」と伝える。 |
| CI が落ちた | `references/ci-failure.md` に沿って失敗の箇所を読み、ワークフローの定義が原因なら `github-actions` に進む。 |
| レビューの指摘が来た | `references/review-response.md` に沿って、指摘を一覧にし、最初の1つの対応を提案する。 |
| ベースが進んだ、またはコンフリクトした | 「ベースの変更を取り込む」に進む。 |
| CI が通り、承認された | マージを提案する。 |
| マージした | ローカルを片付けるため、ベースに戻って最新にする。 |

兆候があるときは、説明を厚くします。用語は初出で1文だけ説明し、利用者がその用語を正しく使っているなら省きます。

## 確認を取る操作

| 段階 | 操作 |
| :- | :- |
| すぐ実行する | `gh pr list` / `view` / `status` / `diff` / `checks`、`gh run view --log-failed`、`gh repo view`、レビューの指摘の読み取り（`gh api` の GET と GraphQL の query） |
| 説明してから実行する（何をするかを一言添える） | `gh pr checkout`（ローカルのブランチを切り替える） |
| 確認を取ってから実行する | `gh pr create`（`--draft` を含む）、`comment`、`review`、`edit`、`ready`、`update-branch`、`merge`（`--auto` を含む）、`close`、`reopen`、`revert`、`gh run rerun`、スレッドへの返信とスレッドの Resolve、ローカルの `git branch -D` |

確認では、送り先のリポジトリと、操作の内容（タイトルと本文、ベースとヘッド、マージ方法など）を見せます。

## 場面ごとの手順

### PR を作る

1. 前提を読み取りで確かめます。今のブランチがベースでないこと（ベースなら、`git` の「`main` に直接 commit した、ブランチを切り忘れた」へ）。ベースより先のコミットがあること（`git log --oneline <ベース>..HEAD`）。**ベース**（マージ先のブランチ）は `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name` で調べ、**ヘッド**（PR の変更を含む、今のブランチ）と区別します。関連する Issue（ブランチ名の番号、または利用者の指定）。
2. 未 push なら、`push` を提案します（確認を取る。手順は `git`）。
3. 本文を書きます。`mattpocock-skills:pr` を読み込み、そのテンプレートで書きます。Issue があり、ベースがデフォルトブランチなら、本文に `Closes #番号` の行を足します（`github-issue` を参照）。「準備と前提」で見つけた PR テンプレートがあれば、そちらを優先します（複数あるときは、どれを使うかを利用者に聞きます）。
   - `mattpocock-skills:pr` が読み込めないときは、本文の作成を進めず、次の文を示します。「PR 本文の作成には `mattpocock-skills` の `pr` が必要です。入っていないようです。Claude Code は `claude plugin install mattpocock-skills@bnba-infra`、Copilot CLI は `copilot plugin install mattpocock-skills@bnba-infra` で入れてください。」
4. 本文を一時ファイルに書き、送り先のリポジトリ、ベースとヘッド、タイトル、本文を見せて、確認を取ります。タイトルは、リポジトリのコミットの書き方に合わせます。
5. `gh pr create --title "<タイトル>" --body-file <ファイル> --base <ベース>` で作ります。`--title` と `--body`（または `--body-file`）がないと、対話式のプロンプトが出て止まります。
6. 既定は、レビューを受けられる PR です。利用者が「まだ途中」と言ったときだけ、`--draft` を提案します。準備ができたら `gh pr ready <番号>`（確認を取る）。

### ベースの変更を取り込む

`gh pr view <番号> --json mergeStateStatus,mergeable,baseRefName` で状態を見ます。`BEHIND`（ベースが進んだ）なら、`gh pr update-branch <番号>`（確認を取る）で取り込み、手元は `git pull --ff-only origin <ブランチ名>` で追いつきます。`DIRTY`（コンフリクト）なら、手元をその PR のブランチにし（違えば `gh pr checkout <番号>`）、`git fetch origin <ベース>` と `git merge origin/<ベース>`（説明してから実行）で手元にコンフリクトを出してから、`git` の `references/conflict.md` に進みます。

### マージする

1. `gh pr view <番号> --json state,isDraft,reviewDecision,mergeStateStatus` と `gh pr checks <番号>` で、ドラフトでないこと、CI が通っていること、必要な承認があることを確かめます。足りないときは、足りない理由を説明し、待つことを案内します。
2. マージ方法は、`gh repo view --json squashMergeAllowed,mergeCommitAllowed,rebaseMergeAllowed` で許されたものだけを提案します（例: `--squash`）。
3. 内容を見せて確認を取り、`gh pr merge <番号> --squash` のように実行します（`--admin` は使いません）。条件を満たしたら自動で行うなら `--auto` です（確認を取る）。

### マージしたあと

1. `git switch <ベース>` と `git pull --ff-only` で、ベースを最新にします。
2. `gh repo view --json deleteBranchOnMerge` が `true` なら、リモートのブランチは自動で消えています。`git fetch --prune` で手元の参照を整えます。
3. ローカルのブランチは、squash でマージすると、`git branch -d` が「まだマージされていない」と拒否します。コミットの形が変わったためで、マージ済みであることは `gh pr view <番号> --json state` で確かめられます。確かめたうえで、`git branch -D <ブランチ名>` を、確認を取って実行します。

## 他の skill への案内

- ブランチ、commit、push の手順、コンフリクトの解消は `git`。Issue の読み方と、`Closes #番号` の書き方は `github-issue`。
- CI のワークフロー自体の不具合（`.github/workflows/` の定義）は `github-actions`。認証情報の設定の不具合は `git-config`。
- Copilot のレビューが英語で届くときは、日本語にする指示を足す `setup-github-repo`。案内するだけにして、指示の文面はこの skill に書かない。
