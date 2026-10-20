# 上流から取り込んでいるファイル

一部の skill は、外部の Gist をそのままコピーしたもの。コピーは**改変しない**。社内向けに調整したいときは、別名の skill として追加する（改変すると、上流の更新を差分で追えなくなる）。

## ライセンス

- 作者: k16shikano
- ライセンス: Unlicense。作者が、public gist のすべてに適用すると宣言している。
  - 宣言の Gist: [67625f2a…](https://gist.github.com/k16shikano/67625f2a7d96e3bbdfae8d571a936063/1092e6b60296c760071c308624e344469ec345cf)（取り込み時のリビジョン `1092e6b`）
  - 宣言は secret gist には及ばない。取り込み対象はいずれも public gist。
- 宣言は後から書き換えられうるので、取り込み時のリビジョンをここに記録している。

## 取り込み状況

<!-- upstream-table:start -->
| skill | 元 Gist | 固定リビジョン | 配置先 |
| :- | :- | :- | :- |
| `japanese-tech-writing` | [fd287c31…](https://gist.github.com/k16shikano/fd287c3133457c4fd8f5601d34aa817d/8f2d57610a73efc97d743c9b0b0ecb1002e09fa4) | `8f2d576` | `plugins/writing/skills/japanese-tech-writing/SKILL.md` |
| `cognitive-rhythm-writing` | [eb2929f1…](https://gist.github.com/k16shikano/eb2929f13ed19c97188393d297be8432/a3b1e26beced71d582e13314fb6f5b179b023c76) | `a3b1e26` | `plugins/writing/skills/cognitive-rhythm-writing/SKILL.md` |
<!-- upstream-table:end -->

`upstream.json` が正で、上の表は `node scripts/sync-upstream.mjs --render` で再生成される（手で編集しない）。

`cognitive-rhythm-writing` は本文で `../japanese-tech-writing/SKILL.md` を参照する。2 つを同じ `skills/` の下に並べ、ディレクトリ名を変えないこと。

## 操作

Node.js 18 以上があればよい（依存パッケージなし）。

| 目的 | コマンド |
| :- | :- |
| 初回の取得・コピーの復元 | `node scripts/sync-upstream.mjs` |
| コピーが固定リビジョンと一致するか確認 | `node scripts/sync-upstream.mjs --verify` |
| 上流に更新があるか確認（変更しない） | `node scripts/sync-upstream.mjs --check` |
| 最新リビジョンへ固定し直す | `node scripts/sync-upstream.mjs --update` |

## 定期チェック

`.github/workflows/sync-upstream.yml` が毎週月曜に `--update` を実行し、差分があれば PR を作る。PR の差分を読み、問題がなければマージする。

- リポジトリの Settings > Actions > General で「Allow GitHub Actions to create and approve pull requests」を有効にしておく。
- `GITHUB_TOKEN` で作った PR では、他のワークフロー（`validate`）が自動では動かない。マージ前に手元で `node scripts/validate.mjs` と `node scripts/sync-upstream.mjs --verify` を実行する。

## 新しい上流を足す

1. `upstream.json` の `sources` に、`id`、`gist`（`作者/ID`）、`revision`（40 文字）、`file`、`dest` を足す。
2. ライセンスを確認し、必要なら上の「ライセンス」に追記する。
3. `node scripts/sync-upstream.mjs` で取得し、`node scripts/sync-upstream.mjs --render` で表を更新する。
