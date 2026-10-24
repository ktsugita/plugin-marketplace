# CONTRIBUTING

編集者(このリポジトリに変更を加える人)向けの手順と規約。プラグインを入れて使うだけの利用者は [README.md](./README.md) を読む。用語は [GLOSSARY.md](./GLOSSARY.md) に合わせる。

## 準備

1. [mise](https://mise.jdx.dev/) を入れ、リポジトリのルートで `mise install` を実行する。`gh`、`hk`、`uv`、`jactionlint` が入り、git のフックも入る。Python の依存(`ruff`、`ty`、`pytest`)は、初回の `uv run` が `uv.lock` どおりに入れる。
2. Claude Code を入れる。`mise run validate` が `claude plugin validate` を呼ぶ。mise の管理外なので、別に入れる。

## 点検

| 目的 | コマンド |
| :- | :- |
| リポジトリ全体を点検し、テストを走らせる | `mise run check` |
| テストだけを走らせる(`pre-push` でも走る) | `mise run test` |
| `marketplace.json`、`plugin.json`、スキルの定義だけを検証する | `mise run validate` |
| `version` と `dependencies` を書いていないことを点検する | `mise run policy:check` |
| `AGENTS.md` と `.github/copilot-instructions.md` の共通部分が一致することを点検する | `mise run agents-sync:check` |
| コミットメッセージを点検する | `mise run commit-msg:check -- <メッセージのファイル>` |

- `validate` が `version` を指定していない警告を出すのは、想定どおり。このリポジトリは `version` を付けず、commit ごとに利用者へ更新を届ける。警告以外の指摘が出たときは直す。
- `AGENTS.md` の「`## Agent skills`」より前を変えたときは、`.github/copilot-instructions.md` も同じ内容にする。Copilot Review は、後者を読む。

## プラグインを足す

1. `plugins/<名前>/.claude-plugin/plugin.json` を作る。`author`、`repository`、`license` は既存のプラグインと同じにする。
2. `plugins/<名前>/skills/` の下にスキルを置く。
3. `.claude-plugin/marketplace.json` の `plugins` に、名前、`source`、説明、カテゴリ、タグを足す。
4. `mise run validate` を実行する。
5. `README.md` の「プラグイン」の表に行を足す。

## スキルを足す・直す

- スキルは `plugins/<プラグイン>/skills/<名前>/SKILL.md` に置く。フロントマターの `name` はディレクトリ名と同じにする。
- `description` には、何をするスキルかと、どんなときに使うかを書く。
- 編集者に向けた文章は日本語で書く。コード、コマンド、識別子、ファイル名は原文のままにする。
- `coding` のスキルは、`mattpocock-skills` を必須にしない。入っていれば使い、入っていなくても動くように書く。

## 上流のスキルを取り込む・更新する

`writing` の 2 スキルは、外部の Gist のコピー。コピーは改変しない。`mise run upstream:update` で最新の版に更新する。手順は [UPSTREAM.md](./UPSTREAM.md) に従う。

## コミット

- メッセージは日本語で書く。1 行目で何を変えたかを書き、本文で理由や内訳を書く。
- AI ツールの帰属行(`Co-Authored-By` など)は入れない。`commit-msg` フックが止める。
