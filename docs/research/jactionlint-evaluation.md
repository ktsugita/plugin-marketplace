# actionlint から jactionlint への乗り換え調査

調査日は 2026-10-24。一次情報だけを根拠にする。確認できなかった点は「未確認」と書く。

この文書は調査時点の記録である。調査後に下した決定と、その実施で確かめた事実は、第 10 節にまとめた。第 9 節の推奨は、決定とは異なる。

## 結論

- 乗り換える価値はある。ただし急ぐ理由は、検査能力よりも、mise の registry が actionlint を非推奨にしたことと、hk に jactionlint の組み込みステップがあることにある。
- 一方で、jactionlint は fork としての最初のリリースから 19 日しか経っていない。メンテナはほぼ 1 人で、v2.0.0 で既定の挙動が変わっている。「十分に枯れている」とは言えない。
- zizmor は、外せる可能性が高い。jactionlint は zizmor 1.30.1 の 41 個の audit すべてに対応するルールを持つと主張している。ただしこれは jactionlint 側の自己申告であり、第三者による検証は見つからなかった。この主張の範囲外(pre-commit 設定の検査、`--min-confidence` など)が残る。このリポジトリでは、それらを使っていない。
- このリポジトリには `.github/workflows/` がない。現状の `actionlint` と `zizmor` のステップは、点検対象のファイルを持たない。乗り換えの実害も効果も、いまは小さい。

## 1. 機能範囲

### 1.1 actionlint の検査を含むか

- jactionlint は actionlint の fork であり、パーサ、式の型検査、ワークフローの構文検査、多くのテストを引き継いでいる。出典: https://github.com/jdx/jactionlint/blob/main/NOTICE.md
- `--profile correctness` が「actionlint の検査 + jactionlint のバグ検出」にあたる。出典: README.md L170-174(コミット 556be51)。
- actionlint の検査種別(`syntax-check`、`expression`、`action`、`events`、`matrix`、`shellcheck` など 17 種)は、すべてルール ID に対応づけられている。出典: `docs/actionlint.md` L99-119。
- 網羅性の根拠は、actionlint 本家のテスト用ファイル 147 件を使うテストである。`actionlint_originals.txt` は 147 行あり、各ファイルの期待出力の誤りがすべて報告されることを検査する。出典: `actionlint_compat_test.go`、`testdata/actionlint_originals.txt`。
- このテストの限界は、jactionlint 自身が書いている。メッセージを変えた箇所や、actionlint が拒否する構文を受け入れる箇所は、期待出力を編集してある。したがって「メッセージまで同一」ではなく「検査を網羅している」ことを示すテストである。また、CLI、終了コード、出力形式は対象外である。出典: `docs/actionlint.md` L179。なお、テストコード内の例外表 `actionlintExceptions` は空である(`actionlint_compat_test.go` の宣言)。「期待出力を編集した」という文書の記述と、例外表が空であることの関係は、確認していない(未確認)。
- 目視で行った actionlint の `docs/checks.md` の 28 項目との 1 対 1 の照合は、していない(未確認)。

### 1.2 actionlint にあって jactionlint にない検査

- 見つかっていない。ただし「ない」ことの証明は、上記テスト以外にない(未確認)。
- 挙動が異なる点は、jactionlint の文書が表にしている(`docs/actionlint.md` L209-221)。主なものを挙げる。
  - `.github/workflows` の下位ディレクトリにあるファイルは、引数なしの実行では検査しない。GitHub が読み込まないためである。actionlint は検査する。
  - shellcheck の指摘は、`run:` キーではなく、スクリプト内の該当箇所に報告する。
  - shellcheck や pyflakes が入っていないとき、stderr に `note:` を出す(終了コードは変わらない)。
  - 引用符つきの値の型判定が、再利用可能ワークフローの入力で反対になる。
  - ランナーラベルと主要アクションの入力のデータは、jactionlint のほうが新しい(例: `ubuntu-26.04`)。
- GitHub の新しい構文(`parallel`、`background` ステップなど)を、jactionlint は受け入れる。actionlint は「予期しないキー」とする。出典: `docs/actionlint.md` L225-237。

### 1.3 jactionlint にあって actionlint にない検査

