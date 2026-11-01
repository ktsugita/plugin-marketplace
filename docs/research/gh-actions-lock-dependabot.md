# gh-actions-lock と Dependabot、公式スキル、`uses:` の書き方

調査日は 2026-11-01。一次情報だけを根拠にする。確認できなかった点は「確認できなかった」と書く。

対象は次の 3 点である。

1. Dependabot は `actions.lock` を更新するか
2. 公式スキルの導入方法と場所
3. `uses:` をタグのまま書く運用が想定どおりか、`gh actions-lock` が workflow を書き換える場面はどこか

## 調査対象の版

- github/gh-actions-lock: main のコミット 113f91d。最新リリースは v0.4.0(2026-10-23)。出典: `gh release list -R github/gh-actions-lock`
- dependabot/dependabot-core: main のコミット 85379652e4ef784fdd38bf4598b0b347832f805b
- 以下で「README」「skill」「troubleshooting」と書くものは、gh-actions-lock リポジトリの次のファイルを指す。
  - README: https://github.com/github/gh-actions-lock/blob/main/README.md
  - skill: https://github.com/github/gh-actions-lock/blob/main/skills/gh-actions-lock/SKILL.md
  - troubleshooting: https://github.com/github/gh-actions-lock/blob/main/docs/troubleshooting.md
- docs.github.com の 3 ページは、ページ全文を取得して要約させる方法で読んだ。逐語の引用は、取得ツールが返した文に限る。節の見出し(「Keep the lockfile current」など)は取得結果に基づく。行番号は付けられない。

## 結論

- 問1: Dependabot は、導入(onboard)済みのワークフローについて、同じ PR 内で `actions.lock` の該当エントリを再生成する。したがって Dependabot の PR で `gh actions-lock --verify` が失敗する、という前提は成り立たない。導入前のワークフローは触らない。`cooldown` は gh-actions-lock 側で通知(`fresh-tag`)にだけ使う。
- 問2: `gh skill install github/gh-actions-lock`。スキルの場所は同リポジトリの `skills/gh-actions-lock/SKILL.md` である。
- 問3: 公式は、タグのまま `uses:` に書く運用を想定している。`gh actions-lock` は、`--migrate-local-actions` 以外でも、初回の固定時に `uses:` の部分バージョン(`v4`)を完全なタグ(`v4.2.1`)へ書き換える。

## 1. Dependabot と `actions.lock`

### 1.1 Dependabot は `actions.lock` を更新するか

更新する。ただし対象は、導入済みのワークフローに限る。

- 公式の手順は、Dependabot が導入済みワークフローのアクションを更新すると、同じ PR で該当の lockfile エントリを更新すると説明している。導入していないワークフローでは lockfile に触れない。出典: https://docs.github.com/en/actions/how-tos/secure-your-work/lock-workflow-dependencies の「Keep the lockfile current」の Dependabot の項。取得ツールが返した原文は "Dependabot only updates lockfile entries for workflows that are already onboarded."
- 管理者向けの文書も同じ内容である。"When Dependabot bumps an action version, it regenerates the matching lockfile entry in the same pull request." と "You don't need any configuration beyond having Dependabot manage GitHub Actions dependencies." と書かれている。"Dependabot will **not** onboard a workflow that has no lockfile entries yet" とも書かれている。出典: https://docs.github.com/en/actions/how-tos/administer/enforce-workflow-lockfiles の「Dependabot」節。
- 概念の文書は、lockfile が構造化された形式であり、Dependabot のようなツールが YAML コメントのバージョン注釈に頼らずに依存の更新を管理できると説明している。出典: https://docs.github.com/en/actions/concepts/security/workflow-dependency-lockfiles の「What does the lockfile record?」。
- 実装でも確認できた。dependabot-core の `github_actions` エコシステムは `actions.lock` を扱う。
  - 更新対象の workflow が lockfile で導入済みのときだけ、gh-actions-lock の CLI を呼んで lockfile を再生成し、更新ファイルに含める。導入済みでないワークフローと、lockfile のないリポジトリでは、従来どおりの正規表現による書き換えだけを行う。出典: https://github.com/dependabot/dependabot-core/blob/85379652e4ef784fdd38bf4598b0b347832f805b/github_actions/lib/dependabot/github_actions/file_updater.rb の `relocked_files`(L57-95)。
  - CLI の呼び出しは `Lockfile::CliEngine#relock` である。出典: 同 `github_actions/lib/dependabot/github_actions/lockfile/cli_engine.rb`。
  - 導入済みかどうかの判定は `Lockfile::Reader#onboarded?` である。出典: 同 `update_checker.rb` の `onboarded_requirement?`(L115-129)。
  - lockfile のバージョンが未対応の場合は `VersionGate.assert_supported!` で拒否する。出典: 同 `file_updater.rb` L83。
