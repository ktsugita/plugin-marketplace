# 上流から取り込んでいるファイル

`writing` の 2 スキルは、外部の Gist(上流)をそのままコピーしたもの。コピーは**改変しない**。調整したいときは、別名のスキルとして追加する(改変すると、上流の更新を差分で追えなくなる)。取り込み元と、取り込んだ版(リビジョン)は、[upstream.toml](./upstream.toml) に記録している。

## ライセンス

- 作者: k16shikano
- ライセンス: Unlicense。作者が、public gist のすべてに適用すると宣言している。
  - 宣言の Gist: [67625f2a…](https://gist.github.com/k16shikano/67625f2a7d96e3bbdfae8d571a936063/1092e6b60296c760071c308624e344469ec345cf)(取り込み時のリビジョン `1092e6b`)
  - 宣言は secret gist には及ばない。取り込み対象はいずれも public gist。
- 宣言は後から書き換えられうるので、取り込み時のリビジョンをここに記録している。
- このリポジトリ自体のライセンスは MIT(`LICENSE`)。上のスキルには、作者の宣言する Unlicense が適用される。

## 取り込み元

| スキル | 上流の Gist |
| :- | :- |
| `japanese-tech-writing` | [fd287c31…](https://gist.github.com/k16shikano/fd287c3133457c4fd8f5601d34aa817d) |
| `cognitive-rhythm-writing` | [eb2929f1…](https://gist.github.com/k16shikano/eb2929f13ed19c97188393d297be8432) |

`cognitive-rhythm-writing` は本文で `../japanese-tech-writing/SKILL.md` を参照する。2 つを同じ `skills/` の下に並べ、ディレクトリ名を変えないこと。

## 更新する

1. `mise run upstream:update` を実行する。最新の版を取得して、スキルを上書きし、`upstream.toml` のリビジョンを書き換える。
2. `git diff` で差分を読む。差分がなければ、上流に更新はない。
3. 問題がなければ commit する。上流のコピーの変更は `pre-commit` の `upstream-guard` が止めるので、このときだけ `HK_SKIP_STEPS=upstream-guard git commit ...` のように止めを外す。
4. ライセンスの宣言が変わっていないかを確かめる。`gh api gists/67625f2a7d96e3bbdfae8d571a936063 --jq '.history[0].version'` の出力が、上の「取り込み時のリビジョン」と違えば、宣言の内容を読み直す。