- `correctness` プロファイルだけで 15 ルール以上が追加されている。例: `action-syntax`、`dependabot-syntax`、`concurrency-deadlock`、`unsound-ternary`、`workflow-run-names`、`github-script-syntax`。出典: `docs/actionlint.md` L190-207。
- 検査対象のファイルも広い。引数なしの実行は、ワークフロー、composite action、`dependabot.yml`、Actions のロックファイルを検査する。actionlint はワークフローだけを検査する。出典: `docs/actionlint.md` L188。
- ルールは全部で 161 個ある(`docs/rules.md` の表の行数)。`correctness` が 73、`default` が 47、`pedantic` が 27、オンライン専用が 9 など。

## 2. zizmor との重複

### 2.1 対応の全体像

- jactionlint の文書は、zizmor 1.30.1 の 41 個の audit すべてにルールがあると述べる。ID は `unsound-condition`(jactionlint では `if-always-true`)を除いて同じである。出典: `docs/zizmor-parity.md` L7。
- 同じ表で、一致の状態は 11 個が `same`、27 個が `differs`、3 個が `not comparable` である。
- 41 個という数は、zizmor のリポジトリの `crates/zizmor/src/audit/` 直下のファイル(`mod.rs` を除く)の数と一致した。出典: https://github.com/zizmorcore/zizmor (コミット d00d411、2026-10-23)。ただし、このリポジトリで固定している zizmor は 1.31.1 である(`mise.lock` L117-137)。1.31.0 の変更(`typosquat-uses` が pre-commit 設定に対応、`self-hosted-runner` の精度向上、`dangerous-triggers` が `issue_comment` を危険とみなす、`cache-poisoning` が `cache-mode` に対応)が、jactionlint の基準の 1.30.1 に含まれるかは、確認していない(未確認)。出典: zizmor `docs/release-notes.md` L30-60。
- jactionlint の作者が行った比較(24 リポジトリ)では、zizmor の 998 件のうち 955 件(95.7%)を jactionlint も報告し、43 件が漏れた。1,109 リポジトリの比較では、112,559 件のうち 104,421 件(92.8%、行位置の許容 3 行)である。漏れの多くは「意図した差」と分類されている。出典: `docs/zizmor-measurements.md` L56、L79。この比較は jactionlint の作者自身が実施し、1,109 リポジトリの一覧と実行時のコミットはリポジトリに記録されていない。再現はできない。

### 2.2 ルールごとの対応表

プロファイルの列は、jactionlint で既定で動くか。`default` は設定なしで動く。`pedantic` はより厳しい設定でのみ動く。`online` は `--online` でのみ動く。レベルは終了コード 1 になるのが `error` だけ、という意味である。

zizmor の persona は、`regular` が jactionlint の `default`、`pedantic` と `auditor` が `pedantic` に対応する。出典: `docs/zizmor-parity.md` L108-113。この表の値の出典は、`docs/rules.md` の表と `docs/zizmor-parity.md` L142-184 である。

