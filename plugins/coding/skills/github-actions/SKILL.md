---
name: github-actions
description: .github/workflows/ 配下のワークフローの作成・編集、GitHub Actions のセキュリティ対策（permissions、スクリプトインジェクション防止）、デバッグを行うときに使用する。
license: MIT
---

ワークフローを作成・編集したら、以下の全項目を適用し、最後に `actionlint` を通してください。

## セキュリティ

### permissions を最小限に設定する

`permissions` を省略したときの `GITHUB_TOKEN` の権限は、エンタープライズ・組織・リポジトリの設定で決まります。2023年2月以降に作られたものは読み取り専用が既定ですが、それより前からあるものは読み書きの権限が付くことがあります。設定に左右されないよう、トップレベルで既定の権限を絞り、ジョブごとに必要な権限だけを明示してください（`write-all` ではなく `contents: write` など）。`permissions` で1つでも権限を指定すると、指定しなかった権限は `none` になります。

```yaml
permissions:
  contents: read

jobs:
  publish:
    permissions:
      contents: write
```

### スクリプトインジェクション（式直接展開）を防ぐ

`${{ github.event... }}` や `${{ inputs... }}` などの外部入力を `run:` に直接埋め込むと、任意コード実行の脆弱性になります。必ず中間環境変数（`env:`）を介して参照してください。

```yaml
- name: Print issue title
  env:
    ISSUE_TITLE: ${{ github.event.issue.title }}
  run: |
    echo "Processing issue: $ISSUE_TITLE"
```

### アクションを commit SHA でピン留めする

`@main` や `@latest` は、予期しない破壊的変更の影響を受けます。`@vN` のようなタグも、作者が付け替えたり削除したりできます。GitHub が不変とするのは完全な commit SHA へのピン留めだけなので、`uses: actions/checkout@<commit-sha> # vX.Y.Z` の形で、版をコメントに書いてください。

SHA と版は、書く時点で次のコマンドで調べます。

```bash
# 最新のリリースのタグ
gh api repos/<owner>/<repo>/releases/latest --jq .tag_name
# そのタグが指す commit SHA
gh api repos/<owner>/<repo>/commits/<タグ> --jq .sha
```

ピン留めした SHA の更新は Dependabot に任せます。Dependabot は SHA と版のコメントを一緒に更新します。

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
```

### actions/checkout には persist-credentials: false を付ける

既定では `GITHUB_TOKEN` が git の認証情報としてローカルに保存されます。後続ステップで要らなければ、無効化してください。

```yaml
- uses: actions/checkout@<commit-sha> # vX.Y.Z
  with:
    persist-credentials: false
```

## 信頼性とパフォーマンス

### シェルを `bash` に明示する

`shell` を指定しない `run:` は、Windows 以外のランナーでは `bash -e {0}` で動きます。エラーで止まりますが、パイプの途中の失敗は見逃します。`shell: bash` を明示すると `bash --noprofile --norc -eo pipefail {0}` で動き、パイプの途中の失敗でも止まります。未定義変数も検出したいときは、スクリプトの先頭に `set -u` を足してください。

Windows ランナーの既定シェルは `pwsh` なので、`shell` を指定しないと `set -euo pipefail` はエラーになります。`shell: bash` を指定してください。

```yaml
defaults:
  run:
    shell: bash

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: |
          set -u
          some-command | other-command
```

### timeout-minutes を設定する

既定は 360 分（6 時間）です。暴走ジョブを防ぐため、処理時間の見積もりに合わせた値（例: `timeout-minutes: 10`）を設定してください。

### concurrency で重複実行を防ぐ

同じブランチへの連続プッシュで重複実行が起きないよう、`concurrency` を設定してください。

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref || github.run_id }}
  cancel-in-progress: false
```

デプロイ系ジョブは `cancel-in-progress: false`（待機）、CI チェックは `true`（キャンセル）でも構いません。

### 依存関係キャッシュを活用する

`setup-*` 系アクションの組み込みキャッシュや `actions/cache` で、CI 実行時間を短縮してください。

