# 上流から取り込んでいるファイル

一部のスキルは、外部の Gist(上流)をそのままコピーしたもの。コピーは**改変しない**。調整したいときは、別名のスキルとして追加する(改変すると、上流の更新を差分で追えなくなる)。

## ライセンス

- 作者: k16shikano
- ライセンス: Unlicense。作者が、public gist のすべてに適用すると宣言している。
  - 宣言の Gist: [67625f2a…](https://gist.github.com/k16shikano/67625f2a7d96e3bbdfae8d571a936063/1092e6b60296c760071c308624e344469ec345cf)(取り込み時のリビジョン `1092e6b`)
  - 宣言は secret gist には及ばない。取り込み対象はいずれも public gist。
- 宣言は後から書き換えられうるので、取り込み時のリビジョンをここに記録している。
- このリポジトリ自体のライセンスは MIT(`LICENSE`)。上のスキルには、作者の宣言する Unlicense が適用される。

## 取り込み状況

この表が唯一の記録で、編集者が手で更新する。

| スキル | 上流の Gist | 固定リビジョン | 配置先 |
| :- | :- | :- | :- |
| `japanese-tech-writing` | [fd287c31…](https://gist.github.com/k16shikano/fd287c3133457c4fd8f5601d34aa817d/8f2d57610a73efc97d743c9b0b0ecb1002e09fa4) | `8f2d576` | `plugins/writing/skills/japanese-tech-writing/SKILL.md` |
| `cognitive-rhythm-writing` | [eb2929f1…](https://gist.github.com/k16shikano/eb2929f13ed19c97188393d297be8432/a3b1e26beced71d582e13314fb6f5b179b023c76) | `a3b1e26` | `plugins/writing/skills/cognitive-rhythm-writing/SKILL.md` |

`cognitive-rhythm-writing` は本文で `../japanese-tech-writing/SKILL.md` を参照する。2 つを同じ `skills/` の下に並べ、ディレクトリ名を変えないこと。

## 手順

`gh` が必要(mise で入る)。以下の `<gist>` は Gist の ID(表の URL の `k16shikano/` の次)、`<revision>` は 40 文字のリビジョン、`<配置先>` は表の配置先を指す。

### コピーが固定リビジョンと一致するか確認する

差分が出なければ、コピーは改変されていない。

```bash
tmp=$(mktemp)
gh api gists/<gist>/<revision> --jq '.files["SKILL.md"].content | rtrimstr("\n")' > "$tmp"
git diff --no-index --exit-code -- "$tmp" <配置先>
```

### 上流に更新があるか確認する

出力が表の固定リビジョンと違えば、上流に更新がある。

```bash
gh api gists/<gist> --jq '.history[0].version'
```

### 更新を取り込む

1. 上の確認と同じ形で、新しいリビジョンの内容を配置先に書き込む(`<revision>` を新しいリビジョンにし、出力先を `<配置先>` にする)。
2. `git diff` で差分を読み、問題がなければ、表の URL と「固定リビジョン」を新しいリビジョンに更新する。
3. ライセンスの宣言が変わっていないかも確かめる。`gh api gists/67625f2a7d96e3bbdfae8d571a936063 --jq '.history[0].version'` の出力が、上の「取り込み時のリビジョン」と違えば、宣言の内容を読み直す。
4. commit する。上流のコピーの変更は `pre-commit` の `upstream-guard` が止めるので、このときだけ `HK_SKIP_STEPS=upstream-guard git commit ...` のように止めを外す。

### 新しい上流を足す

1. 作者と、ライセンスの宣言を確かめる。必要なら、「ライセンス」の節に追記する。
2. 「更新を取り込む」の手順 1 と同じ形で、配置先に取得する。
3. 「取り込み状況」の表に行を足す。
4. `hk.pkl` の `upstream-guard` の `glob` に、配置先を足す。
