# 公開への切り替え

作成のあとに「公開したい」と言われたら、「公開の準備ができてから切り替えましょう」と伝え、切り替える前に次を利用者と確かめます。

- 履歴と設定に、パスワード、トークン、個人情報が入っていないこと。公開すると、過去のコミットも、Actions の履歴とログも、誰でも読めるようになります。
- `README.md` と `LICENSE` が、公開してよい内容であること。

確認を取ってから、`gh repo edit <owner>/<repo> --visibility public --accept-visibility-change-consequences` を実行します。確認では、誰でもフォークできること、非公開に戻しても、すでにできた公開のフォークは、元から切り離されて残ることを伝えます(出典: GitHub Docs の「Setting repository visibility」)。
