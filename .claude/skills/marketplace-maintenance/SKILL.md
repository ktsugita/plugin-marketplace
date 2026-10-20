---
name: marketplace-maintenance
description: このリポジトリのプラグインやスキルを追加、修正、削除するとき、`plugin.json` や `marketplace.json` を編集するとき、上流のスキルに触れるときに使う。点検では判定できない、このリポジトリ固有の判断基準を定める。
---

# marketplace の保守で守る判断基準

作業の手順は `CONTRIBUTING.md` に書いてある。`version` と `dependencies` を書かないことは、`hk` の点検(`policy`)が止める。ここには、点検では判定できない判断基準だけを置く。

## 上流のスキルを調整するとき

- 上流のコピー(`UPSTREAM.md` に挙げたスキル)は直さない。次の `mise run upstream:update` で上書きされ、手入れが消える。調整したい内容があれば、別名のスキルを足す。

## `coding` と `mattpocock-skills`

- スキルの本文で `mattpocock-skills` に触れるときは、「入っていれば使う」と書き、入っていないときの動作も書く。

## 公開リポジトリとして守ること

- 旧リポジトリ(`bnba-infra`)の名前や、社内向けの記述を持ち込まない。
- 絶対パス、認証情報、個人の環境に依存する記述を入れない。
- `marketplace.json` の `plugins` と `plugins/` 配下のディレクトリを、常に一致させる。
