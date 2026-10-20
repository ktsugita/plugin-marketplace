# 間違いを戻す

戻す前に、まず今の状態を見せます（`git status`、`git diff`、`git diff --staged`、`git log --oneline -5`）。何が失われるかを説明してから、`SKILL.md` の「操作の段階」に従って進めます。迷ったら、`git reflog` で、手元の HEAD が過去に指していた場所を探せます（すぐ実行）。

| 戻したいもの | 手順 |
| :- | :- |
| `add` したものを取り消す | `git restore --staged <パス>`。ファイルの変更は残ります。 |
| 変更を捨てる（コミット前） | `git diff <パス>` と `git diff --staged <パス>` で失われる内容を見せ、`git restore <パス>`。 |
| 直前の commit を取り消す（push 前、変更は残す） | `git reset --soft HEAD~1`。変更は、`add` 済みのまま残ります。 |
| push 済みの commit を取り消す | `git revert <コミット>`。取り消しの新しい commit を足します。履歴は書き換えません。マージコミットは `-m 1` が要ります（`-m 1` は、マージ先の側を残す指定です）。 |
| 直前の commit のメッセージや内容を直す | push 前なら `git commit --amend`。push 済みなら、`amend` せずに、直しを新しい commit にします。 |
| 追跡していないファイルを消す | `git clean -n` で一覧を見せてから、`git clean -f <パス>`。 |
| すべてやり直す（コミット前も含めて） | `git reflog` で戻り先を探し、`git reset --hard <戻り先>`。 |

## 秘密情報や大きなファイルを commit した

**秘密情報（パスワード、トークン、鍵）は、push 済みなら、その値を失効させることが先です。** ファイルを消して commit し直しても、履歴に残るからです。push 前の値は、手元から出ていないので、失効は必須ではありません。ただし、他の場所（チャット、ログ）に貼った値は、失効させます。迷えば、失効を勧めます。

### まだ commit していない（`add` 済み）

1. `git restore --staged <パス>` で外します。
2. 新しいファイルなら、`.gitignore` に足します。追跡済みのファイルの変更に入っているなら、ファイルから値を取り除いて、`add` し直します。
3. `git diff --staged` で、値が残っていないことを確かめます。

### commit 済み、push 前

`git log --oneline -- <パス>` で、そのファイルを変えたコミットを調べます。

- 秘密が入っているのが直前の commit だけで、そのファイルがその commit で初めて追加されたなら、`git reset --soft HEAD~1` で commit を取り消し（確認を取る）、`git restore --staged <パス>` で外し、`.gitignore` に足してから、commit し直します。
- 古い commit にも入っている、または追跡済みのファイルの変更に入っているなら、ブランチの commit を、1つにまとめ直します。
  1. `git fetch` のあと、ブランチの分岐元を `git merge-base origin/main HEAD` で調べます。
  2. ブランチの commit が1つにまとまることを伝え、確認を取ってから、`git reset --soft <分岐元>` を実行します。
  3. `git restore --staged <パス>` で秘密のファイルを外し（追跡済みなら、値を取り除いて `add` し直し）、`.gitignore` に足します。
  4. `git diff --staged` で、値が残っていないことを確かめて、commit し直します。

今後の追跡を外すには、`git rm --cached <パス>` と `.gitignore` を使います（`.gitignore` だけでは、追跡済みのファイルに効きません）。

### push 済み

値はすでに漏れたものとして扱います。失効が済んでいることを確かめたうえで、履歴の書き換えは、リポジトリの管理者に相談するよう案内します。

大きなファイルは、push 前なら「commit 済み、push 前」と同じ手順で取り除きます（失効は要りません）。push 済みなら、管理者に相談します。

## 間違ったブランチに commit した

`SKILL.md` の「区切りと次の一手」の表にある、「`main` に直接 commit した、ブランチを切り忘れた」に従います。