- 制約: 上のコードは dependabot-core の main ブランチである。GitHub がホストする Dependabot の本番環境に、いつ反映されたかは確認できなかった。ただし docs.github.com の記述は、本番での動作を前提にしている。

### 1.2 Dependabot の PR で `gh actions-lock --verify` は失敗するか

導入済みのワークフローを更新する PR では、失敗しない想定である。根拠は 1.1 の「同じ PR で lockfile を再生成する」という記述と実装である。

次の場合の挙動は、一次情報から確認できなかった。

- Dependabot が lockfile を再生成できず、PR に `actions.lock` の更新が含まれない場合(CLI のエラー、未対応のバージョンなど)の PR 上の結果。コードは例外を送出するが、PR がどう扱われるかは確認していない。
- 導入前のワークフローの PR。docs は lockfile に触れないと説明している。ただし導入前なら、そのワークフローは lockfile に載っていないため、`--verify` の扱いは確認できなかった。
- Dependabot のセキュリティ更新が `actions.lock` を更新するか。管理者向け文書の「Updating the lockfile」には "Keep the lockfile up to date with your repository's workflow files and security updates." という文がある。ただし、この文が Dependabot のセキュリティ更新を指すのかは、読み取れなかった。

### 1.3 運用上の対処は公式に示されているか

Dependabot が更新しない場合の対処は、見つからなかった。理由は、公式が「Dependabot が更新する」前提だからである。示されている近い対処は次のとおり。

- 管理者向け文書「Updating the lockfile」: push 時に lockfile を再生成してコミットする **update** ジョブを置く方法が書かれている。出典: https://docs.github.com/en/actions/how-tos/administer/enforce-workflow-lockfiles 。ジョブの書き方は取得結果から確認できなかった。lockfile への書き込みには `workflow` OAuth スコープが要るという記述がある("Writing to the lockfile requires the `workflow` OAuth scope")。
- 同「Verification」: `gh actions-lock --verify` を PR で実行する **verify** ジョブ。lockfile が古いときにエラー終了するので、必須チェックに向く、と書かれている。
- 公式リポジトリの `.github/workflows/verify-lockfile.yml` は、`pull_request` と `main` への push で `gh actions-lock --verify` を実行する。出典: https://github.com/github/gh-actions-lock/blob/main/.github/workflows/verify-lockfile.yml L6-25。
- 公式が「Dependabot の PR 上で再実行する」運用を明示している記述は、確認できなかった。
- 手動で直す場合の一般的な手順は、lockfile を壊したときの手順として troubleshooting にある。「Restoring the lockfile」節(`git checkout origin/DEFAULT-BRANCH -- .github/workflows/actions.lock` のあと `gh actions-lock`)。Dependabot のブランチ向けの手順ではない。

### 1.4 `cooldown` との関係

- gh-actions-lock は `.github/dependabot.yml` の `github-actions` の `cooldown` を読み、`fresh-tag` の通知にだけ使う。`cooldown` の期間内に公開されたタグに固定すると、通知が出る。出典: troubleshooting の `fresh-tag` 節(L297-303)。
- `gh actions-lock` は `cooldown` を理由にリリースを止めない。同 L303 に "`gh actions-lock` doesn't hold back a release because of the cooldown setting. It only uses the setting for this notice." とある。
- `cooldown` を設定していないときは、直近 3 日以内のリリースを対象にする。同 L301。
- 読み取るのは `default-days` だけである。`semver-major-days` や `include` などは使わず、`cooldown-config-ignored` の通知が出る。出典: troubleshooting L305-307。公式リポジトリ自身の `.github/dependabot.yml` の冒頭コメントにも、"it honors only default-days" とある。
- Dependabot 側では、導入済みワークフローの更新でも `latest_version_tag_respecting_cooldown` を使い、`cooldown` を尊重する。出典: dependabot-core の `update_checker.rb` L283-284、L364-367(上記コミット)。
- docs.github.com の Dependabot オプション一覧は、`github-actions` で `default-days` が対応、`semver-*-days` が非対応と示している(取得結果の要約による。ページの後半 82,000 文字は未読)。出典: https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference 。このページに `actions.lock` への言及は、読んだ範囲では見つからなかった。

