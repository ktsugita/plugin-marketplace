# plugin-marketplace

自作のプラグインを公開する。marketplace としても利用できる。

## プラグイン

| プラグイン | 内容 |
| :- | :- |
| `coding` | コード開発者向けの規約集(mise、hk、GitHub Actions、Git の設定、Python、PowerShell)を、AI エージェントが従う形で定める。あわせて、GitHub 初学者に Git、Issue、Pull Request の使い方と、リポジトリの初期設定を案内する。 |
| `writing` | 日本語の技術文書を書く・推敲するための文章規範。k16shikano 氏の Gist 2 本(`japanese-tech-writing`、`cognitive-rhythm-writing`)を、改変せずに同梱している。 |

## 使い方

### 前提条件

次のどちらかが入っていること。

- Claude Code
- GitHub Copilot CLI

[`mattpocock-skills`](https://github.com/mattpocock/skills) プラグインも入れることを推奨する。`coding` の一部のスキルが、入っていればそれも使う(`github-pr` の PR 本文のテンプレートなど)。入っていなくても `coding` は使える。入れ方は「mattpocock-skills も入れる」を参照。

### Claude Code に入れる

```bash
claude plugin marketplace add ktsugita/plugin-marketplace
claude plugin install coding@ktsugita
claude plugin install writing@ktsugita
```

Claude Code の中では、`/plugin marketplace add ktsugita/plugin-marketplace` と `/plugin install coding@ktsugita` のように入力しても同じ。

### GitHub Copilot CLI に入れる

```bash
copilot plugin marketplace add ktsugita/plugin-marketplace
copilot plugin install coding@ktsugita
copilot plugin install writing@ktsugita
```

### mattpocock-skills も入れる

別の marketplace(`mattpocock/skills`)から入れる。使うツールに合わせて実行する。

Claude Code:

```bash
claude plugin marketplace add mattpocock/skills
claude plugin install mattpocock-skills@mattpocock
```

GitHub Copilot CLI:

```bash
copilot plugin marketplace add mattpocock/skills
copilot plugin install mattpocock-skills@mattpocock
```

## 不具合や要望

[Issue](https://github.com/ktsugita/plugin-marketplace/issues) で受け付けている。Pull Request は、原則として受け付けていない。

## ライセンス

[MIT](./LICENSE)。ただし、`writing` に同梱するスキルには、作者が宣言する Unlicense が適用される。取り込み元とリビジョンは [UPSTREAM.md](./UPSTREAM.md) に記録している。
