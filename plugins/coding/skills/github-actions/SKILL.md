---
name: github-actions
description: .github/workflows/ 配下のワークフローの作成・編集、GitHub Actions のセキュリティ対策（permissions、スクリプトインジェクション防止、ロックファイル actions.lock による依存の固定）、デバッグを行うときに使用する。
license: MIT
---

# GitHub Actions の規約とデバッグ

ワークフローを作成・編集したら、セキュリティと信頼性の必須原則を適用し、最後に `jactionlint` で検証します。

## 必須の原則（セキュリティ・信頼性）

### 1. `permissions` を最小限にする

設定に左右されないよう、トップレベルで既定の権限を絞り（`permissions: contents: read` または `permissions: {}`）、書き込み権限が必要なジョブにだけ個別に付与します。`write-all` は使いません。

### 2. スクリプトインジェクションを防ぐ

`${{ github.event... }}` や `${{ inputs... }}` などの外部入力を `run:` に直接展開せず、必ず中間環境変数（`env:`）を介してシェル変数として参照します。ステップ内で `gh` を使うときも `env: GH_TOKEN: ${{ github.token }}` を渡します。

```yaml
- name: Check PR status
  env:
    GH_TOKEN: ${{ github.token }}
    PR_NUMBER: ${{ github.event.pull_request.number }}
  run: gh pr view "$PR_NUMBER"
```

### 3. ワークフローの依存をロックファイルで固定する

タグ（`@v4` など）やブランチは付け替えられうるため、[gh-actions-lock](https://github.com/github/gh-actions-lock) で、直接・間接のすべてのアクションを検証済みの commit に固定し、`.github/workflows/actions.lock`（Workflow Lockfiles）に記録します。`uses:` は読みやすいタグのまま書き、commit SHA には書き換えません。

```bash
gh extension install github/gh-actions-lock
gh actions-lock            # 固定して actions.lock を書く
gh actions-lock --verify   # 確認する(書き込まない)
```

- ワークフローを追加したときと、`uses:` を手で変えたときは `gh actions-lock` を再実行し、`actions.lock` を同じ commit に含めます。
- ロックファイルを導入済みのワークフローでは、Dependabot が同じ PR で `actions.lock` を更新します。PR に `actions.lock` の変更が含まれないときだけ、再実行します。バージョン更新は、引き続き `.github/dependabot.yml`（`package-ecosystem: github-actions`、`cooldown: default-days: 7`）に任せます。
- CI では `gh actions-lock --verify` を実行します。`--verify-local` はロックファイルに記載があるかしか見ないため、CI の代わりになりません。タグの付け替えを検知する定期実行（`schedule:`）も足します。
- `--accept-moved` は、固定した commit が履歴から消えた理由を人が確かめてから使います。CI や定期実行などの自動化では使いません。改ざんされた固定を黙って受け入れてしまうためです。

コマンドの全体、findings の読み方、`local-action` への対処は、公式スキル（`gh skill install github/gh-actions-lock` で導入）に従います。入っていなければ、[公式の README](https://github.com/github/gh-actions-lock#readme) を読みます。ロックファイルの対象外、対応する環境と版、部分バージョンの書き換え、`verify-lockfile.yml` の取り込み方を確かめたいときは、[references/gh-actions-lock.md](references/gh-actions-lock.md) を読みます。

### 4. `actions/checkout` に `persist-credentials: false` を付ける

後続ステップで git の認証情報が不要なら、`with: persist-credentials: false` を指定してローカルへの `GITHUB_TOKEN` 保存を防ぎます。

### 5. シェルとタイムアウトを明示する

- `run:` には `shell: bash` を明示します（`defaults.run.shell: bash` でも可）。指定しないと Windows ランナーでは既定が `pwsh` になり、Linux / macOS でも `-o pipefail` が付かない `bash -e {0}` になります。未定義変数も止める場合は先頭に `set -u` を足します。
- 各ジョブに処理時間に見合った `timeout-minutes`（例: `10`）を設定します（既定は 360 分）。

## 用途別の設定

- **`concurrency`**: 同一ブランチへの連続 push による重複実行を防ぐため、`group: ${{ github.workflow }}-${{ github.ref || github.run_id }}` を設定します（CI は `cancel-in-progress: true`、デプロイ系は `false`）。
- **キャッシュと権限境界**:
  - 通常の CI では `setup-*` の組み込みキャッシュを活用します（`astral-sh/setup-uv` の `enable-cache` はキャッシュポイズニング保護が働く既定の `auto` のままにし、`true` を明示しない）。
  - **リリースやデプロイなど強い権限を持つワークフローではキャッシュを使いません。** `actions/setup-node` は `package.json` に `packageManager` があると自動でキャッシュを有効にするため、強権限のワークフローでは `package-manager-cache: false` を明示します。
- **`workflow_dispatch`**: 手動再実行や検証が必要なワークフローには `on:` に `workflow_dispatch:` を含めます。
- **AWS 認証**: 長期アクセスキーをシークレットに置かず、`aws-actions/configure-aws-credentials` と OIDC（`permissions: id-token: write, contents: read`）で一時認証情報を取得します。

## 静的解析（`jactionlint`）とデバッグ

- **静的解析**: [jactionlint](https://github.com/jdx/jactionlint)（`mise use jactionlint`）でワークフロー、composite action、`dependabot.yml` の構文・型・セキュリティ問題を検証します。git フックに組み込むときは `hk` 2.6.0 以上の `Builtins.jactionlint` を使います（`hk.pkl` の `amends` / `import` の参照先の版も 2.6.0 以上であることを確かめます。`hk` スキルを参照）。
- **ロックファイルの検証**: git フックには `gh actions-lock --verify-local` を載せられます。ネットワークを使わず、`uses:` ごとに `actions.lock` の記載があるかを確かめます。記載の中身が信頼できるかは見ないため、CI の `--verify` の代わりにはなりません。
- **デバッグ**:
  - 失敗ログの確認: `gh run list`、`gh run view <run_id> --log-failed`、`gh run watch <run_id>`。
  - デバッグ再実行: `gh run rerun <run_id> --debug`（継続的に出す場合はリポジトリの Actions 変数 `ACTIONS_STEP_DEBUG=true` / `ACTIONS_RUNNER_DEBUG=true` を一時設定し、調査後に削除する）。