## 2. 公式スキルの導入

### 2.1 コマンド

- README に `gh skill install github/gh-actions-lock` と書かれている("To teach your AI coding agent the CLI")。出典: README L13-17。
- `gh skill install` の書式は `gh skill install <repository> [<skill[@version]>] [flags]` である。第 1 引数が `OWNER/REPO` 形式のリポジトリ、第 2 引数がスキル名(省略可)。出典: `gh skill install --help`(gh 2.103.3 で確認)。
- 非対話で実行するときは、スキル名か `--all` を指定しない場合、見つかったスキルの一覧が表示されるだけである。同ヘルプ。一覧に出るスキルは 1 つ(下記)なので、README のコマンドで足りるかどうかは、対話・非対話で動作が違う可能性がある。実際のインストールは試していない(確認できなかった)。
- 配置先は `--agent` と `--scope`(`project` が既定、`user` も選べる)で決まる。Claude Code は `--agent claude-code`。同ヘルプ。
- バージョンは `@VERSION` か `--pin` で固定できる。指定しなければ、最新のタグ付きリリース、なければ既定ブランチの HEAD である。同ヘルプ。

### 2.2 スキルの場所

- リポジトリの `skills/gh-actions-lock/SKILL.md`。`skills/` 配下のスキルは、このディレクトリ 1 つだけである。出典: https://github.com/github/gh-actions-lock/tree/main/skills/gh-actions-lock (`gh api` で一覧を確認)。
- スキルの名前は `gh-actions-lock`。出典: 同 SKILL.md の frontmatter L2。
- なお、この調査は、docs.github.com の 3 ページにスキルへの言及がないことを確認している(取得結果)。公式スキルの導入方法は README だけに書かれている。

## 3. `uses:` の書き方と workflow の書き換え

### 3.1 タグのまま書く運用は想定か

想定している。

- 概念の文書は、lockfile を採用するリポジトリでは workflow 内の SHA 固定は不要になる("For repositories that adopt a lockfile, SHA pinning within workflow files is **no longer necessary**.")と述べている。lockfile の利点として、workflow ファイルが読みやすくなる点も挙げている。出典: https://docs.github.com/en/actions/concepts/security/workflow-dependency-lockfiles の「How do lockfiles compare with SHA pinning?」。
- lockfile は、"Creating a lockfile pins your dependencies to commits based on the current branch or tag reference." と説明されている。出典: how-to の「Check your action references」。
- 公式リポジトリ自身の workflow も、タグで書いている(`actions/checkout@v7.0.1`)。出典: https://github.com/github/gh-actions-lock/blob/main/.github/workflows/verify-lockfile.yml L21。
- 注意点(公式が勧める書き方): 完全なバージョンタグ(`v4.2.1`)は 1 つのコミットを指す。部分バージョン(`v4`)は、リリースのたびに動く。troubleshooting の `version-ref` 節は、`uses:` を完全なタグに変えることを勧める(同ファイル L309-)。ブランチ(`main`)と部分バージョンは、固定したコミットのまま `ref-moved` の警告になる。完全なタグは、固定したコミットと一致しなければエラーになる。出典: how-to の「Keep the lockfile current」の Moved references の項。
- アクション許可リスト(allowlist)との関係: 導入済みのワークフローでは、許可リストが、タグではなく固定したコミット SHA と照合される。タグで書いた許可リストのエントリ(`actions/checkout@v6`)は一致しなくなる。ワイルドカードか完全な SHA を使う。出典: how-to の「Review the changes and commit」。

### 3.2 `gh actions-lock` が workflow を書き換える場面

`--migrate-local-actions` 以外にも、次の場面がある。

