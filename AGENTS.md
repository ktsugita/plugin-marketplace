- ユーザとのコミュニケーションは日本語を使用してください
- わかりにくくなるので比喩は避けてください。
- 不明な事や迷う事があればユーザに質問して指示を仰いでください。

- 編集者や利用者に向けた文章は、すべて日本語で書く
- PR のレビューコメントと概要、チャットの返答、説明、提案が対象になる
- コード、コマンド、識別子、ファイル名は原文のままにする
- コミットメッセージに AI ツールの帰属行(Co-Authored-By など)を入れない

- 用語は `GLOSSARY.md` に合わせる
- このリポジトリ固有で、設定ファイルやコードを見ても分からない知識は、`.claude/skills/` のローカルスキルに書く
- 作業でその知識が増えたり変わったりしたら、該当するスキルを更新する
- 該当するスキルがなければ、新しく作る

## Agent skills

### Issue tracker

Issue は GitHub Issues で管理する(`gh` CLI を使用)。`docs/agents/issue-tracker.md` を参照。

### Triage labels

標準の5ラベル(`needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix`)をそのまま使う。`docs/agents/triage-labels.md` を参照。

### Domain docs

single-context(ルートの `GLOSSARY.md` と `docs/adr/`)。`docs/agents/domain.md` を参照。