```yaml
# uv: GitHub ホストランナーでは、キャッシュは既定（enable-cache: auto）で有効になる
- uses: astral-sh/setup-uv@<commit-sha> # vX.Y.Z

# Node.js のキャッシュ例
- uses: actions/setup-node@<commit-sha> # vX.Y.Z
  with:
    node-version: <版>
    cache: 'npm'
```

- `node-version` の `<版>` は書く時点で調べる（例: `mise latest node@lts` で最新の LTS）。
- setup-uv の `enable-cache` は既定の `auto` のままにする。`auto` は、release、タグの push、`pull_request_target`、`workflow_run` ではキャッシュを使わない（キャッシュポイズニング対策）。`enable-cache: true` を明示すると、この保護が外れる。
- リリースやデプロイのような権限の強いワークフローでは、キャッシュを使わない。setup-node では `cache` を指定せず、さらに `package-manager-cache: false` を指定する。`package.json` の `packageManager`（または `devEngines.packageManager`）に npm が書かれていると、`cache` を指定しなくてもキャッシュが自動で有効になるためである。

## メンテナビリティ

### workflow_dispatch を追加する

デバッグや緊急時に再実行できるよう、`on:` に `workflow_dispatch:` を含めてください。

```yaml
on:
  push:
    branches: [main]
  workflow_dispatch:
```

### GitHub CLI (`gh`) 実行時の GH_TOKEN 設定

ステップ内で `gh` を使うときは、`env: GH_TOKEN: ${{ github.token }}` を設定してください。

```yaml
- name: Check PR status
  env:
    GH_TOKEN: ${{ github.token }}
    PR_NUMBER: ${{ github.event.pull_request.number }}
  run: gh pr view "$PR_NUMBER"
```

## AWS 認証

GitHub Actions Runner から AWS リソースにアクセスするときは、`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` をシークレットに保存せず、OIDC で一時的な認証情報を取得してください。OIDC を使うジョブには `id-token: write` と `contents: read` が必要です。AWS 側では、事前に OIDC Identity Provider と IAM ロールを設定します。

```yaml
jobs:
  deploy:
    permissions:
      id-token: write
      contents: read

    steps:
      - uses: actions/checkout@<commit-sha> # vX.Y.Z
        with:
          persist-credentials: false

      - uses: aws-actions/configure-aws-credentials@<commit-sha> # vX.Y.Z
        with:
          role-to-assume: arn:aws:iam::123456789012:role/MyGitHubActionsRole
          aws-region: ap-northeast-1
```

## 静的解析 (`actionlint`)

[actionlint](https://github.com/rhysd/actionlint) は、構文・型・式の誤りとスクリプトインジェクションを、プッシュ前にローカルで検出します。インストールは `mise use actionlint` です。

git フックに組み込むには `hk` を使い、hk の組み込みステップ `Builtins.actionlint` を指定します（`.yml` と `.yaml` の両方が対象になる）。hk の導入と `hk.pkl` の書き方は、`hk` スキルが使える場合はそれに従います。使えない場合は hk の公式ドキュメント（https://hk.jdx.dev/）を参照します。

## デバッグ

ワークフローが失敗したり想定外の動作をしたりするときは、まずデバッグログを有効にして再実行します。GitHub の UI の「Re-run jobs」で「Enable debug logging」を選ぶか、`gh run rerun <run_id> --debug` を使います。

毎回の実行でデバッグログが必要なときは、リポジトリの Settings → Secrets and variables → Actions で、次の変数（またはシークレット）を設定します。両方にある場合はシークレットが優先されます。確認が終わったら削除してください。

| 名前                   | 値     | 効果                             |
| ---------------------- | ------ | -------------------------------- |
| `ACTIONS_STEP_DEBUG`   | `true` | ステップの詳細ログを出力         |
| `ACTIONS_RUNNER_DEBUG` | `true` | ランナー自体のデバッグログを出力 |

実行状況は `gh run list`、`gh run view <run_id> --log-failed`（失敗したステップのログだけ）、`gh run watch <run_id>` で確認します。`gh workflow run <workflow-file-or-name> [--ref <branch>]` で手動トリガーするには、`workflow_dispatch` が必要です。