1. 部分バージョンの narrowing。初めて固定するとき、`v4` のような部分バージョンを、一致する最も高い完全なタグ(`v4.2.1`)に書き換える。`--no-narrow` で止められる。
   - 出典: skill L59(「Partial versions (`v4`) are narrowed to the highest matching full tag (`v4.2.1`) when first pinned」)、README L66、troubleshooting の `version-ref` 節。
   - how-to も、"It also rewrites your workflow `uses` references to the specific version it resolved,"(例: `octo-org/deploy-action@v3` が `@v3.1.0` になりうる)と述べ、書き換えた行を確認するよう求めている。出典: how-to の「Review the changes and commit」。
   - 実装では、`--no-narrow` が `opts.noNarrow` として扱われ、`pin.Plan` が narrowing を行う。出典: https://github.com/github/gh-actions-lock/blob/113f91d/cmd/gh-actions-lock/run.go L46-49、L86-89、L446-457。なお「narrowing は `uses:` の `ref` だけを変え、コミットは変えない」という点は、how-to の記述(コミットは変わらない)に依拠した。コードの詳細は追っていない。
   - 対象は、セマンティックバージョンとして解釈できる参照だけである。ブランチ名(`main`)や、バージョンでないタグは narrowing されない。出典: run.go L86-89 のフラグ説明。
2. `--migrate-local-actions`。同じリポジトリの `./…` を `$/…` に書き換える。workflow と、リポジトリ内の `action.yml` が対象である。出典: README L73、how-to の同節、run.go L103-104、L266-273。
3. 書き込みの範囲について。書き込みは全部成功するか、全く行わないかのどちらかである(skill L55 付近の "Writes are all or nothing")。lockfile の更新と同じ変更に、workflow の編集が含まれることがあるため、同じコミットに含める(skill の「Onboarding and fixing」節)。
4. 読み取り専用のモード(`--verify`、`--verify-local`、`--no-fix`)は書き込まない。出典: README L51-58 の表(Writes 列)。

次の点は確認できなかった。

- 2 回目以降の実行で、既に固定済みのエントリについて workflow を書き換える場面があるか。README と skill は「固定したコミットは sticky で、通常の実行は lockfile に記録のない参照だけを解決する」と述べる(skill L55 付近)。`--relock` が `uses:` の記述を変えるかは、確認できなかった。

## 4. 本リポジトリの SKILL.md への含意

下のうち、1 から 3 は一次情報で確認できた。4 と 5 は、気づいた点の記録である。

1. 原則 3 の「Dependabot の更新を含む」場合に `gh actions-lock` を再実行して `actions.lock` を同じコミットに含める、という指示は、公式の説明(導入済みなら Dependabot が同じ PR で更新する)より手間が多い。Dependabot の PR では、再実行が不要な場合が多いはずである。再実行が必要な場合(導入前のワークフロー、再生成の失敗)は、1.2 のとおり確認できなかった。記述を「Dependabot の PR は `actions.lock` の更新を含むはずなので、含まれなければ `gh actions-lock` を再実行する」とすれば、公式の説明と矛盾しない。
2. 「`gh skill install` で導入」は、`gh skill install github/gh-actions-lock` と具体的に書ける(2.1)。
3. 「`uses:` は読みやすいタグのまま書き、commit SHA への書き換えはしません」は、方向性は公式と合う。ただし `gh actions-lock` 自身が、部分バージョンを完全なタグに書き換える(3.2 の 1)。「SHA への書き換えはしない」に加えて、この書き換えがあることを書かないと、利用者が差分に驚く。
4. 「公式の `verify-lockfile.yml` を取り込み、定期実行で、タグの付け替えを検知します」について。公式スキル(skill L134-141)は、PR、`main` への push、毎週のスケジュールで実行すると書いている。しかし、公式リポジトリの現行の `verify-lockfile.yml`(L6-10)には、`schedule` のトリガーがない。したがって「公式の `verify-lockfile.yml` を取り込めば定期実行になる」とは言えない。スキル(skill)の記述と実ファイルが食い違っている。定期実行を使うなら、`schedule` を自分で足す必要がある。
5. `verify-lockfile.yml` は `gh extension install github/gh-actions-lock --pin v0.2.0` で拡張を固定している(L24)。最新リリースは v0.4.0 なので、取り込むときに固定する版を決める必要がある。