| zizmor の audit | jactionlint のルール | 状態 | プロファイル / レベル | 主な差 |
| --- | --- | --- | --- | --- |
| adhoc-packages | adhoc-packages | differs | default / error | `--prefix` の値とローカルの tarball は対象外。`sudo` 配下は報告する |
| anonymous-definition | anonymous-definition | differs | pedantic / warn | 生成ファイルと `action.yml` は対象外 |
| archived-uses | archived-uses | differs | online / warn | zizmor はアーカイブ済みリポジトリの一覧を内蔵し、オフラインで報告する。jactionlint は GitHub に問い合わせるため、オフラインでは何も報告しない |
| artipacked | artipacked | differs | default / error | 後続のステップが push するとき、`actions/checkout@v1` のとき、式の値のときは報告しない。修正は jactionlint が safe、zizmor が unsafe |
| bot-conditions | bot-conditions | differs | default / error | 否定形の判定は報告しない |
| cache-poisoning | cache-poisoning | differs | default / error | 既定では件数が少ない。zizmor の経験則は `pedantic` オプション |
| concurrency-limits | concurrency-limits | differs | default / error | zizmor は pedantic。schedule と手動実行のみのワークフローは `pedantic` オプション |
| dangerous-triggers | dangerous-triggers | differs | default / error | 報告位置が `on:` ではなくトリガー |
| dependabot-cooldown | dependabot-cooldown | differs | default / error | 修正に `default-days` の設定が必要(zizmor は 7 を書く) |
| dependabot-execution | dependabot-execution | same | default / error | |
| excessive-permissions | excessive-permissions と missing-permissions | differs | default / error | 2 ルールに分かれる。再利用専用ワークフローのジョブは呼び出し側に任せる |
| forbidden-uses | forbidden-uses | not comparable | 設定時のみ / error | |
| github-app | github-app | differs | default / error | 他の 2 アクションも検査する |
| github-env | github-env | differs | default / error | 攻撃者が制御できないと示せる値は許容する |
| hardcoded-container-credentials | hardcoded-container-credentials | same | correctness / error | actionlint の `credentials` 検査が報告する |
| impostor-commit | impostor-commit | same | online / error | |
| insecure-commands | insecure-commands | same | default / error | |
| insecure-url-scheme | insecure-url-scheme | not comparable | default / error | zizmor は pre-commit 設定の `repo:` URL、jactionlint はスクリプトと入力 |
| known-vulnerable-actions | known-vulnerable-actions | same | online / error | |
| misfeature | misfeature | differs | default / error | カスタムシェルは `pedantic` オプション |
| obfuscation | obfuscation | differs | default / error | 定数の `if:` などは報告しない |
| overprovisioned-secrets | overprovisioned-secrets | differs | default / error | |
| ref-confusion | ref-confusion | not comparable | online / warn | |
| ref-version-mismatch | ref-version-mismatch と missing-version-comment | differs | online / warn、後者は pedantic / warn | ブランチ名のコメントは比較しない |
| secrets-inherit | secrets-inherit | same | default / error | |
| secrets-outside-env | secrets-outside-env | differs | pedantic / warn | |
| self-hosted-runner | self-hosted-runner | differs | pedantic / info | |
| self-repository | self-repository | same | pedantic / info | |
| stale-action-refs | stale-action-refs | same | online / info | |
| superfluous-actions | superfluous-actions | differs | default / error | セルフホストの可能性があるランナーは報告しない |
| template-injection | template-injection | differs | correctness / error | zizmor の regular が報告する `github.actor`、`env.*`、`vars.*`、ステップ出力は、`pedantic` オプションでのみ報告する |
| typosquat-uses | typosquat-uses | differs | default / error | jactionlint は追加・置換した文字も報告する |
| undocumented-permissions | undocumented-permissions | differs | pedantic / info | |
| unpinned-images | unpinned-images | differs | default / error | persona の分割はなく、`require-digest` で切り替える |
| unpinned-tools | unpinned-tools | differs | default / error | |
| unpinned-uses | unpinned-uses | differs | default / error | 方針 `immutable-release` と Actions のロックファイルを追加。修正は `--online` が必要で safe |
| unredacted-secrets | unredacted-secrets | same | default / error | |
| unsound-condition | if-always-true | differs | correctness / error | ID が違う。`if: \|` の 1 式だけのブロックは報告しない |
| unsound-contains | unsound-contains | same | default / error | |
| unsound-ternary | unsound-ternary | same | correctness / error | |
| use-trusted-publishing | use-trusted-publishing | differs | default / error | |

`unsound-ternary` の行のプロファイルとレベルは、`docs/rules.md` の行が `||` を含むため表の列が崩れて取れなかった。`docs/zizmor-parity.md` L124 の「`correctness` プロファイル」と、`docs/actionlint.md` L204 の説明から補った。レベルが `error` であることは未確認である。

### 2.3 zizmor を外すと残るもの

jactionlint 自身が認めている「できないこと」は次のとおり。出典: `docs/zizmor-parity.md` L328-339。

- pre-commit 設定ファイルの検査。リポジトリのスラッグ(`zizmor owner/repo`)の指定。LSP モード。
- `zizmor.yml` と `.github/zizmor.yml` の読み込み。設定は `.github/jactionlint.yaml` に書き直す。
- `--min-confidence`。ルールのレベルは 1 つで、トリガーや確度では変わらない。
- `archived-uses` のオフライン検査。
- `ref-version-mismatch` のブランチ名コメントの比較。
- `# zizmor: ignore[...]` のコメントは読む。`--migrate-ignores` で `# jactionlint ignore=` に書き換えられる。

挙動の違いで、運用に響くものを挙げる。

- ネットワーク: zizmor はトークンがあればオンライン audit を実行する。jactionlint は `--online`、`online: true`、`JACTIONLINT_ONLINE` のどれかがないと使わない。出典: `docs/zizmor-parity.md` L93。
- このリポジトリの現状は `zizmor --offline` である(`hk.pkl` L33)。jactionlint の既定と同じ条件になる。

