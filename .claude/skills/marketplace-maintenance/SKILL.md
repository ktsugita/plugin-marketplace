---
name: marketplace-maintenance
description: このリポジトリのプラグインやスキルを追加、修正、削除するとき、`plugin.json` や `marketplace.json` を編集するとき、上流のスキルに触れるときに使う。コードや設定を見ても分からない、このリポジトリ固有の判断基準を定める。
---

# marketplace の保守で守る判断基準

作業の手順は `CONTRIBUTING.md` に書いてある。ここには、手順に書かれない判断基準だけを置く。

## 上流のコピーは改変しない

- `UPSTREAM.md` の表にあるスキル(`plugins/writing/skills/` の 2 つ)は、外部 Gist の無改変のコピーである。内容を直さない。誤字や表現も直さない。
- 調整したいときは、別名のスキルを足す。直すと、上流の更新を差分で追えなくなる。
- 上流の更新を取り込んだら、`UPSTREAM.md` の表の固定リビジョンも、同じ変更で更新する。

## `version` を付けない

- `plugin.json` と `marketplace.json` に `version` を足さない。このリポジトリは、commit ごとに利用者へ更新を届ける運用にしている。
- `claude plugin validate` が出す `version` の警告は、想定どおりなので、消すために `version` を足さない。

## `coding` は `mattpocock-skills` を必須にしない

- `plugin.json` に `dependencies` を足さない。別の marketplace のプラグインを、利用者に先に入れさせることになるため。
- スキルの本文で `mattpocock-skills` に触れるときは、「入っていれば使う」と書き、入っていないときの動作も書く。

## 公開リポジトリとして守ること

- 旧リポジトリ(`bnba-infra`)の名前や、社内向けの記述を持ち込まない。
- 絶対パス、認証情報、個人の環境に依存する記述を入れない。
- `marketplace.json` の `plugins` と `plugins/` 配下のディレクトリを、常に一致させる。