zizmor 側の公式な位置づけは、次の 1 点を確認した。zizmor の終了コードは、検出なしが 0、実行エラーが 1、引数エラーが 2、入力なしが 3、検出ありが最高の重大度に応じて 11〜14 である。出典: zizmor `docs/usage.md` L589-605。

jactionlint 側で、zizmor との重複を一括で止める設定を求める Issue が出ている(#278 `zizmor_parity_audits`)。この Issue は 2026-10-14 に閉じられた。実装されたかは確認していない(未確認)。`grep -rn zizmor_parity` はリポジトリの `.md` と `.go` に一致しなかった。実装されていないと見てよい。

### 2.4 第三者の採用例

- jdx/hk は自身の CI で jactionlint v2 に移り、zizmor のジョブを外した。出典: https://github.com/jdx/hk/pull/1682。ただし、hk と jactionlint のメンテナは同じ jdx であり、独立した検証ではない。
- 「zizmor を外しても安全」という第三者の検証は、見つからなかった(未確認)。

## 3. 実行速度

- jactionlint が公表している、他のツール(actionlint、zizmor)との速度比較は、見つからなかった。公表なし。
- 検索した場所は、`README.md`、`docs/*.md`、`CHANGELOG.md`、`CONTRIBUTING.md`、`scripts/README.md`。
- 内部の性能試験はある。`perf_test.go` の `TestScalingBudget` は、入力が 4 倍になったときの時間が 12 倍を超えないことを確認する。数値の比較ではない。ベンチマークは `mise run bench`(`go test -bench Lint`)で実行できる。出典: `CONTRIBUTING.md` L96、L373。
- 変更履歴の「Performance Improvements」は、式の解析を 1 回にする、同時チェック数を制限してメモリを抑える、といった内容で、数値を伴わない。出典: `CHANGELOG.md` L120-126、L161-165。
- actionlint と zizmor の README と `docs/` にも、他のツールとの速度比較は見つからなかった。
- 実測は、この調査では行っていない(未確認)。

## 4. 導入方法

### 4.1 mise

- mise の registry に `jactionlint` がある。バックエンドは `github:jdx/jactionlint`。出典: https://github.com/jdx/mise/blob/main/registry/jactionlint.toml 。登録は 2026-10-05(PR #13960)。
- 同じ PR で、registry の `actionlint` に `deprecated` が付いた。メッセージは「jactionlint は上流の修正を取り込んで保守されている fork です。`mise use jactionlint` を実行してください」。出典: https://github.com/jdx/mise/blob/main/registry/actionlint.toml 。つまり、いまの `actionlint = "latest"` は非推奨の指定である。
- `packslip:jdx/jactionlint` でも入れられる。出典: `docs/install.md` L48-51。このリポジトリは hk を `packslip:github.com/jdx/hk` で入れている(`mise.toml` L17)。ただし、registry のバックエンドは `github:` であり、`packslip:` を使う必要はない。
- `mise.lock` に載る。jactionlint の文書が `mise lock` でバージョン、プラットフォームごとのチェックサム、由来を記録すると述べている。出典: `docs/install.md` L35-38。このリポジトリの `lockfile_platforms` は `windows-x64`、`linux-x64`、`linux-arm64` で、v2.3.0 のリリースにはこの 3 つの資産がある(`jactionlint_2.3.0_windows_amd64.zip`、`linux_amd64.tar.gz`、`linux_arm64.tar.gz`)。出典: `gh release view v2.3.0 -R jdx/jactionlint`。
- 注意点が 1 つある。hk の PR #1682 には、「`mise lock --bump` が `latest` をこのツールでは 1.8.2 に解決する。そのため `"2"` を使った」とある(その時点の記述)。いまも同じかは確認していない(未確認)。`mise ls-remote jactionlint` は 2.3.0 まで列挙する(この環境で確認)。
- 比較として、actionlint は `aqua:rhysd/actionlint`、zizmor は `aqua:zizmorcore/zizmor` である(`mise.lock` L7、L119)。jactionlint のバイナリは検証の署名も備える(`packslip.sigstore.json`)。

### 4.2 hk

- `Builtins.jactionlint` がある。出典: https://github.com/jdx/hk/blob/main/pkl/builtins/jactionlint.pkl 。
  - glob は `.github/workflows/*.y*ml`、`.github/actions/**/action.y*ml`、`.github/dependabot.y*ml`。
  - `check` は `jactionlint --format gcc {{files}}`。`check_diff` は `hk util sarif-diff -- jactionlint --format sarif {{files}}`。`fix` は `jactionlint --fix {{files}}`。
- 組み込みが入った版: ステップの追加(#1663)は hk 2.6.0、SARIF による修正(#1687)は hk 2.7.0 に含まれる。出典: `gh api repos/jdx/hk/compare/v2.5.0...v2.6.0` と `v2.7.0` の差分。2.7.0 に入ったと判断した根拠は、#1687 のコミット時刻(2026-10-12 21:59)が v2.6.0 の公開時刻(同日 10:39)より後であること。
- このリポジトリの `hk.pkl` は `hk@2.5.0` の `Config.pkl` と `Builtins.pkl` を読み込んでいる(L1-2)。この版に `Builtins.jactionlint` はない。使うには、URL を 2.7.0 以降に上げる必要がある。`mise.lock` 側の hk は v2.7.1 まで進んでいる(`mise.lock` の hk の url)。
- 版を上げずに書く場合の `hk.pkl` の例を示す。この例は実行して確かめていない(未確認)。

```pkl
["jactionlint"] = new Step {
    glob = List(".github/workflows/*.y*ml", ".github/actions/**/action.y*ml", ".github/dependabot.y*ml")
    batch = true
    diagnostic_format = "gcc"
    check = "jactionlint --format gcc {{files}}"
    fix = "jactionlint --fix {{files}}"
}
```

- プロファイルを `hk.pkl` だけで指定する方法は、組み込みのコメントにある。`check`、`check_diff`、`fix` の 3 つすべてに `--profile` を渡す。

### 4.3 外部プログラム

- shellcheck と pyflakes は、jactionlint も `PATH` から探して呼ぶ。入っていなければ `note:` を出して検査を飛ばす。出典: `docs/usage.md` L251-260。このリポジトリの `mise.toml` には shellcheck が入っていない。actionlint の現状と同じである。

## 5. 互換性

| 項目 | actionlint | jactionlint | 出典 |
| --- | --- | --- | --- |
| 出力形式(text) | `file:line:col: message [kind]` | 末尾のラベルがルール ID。形式は同じ | `docs/actionlint.md` L136 |
| 他の形式 | `-format` の Go テンプレート | `text`、`oneline`、`json`、`jsonl`、`sarif`、`gcc`、`github`、`summary`、テンプレート | `docs/actionlint.md` L68 |
| 終了コード | 0 なし、1 検出あり、2 引数エラー、3 致命的エラー | 同じ 4 値。ただし `warn` と `info` の検出は 0。`--strict-exit` で 1 | `actionlint/docs/usage.md` L181-188、`docs/cli.md` L270-292 |
| オプションの綴り | `-ignore` など 1 ダッシュ | 2 ダッシュ(`--ignore`)。1 ダッシュは終了コード 2 | `docs/v2-migration.md` L11 |
| 設定ファイル | `.github/actionlint.yaml` | `.github/jactionlint.yaml` を先に探し、なければ `actionlint.yaml` も読む。未知のキーは終了コード 3 | `docs/actionlint.md` L82-94 |
| 設定のキー | `self-hosted-runner`、`config-variables`、`paths` | 同じキー + `profile`、`rules`、`ignores` など | `docs/actionlint.md` L84 |
| `shellcheck` と `pyflakes` | `-shellcheck`、`-pyflakes` で実行ファイルを指定。空文字で無効 | `--shellcheck`、`--pyflakes`。空文字で無効。存在しない名前を明示すると終了コード 3(actionlint は無視) | `actionlint/docs/usage.md` L37-42、`docs/actionlint.md` L75 |
| `-ignore` | メッセージへの正規表現 | 正規表現またはルール ID。ほかにコメント `# jactionlint ignore=RULE`、設定の `ignores:`(期限つき) | `docs/actionlint.md` L47-55 |
| `--ignore` の複数指定 | 繰り返す | 繰り返す。カンマ区切りは 1 つの正規表現になる | `docs/cli.md` L28 |
| 既定の厳しさ | actionlint の検査のみ | 既定の `default` プロファイルは検査が多い。actionlint 相当にするには `--profile correctness` | `docs/actionlint.md` L31 |
| パッケージ名 | `actionlint` | Homebrew core などの `actionlint` は本家を入れる | `docs/install.md` L24 |

- 設定ファイルは、`.github/actionlint.yaml` を置いたまま、`profile: correctness` を足せば両方のツールで読める(actionlint は未知のキーを無視する)。出典: `docs/actionlint.md` L84。
- 本家の actionlint が出すメッセージの文面は、jactionlint で書き換えられている箇所がある。メッセージへの正規表現の `-ignore` は、動かなくなる可能性がある。出典: `docs/actionlint.md` L57。
- このリポジトリは `-ignore` も設定ファイルも使っていない。`.github/actionlint.yaml` は存在しない(`ls -a .github` で確認)。
- `.github/dependabot.yml` がある。jactionlint の `default` プロファイルは、`dependabot.yml` も検査する。`dependabot-cooldown` は `default` プロファイルで `error` である。現在のファイルには `cooldown` の記述がないので、指摘される可能性が高い。調査の時点では、実行して確かめていない(実行はこの調査の環境で許可されなかった)。のちに実行して確かめた(第 10 節)。

## 6. 成熟度

| 項目 | jactionlint | actionlint | zizmor |
| --- | --- | --- | --- |
| リポジトリの作成 | 2026-10-05(fork) | 2021-05-25 | 2024-08-19 |
| 最初のリリース(fork として) | v1.8.0、2026-10-05 | 未確認 | 未確認 |
| 最新リリース | v2.3.0、2026-10-21 | v1.7.12、2026-03-30 | v1.31.1、2026-10-15 |
| 直近のリリース間隔 | 7 リリース、17 日間 | 約 1〜1.5 か月(v1.7.8 から v1.7.12 の 5 リリース、2025-10-11 から 2026-03-30) | 未確認 |
| スター数 | 282 | 4,347 | 6,766 |
| 未解決の Issue | 1(#304、2026-10-24 起票) | 208 | 未確認 |

出典: `gh release list`、`gh api repos/...`(2026-10-24 に実行)。jactionlint の履歴の大半(1,827 コミット)は actionlint 本家の rhysd のコミットを引き継いだものである。

- 2026-10-01 以降の jactionlint のコミットは 282 件。うち 267 件が jdx 本人、10 件が bot、4 件がその他である。出典: `git log --since=2026-10-01`。メンテナは実質 1 人である。
- 閉じた Issue は 30 件で、いずれも起票から 0〜5 日で閉じている。Issue のほとんどは作者本人のものと見られる(未確認)。
- v2.0.0(2026-10-09)は、既定のプロファイルを厳しくし、長いオプションを 2 ダッシュに変えるなど、挙動を変えた。fork の最初のリリースから 4 日後である。出典: `docs/v2-migration.md` L9-25、`CHANGELOG.md` L181。
- actionlint 本家は、最後のリリースが 2026-03-30、最後の push が 2026-07-16 で、未解決の Issue は 208 件である。jactionlint は、本家の変更を取り込むと述べている(`NOTICE.md`)。本家を取り込む作業が継続して行われるかは、未確認である。
- mise と hk のメンテナ(jdx)が jactionlint のメンテナでもある。このリポジトリは mise と hk を既に採用しており、ツールの連携は整っている。一方で、1 人のメンテナへの依存が、ツール全体で増える。

## 7. 乗り換え時に直す箇所

乗り換えの範囲を、(A) actionlint を jactionlint に置き換える、(B) zizmor も外す、に分けて示す。

### (A) actionlint を jactionlint に置き換える

| ファイルと行 | 現状 | 直す内容 |
| --- | --- | --- |
| `mise.toml` L16 | `actionlint = "latest"` | `jactionlint = "latest"` に変更。`mise.lock` を `mise lock` で更新 |
| `mise.lock` L5-25 | `aqua:rhysd/actionlint` v1.7.12 | `mise lock` が置き換える。手で編集しない |
| `hk.pkl` L1-2 | `hk@2.5.0` | 2.7.0 以上に上げる(`Builtins.jactionlint` に必要) |
| `hk.pkl` L30 | `["actionlint"] = Builtins.actionlint` | `["jactionlint"] = Builtins.jactionlint`。既存の `actionlint` と同等にするなら `--profile correctness` を 3 つのコマンドに渡す(4.2 の節) |
| `CONTRIBUTING.md` L7 | 「`gh`、`hk`、`uv`、`actionlint`、`zizmor` が入り」 | `actionlint` を `jactionlint` に変更 |
| `plugins/coding/skills/github-actions/SKILL.md` L7 | 「最後に `actionlint` を通してください」 | `jactionlint` に変更 |
| 同 L176-180 | 見出し「静的解析 (`actionlint`)」、リンク https://github.com/rhysd/actionlint、`mise use actionlint`、`Builtins.actionlint`、「`.yml` と `.yaml` の両方が対象」 | 見出し、リンク(https://github.com/jdx/jactionlint)、`mise use jactionlint`、`Builtins.jactionlint` に変更。対象に `dependabot.yml` と composite action が増えることを書く。プロファイルの説明(`default` と `correctness`)を足す |
| `plugins/coding/skills/mise/SKILL.md` L70 | 設定例の `actionlint = "latest"` | `jactionlint = "latest"` に変更 |
| `.github/dependabot.yml` | `cooldown` の記述なし | `default` プロファイルの `dependabot-cooldown` に指摘される可能性がある(実行して未確認)。指摘されたら `cooldown` を足す |

`GLOSSARY.md`、`README.md`、`UPSTREAM.md` に `actionlint`、`zizmor` の記述はない(`grep` で確認)。`.claude/skills/` と `src/`、`tests/` にも記述はない。

### (B) zizmor も外す場合の追加分

| ファイルと行 | 直す内容 |
| --- | --- |
| `mise.toml` L18 | `zizmor = "latest"` を削除 |
| `mise.lock` L117-137 | `mise lock` で消える |
| `hk.pkl` L31-34 | `["zizmor"]` のステップを削除 |
| `CONTRIBUTING.md` L7 | `zizmor` を削除 |
| `plugins/coding/skills/github-actions/SKILL.md` | zizmor の記述は元からない。セキュリティ点検を jactionlint に任せる旨を書くなら追記する |

`.github/zizmor.yml` と `zizmor.yml` はこのリポジトリにない(`find` で確認)。移行する設定はない。`# zizmor: ignore[...]` のコメントも、現在のリポジトリには存在しない(`.github/workflows/` がないため)。

## 8. 判断に必要な未確認事項

- `.github/dependabot.yml` に対する jactionlint の実際の出力。
- 実行速度の実測。
- jactionlint の `correctness` プロファイルが、actionlint の検査を漏れなく含むことの独立した検証。
- zizmor 1.31.1 に対する jactionlint の対応状況(基準は 1.30.1)。
- `mise lock --bump` が現在、jactionlint の最新を解決するか。
- actionlint 本家の変更を、jactionlint が継続して取り込むか。

## 9. 推奨(調査時点)

この節は調査時点の推奨である。実際の決定は第 10 節に書いた。

1. すぐに乗り換えなくても、実害は出ない。このリポジトリにワークフローがないためである。
2. 乗り換えるなら、(A) を先に行い、`--profile correctness` で actionlint と同等にする。`default` への引き上げと zizmor の撤去(B)は、実際にワークフローを追加した時点で、`zizmor` と並べて 1 回比較してからにする。jactionlint の文書もこの順序(並走させてから切り替える)を勧めている(`docs/zizmor-parity.md` L17-19)。
3. バージョンを固定するなら、`mise.lock` を使う(`docs/install.md` L35-38)。fork 直後で挙動が変わりやすいため、`mise.toml` は `latest` のままにせず、メジャーバージョンを固定する選択肢もある(hk の PR #1682 は `"2"` を使った)。

## 10. 決定と実施結果

実施日は 2026-10-24。調査の結果を受けて、次のように決めて実施した。

### 10.1 決定

- このリポジトリの `actionlint` を `jactionlint` に置き換え、`zizmor` を外す。第 9 節は「ワークフローを追加するときまで待ち、`zizmor` と並べて比べてから外す」と推奨していたが、待たずに両方を実施した。
- `coding:github-actions` スキルが利用者に勧めるツールも、`jactionlint` に変える。プロファイルは `default` を勧め、`--profile correctness` は補足に書く。
- 実行速度は、判断の根拠にしない。比較が公表されておらず、ワークフローがないので実測もできなかった。
- 第三者による `zizmor` 代替の検証がないこと、fork から日が浅く挙動が変わりやすいことは、承知のうえで受け入れた。
- スキルには、`zizmor` を不要にするとは書かず、`zizmor` にも触れない。
- 判断のきっかけは、速度と、`zizmor` を減らせる可能性だった。決め手は、機能の優劣ではなく、mise が `actionlint` を非推奨にしたことと、hk の組み込みステップがあることである(第 1 節、第 4 節)。

### 10.2 変更したもの

第 7 節の (A) と (B) の両方を実施した。

| 対象 | 変更 |
| --- | --- |
| `mise.toml` | `actionlint` を `jactionlint = "latest"` に変更。`zizmor` を削除 |
| `mise.lock` | `mise lock` で更新。`actionlint` と `zizmor` の項目が消え、`jactionlint` 2.3.0 が入った |
| `hk.pkl` | hk を 2.5.0 から 2.7.1 に更新。`Builtins.jactionlint` に変更(プロファイルは `default`)。`zizmor` のステップを削除 |
| `.github/dependabot.yml` | `cooldown.default-days: 7` を追加 |
| `CONTRIBUTING.md` | `actionlint` を `jactionlint` に変更。`zizmor` を削除 |
| `plugins/coding/skills/github-actions/SKILL.md` | 冒頭の文と静的解析の節を `jactionlint` に変更 |
| `plugins/coding/skills/mise/SKILL.md` | 設定例を `jactionlint = "latest"` に変更 |

### 10.3 実施で確かめた未確認事項

第 8 節の未確認事項のうち、次の 2 点が確かめられた。

- `.github/dependabot.yml` に対する出力: jactionlint 2.3.0 は `dependabot-cooldown` を指摘し、終了コード 1 を返した(`cooldown` が未設定なので、Dependabot の暗黙の 3 日が適用される。`cooldown.default-days` を 7 以上にするよう求める)。`default-days: 7` を足すと指摘はなくなり、`hk check --all` が通った。
- `mise lock` での `latest` の解決: `jactionlint = "latest"` は 2.3.0 に解決された。hk の PR #1682 で見られた、古い版 1.8.2 への解決は再現しなかった。そのため `"2"` による固定は使っていない。

次の 4 点は、まだ未確認である。

- 実行速度の実測
- `correctness` プロファイルが、actionlint の検査を漏れなく含むことの独立した検証
- `zizmor` 1.31.1 に対する、jactionlint の対応状況
- actionlint 本家の変更を、jactionlint が継続して取り込むか

### 10.4 その後の変更

`.github/dependabot.yml` は削除した。このリポジトリには `.github/workflows/` も `action.yml` もなく、Dependabot の `github-actions` が更新の対象を見つけられずに、Insights のエラー(`Dependabot couldn't find a <anything>.yml`)になったためである。ワークフローを追加するときに、`cooldown.default-days: 7` を付けて作り直す。

## 出典一覧

- jactionlint(コミット 556be51、2026-10-21): https://github.com/jdx/jactionlint 。`README.md`、`NOTICE.md`、`CHANGELOG.md`、`CONTRIBUTING.md`、`docs/actionlint.md`、`docs/zizmor-parity.md`、`docs/zizmor-measurements.md`、`docs/cli.md`、`docs/install.md`、`docs/hooks.md`、`docs/usage.md`、`docs/v2-migration.md`、`docs/rules.md`、`actionlint_compat_test.go`、`perf_test.go`
- actionlint(コミット 011a6d1): https://github.com/rhysd/actionlint 。`docs/usage.md`、`docs/checks.md`、`docs/config.md`
- zizmor(コミット d00d411、2026-10-23): https://github.com/zizmorcore/zizmor 。`docs/usage.md`、`docs/release-notes.md`、`crates/zizmor/src/audit/`
- mise registry: https://github.com/jdx/mise/tree/main/registry (`jactionlint.toml`、`actionlint.toml`)、PR #13960
- hk: https://github.com/jdx/hk (`pkl/builtins/jactionlint.pkl`、`actionlint.pkl`、`zizmor.pkl`)、PR #1663、#1682、#1687
- このリポジトリ: `mise.toml`、`mise.lock`、`hk.pkl`、`CONTRIBUTING.md`、`.github/dependabot.yml`、`plugins/coding/skills/github-actions/SKILL.md`、`plugins/coding/skills/mise/SKILL.md`
