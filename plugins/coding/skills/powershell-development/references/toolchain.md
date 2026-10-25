# PowerShell のツールチェーンの導入

PSScriptAnalyzer（静的解析）と Pester（テスト）を、mise と hk から呼ぶ形に整えます。利用者が導入を承認してから行います。

## 導入と版の固定

PSScriptAnalyzer と Pester は PSGallery のモジュールです。mise の `[tools]` には入れられません（PSGallery のバックエンドも、mise のレジストリへの登録もありません）。PSResourceGet（最新の LTS に同梱）のネイティブ形式の宣言ファイルで、版を完全一致で固定します。

```powershell
# psresources.psd1
@{
    PSScriptAnalyzer = @{ version = '[<版>]'; repository = 'PSGallery' }
    Pester           = @{ version = '[<版>]'; repository = 'PSGallery' }
}
```

```powershell
Install-PSResource -RequiredResourceFile ./psresources.psd1 -TrustRepository -Quiet
```

- 版は書かずに調べます。`Find-PSResource PSScriptAnalyzer -Repository PSGallery` と `Find-PSResource Pester -Repository PSGallery` の最新の安定版を使います。Pester は 6 系を使います（5 は 5.9.0 から maintenance mode です）。
- 版は完全一致（`'[x.y.z]'`）で書きます。範囲指定は、PSGallery では範囲内の最新版を選ばないことがあるので使いません。
- `uv.lock` に相当する公式の機能はありません。宣言ファイルが固定するのは版番号までで、ハッシュと依存の解決結果は残りません。この2つのモジュールは依存を持ちません。
- 書式は、PSDepend の `requirements.psd1`（`Pester = '5.9.1'` の短縮形）と互換ではありません。短縮形は `Install-PSResource` で失敗します。
- PSGallery は既定で未信頼です。非対話（フック、CI）では、呼び出しごとに `-TrustRepository` を付けます。宣言ファイルの `trustrepository` キーでは対話の確認が省かれず、未信頼の PSGallery で `-NonInteractive` が失敗しました。`Set-PSResourceRepository -Trusted` は利用者の環境を恒久的に変えるので使いません。`scope` キーは効きます（既定の `CurrentUser` で足ります）。
- 導入済みの版を再度指定すると、「すでに導入済み」の警告が出て終了コード 0 になります。毎回呼んでも副作用はありません（PSGallery への問い合わせは発生します）。
- 導入先（CurrentUser のモジュールの保存先）は mise の外にあり、`pwsh` の導入元によらず共有されます。複数の版が並ぶと `Import-Module` は最大の版を読むので、ラッパーで `-RequiredVersion` を指定します。

## mise と hk との連携

mise でタスクを、hk で git フックを管理するプロジェクトでは、PSScriptAnalyzer と Pester を次の形で呼び出します。

| 方針 | 理由 |
|---|---|
| `pwsh` は、`references/pwsh-install.md` に従う。PSScriptAnalyzer と Pester は mise の `[tools]` の外（PSGallery）にあり、`psresources.psd1` で固定する | 手元の `pwsh` を尊重し、入れ直しを強いないため。`pwsh` の版も固定したいプロジェクトだけ、mise の `[tools]` に足す。 |
| 呼び出しは `scripts/lint.ps1` と `scripts/test.ps1` のラッパーに集め、hk のステップと mise タスクから `pwsh -File` で呼ぶ | 単体の `Invoke-ScriptAnalyzer` は違反があっても終了コード 0 で終わり、Pester は `Run.Exit` なしだと失敗しても 0、ありだと Linux で 256 の剰余になるため。`pwsh` の起動には、呼ぶたびに時間がかかるので、ファイルごとに起動せず、同一プロセスのループにするため。 |
| hk のステップは `argv` の `Command` で書く。`-Command` の後ろに `{{files}}` を並べない | `-Command` は引数を連結して再解釈し、空白や `$`、`&` を含むパスで壊れるため。`-File` なら1引数ずつ届く。 |
| 導入は `deps` タスクを正本にし、`[hooks] postinstall` から呼ぶ。ラッパーは導入済みの版を検査し、不一致なら `mise run deps` を促して失敗する。自動導入はしない | `postinstall` は `mise install` で走るため。ラッパーが黙って導入すると、版の固定が崩れるため。 |
| 失敗とみなす重大度はすべてにする（`-Severity` を指定しない）。整形はしない | `Information` の規則も、ヘルプや `[OutputType()]` に対応するため。`Invoke-Formatter` は文字列入力のみで、`-Fix` と整形規則の組み合わせは壊れた出力を書いたため。 |
| pre-commit でリントを走らせ、Pester は pre-push で走らせる | Pester はコミットごとに走らせるには遅いことが多いため。 |
| 人と CI の入口を `mise run check` にそろえる | 手元で `mise run check` が通れば CI も通るという対応を保つため。 |

`hk.pkl` の例です。`amends` の URL は、`hk init` が生成したものをそのまま使います。

```pkl
amends "package://github.com/jdx/hk/releases/download/v<hk の版>/hk@<hk の版>#/Config.pkl"

local powershell = new Step {
  glob = List("*.ps1", "*.psm1", "*.psd1")
  check = new Command {
    argv = List("pwsh", "-NoProfile", "-NonInteractive", "-File", "scripts/lint.ps1", "{{files}}")
  }
  fix = new Command {
    argv = List("pwsh", "-NoProfile", "-NonInteractive", "-File", "scripts/lint.ps1", "-Fix", "{{files}}")
  }
}

hooks {
  ["pre-commit"] {
    fix = true
    stash = "git"
    steps { ["powershell"] = powershell }
  }
  ["pre-push"] {
    steps {
      ["test"] { check = "mise run test" }
    }
  }
  ["check"] { steps { ["powershell"] = powershell } }
  ["fix"] { fix = true; steps { ["powershell"] = powershell } }
}
```

`mise.toml` の例です。

```toml
[tools]
hk = "latest"

[tasks.deps]
description = "PSScriptAnalyzer と Pester を psresources.psd1 の版で導入する"
shell = "pwsh -NoProfile -NonInteractive -Command"
run = "Install-PSResource -RequiredResourceFile ./psresources.psd1 -TrustRepository -Quiet"

[tasks.test]
run = "pwsh -NoProfile -NonInteractive -File scripts/test.ps1"

[tasks.check]
run = ["hk check --all", "mise run test"]

[tasks.fix]
run = "hk fix --all"

[hooks]
postinstall = "mise run deps"
```

- `deps` の `-Command` には文を1つだけ書きます。複数の文を並べると、途中の失敗が隠れて終了コード 0 になります。
- glob は大文字小文字を区別します。`Up.PS1` は拾われません。拡張子は小文字に統一します。大文字の拡張子が既にあるプロジェクトは、glob に `*.PS1` などを足します。`*.Tests.ps1` は `*.ps1` に含まれます。
- `pwsh` が PATH に無いと、hook 全体が中断されます（他のステップも `aborted` になります）。フックを登録する前に、`pwsh` が PATH にあることを確かめます。
- フックの登録は、`hk` スキルが使える場合はそれに従います。使えない場合は hk の公式ドキュメント（https://hk.jdx.dev/）を参照します。

### `python-development` との違い

`python-development` スキルが使えるプロジェクトと形が違う点が2つあります。

- hk に PowerShell の Builtins が無いので、Group と `prefix` を使わず、ステップを自分で書きます。
- PSScriptAnalyzer と Pester は mise の `[tools]` の外（PSGallery）にあり、`psresources.psd1` で固定します。Python の ruff、ty、pytest は `uv.lock` で固定します。

## ラッパーの実装例

どちらも、規約の「先頭の3行」から始めます。導入済みの版が `psresources.psd1` と一致するかを `Import-Module -RequiredVersion` で検査し、不一致なら `mise run deps` を促して失敗します。

`scripts/lint.ps1` は、引数のファイルを解析します。無指定なら、Git が管理する `.ps1`、`.psm1`、`.psd1` を解析します。`-Settings` を明示し、1つの `pwsh` のプロセスでループし、違反が1件でもあれば `exit 1` します。

```powershell
#Requires -PSEdition Core
#Requires -Version <最新の LTS の major.minor>
<#
.SYNOPSIS
PowerShell のファイルを PSScriptAnalyzer で解析する。違反が残れば終了コード 1 で終わる。
.EXAMPLE
pwsh -NoProfile -File scripts/lint.ps1 -Fix
#>
[CmdletBinding()]
param(
    # PSUseBOMForUnicodeEncodedFile が報告したファイルに BOM を前置する
    [switch]$Fix,
    # 解析するファイル。無指定なら Git が管理する PowerShell のファイル
    [Parameter(ValueFromRemainingArguments)]
    [string[]]$Path
)

Set-StrictMode -Version 3.0
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true

$repoRoot = Split-Path -Parent $PSScriptRoot
$settings = Join-Path $repoRoot 'PSScriptAnalyzerSettings.psd1'

# psresources.psd1 の版を読み込む
$pinned = Import-PowerShellDataFile -LiteralPath (Join-Path $repoRoot 'psresources.psd1')
$version = $pinned['PSScriptAnalyzer'].version.Trim('[', ']')
try {
    Import-Module PSScriptAnalyzer -RequiredVersion $version
}
catch {
    throw "PSScriptAnalyzer $version is not installed. Run 'mise run deps'."
}

if (-not $Path) {
    $Path = git -c core.quotePath=false -C $repoRoot ls-files --cached --others --exclude-standard |
        Where-Object { $_ -match '\.(ps1|psm1|psd1)$' } |
        ForEach-Object { Join-Path $repoRoot $_ } |
        Where-Object { Test-Path -LiteralPath $_ }
}

function Invoke-Analyzer {
    param([string[]]$Files)
    foreach ($file in $Files) {
        Invoke-ScriptAnalyzer -Path ([WildcardPattern]::Escape($file)) -Settings $settings
    }
}

$diagnostics = @(Invoke-Analyzer -Files $Path)

if ($Fix) {
    $bom = [byte[]](0xEF, 0xBB, 0xBF)
    $targets = $diagnostics |
        Where-Object RuleName -EQ 'PSUseBOMForUnicodeEncodedFile' |
        Select-Object -ExpandProperty ScriptPath -Unique
    foreach ($target in $targets) {
        $bytes = [System.IO.File]::ReadAllBytes($target)
        [System.IO.File]::WriteAllBytes($target, $bom + $bytes)
    }
    if ($targets) {
        $diagnostics = @(Invoke-Analyzer -Files $Path)
    }
}

if ($diagnostics.Count -gt 0) {
    $diagnostics | ForEach-Object { '{0}:{1} [{2}] {3}' -f $_.ScriptPath, $_.Line, $_.RuleName, $_.Message }
    exit 1
}
```

- `Invoke-ScriptAnalyzer` は、設定ファイルを `-Path` のディレクトリ直下からしか探しません。ファイル単位で呼ぶので `-Settings` が必須です。`-Path` は文字列1つなので、ファイルごとにループします。
- `Invoke-ScriptAnalyzer -Fix` は使いません。`-Fix` は BOM の規則単独では何もせず、他の規則の修正（エイリアスの展開など）の副作用でしか BOM を付けません。整形規則と組み合わせると、壊れた出力を書きます。

`scripts/test.ps1` は、`[PesterConfiguration]` をスクリプトの中に持ちます。`Run.Exit` は使わず、`Run.PassThru` の結果から終了コード 0 か 1 で終わります。

```powershell
#Requires -PSEdition Core
#Requires -Version <最新の LTS の major.minor>
<#
.SYNOPSIS
tests/ の Pester のテストを実行する。すべて通らなければ終了コード 1 で終わる。
#>
[CmdletBinding()]
param()

Set-StrictMode -Version 3.0
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true

$repoRoot = Split-Path -Parent $PSScriptRoot

# psresources.psd1 の版を読み込む
$pinned = Import-PowerShellDataFile -LiteralPath (Join-Path $repoRoot 'psresources.psd1')
$version = $pinned['Pester'].version.Trim('[', ']')
try {
    Import-Module Pester -RequiredVersion $version
}
catch {
    throw "Pester $version is not installed. Run 'mise run deps'."
}

$configuration = [PesterConfiguration]@{
    Run    = @{ Path = Join-Path $repoRoot 'tests'; PassThru = $true }
    Output = @{ Verbosity = 'Detailed' }
}
$result = Invoke-Pester -Configuration $configuration

if ($result.Result -ne 'Passed') {
    exit 1
}
```

- Pester が自動で読む設定ファイルはありません。設定が増えたら、`Import-PowerShellDataFile` と `New-PesterConfiguration -Hashtable` で読む形にします。
- `Run.Exit = $true`（または `-CI`）は、Linux で終了コードが 256 の剰余になり、256 件の失敗が 0 になります。使いません。

## BOM の付与

非 ASCII を含むソースは BOM 付き UTF-8 にします。付与は三段で行います。

1. 保存時: VS Code の `[powershell]` の `files.encoding` に `utf8bom` を設定します（`.vscode/settings.json` または個人設定）。`.editorconfig` の `charset = utf-8-bom` は、仕様が推奨しておらず、道具が対応しているとは限らないので使いません。
2. 検出: `PSUseBOMForUnicodeEncodedFile`（既定で有効）が、BOM の無いファイルを Warning で報告します。
3. 付与: `lint.ps1 -Fix`（`mise run fix`）が、報告されたファイルに BOM の3バイトを前置し、再解析します。

`.gitattributes` が `* text=auto` のままなら、BOM はコミットでもチェックアウトでも保たれます。グローバルの Git の設定（`core.attributesFile`）と、グローバルの attributes ファイル（既定は `$XDG_CONFIG_HOME/git/attributes`、なければ `$HOME/.config/git/attributes`）が、`working-tree-encoding` などの属性を与えて結果を左右するので、確かめるときは、`GIT_CONFIG_GLOBAL` を空のファイルに向け、`HOME` と `USERPROFILE` と `XDG_CONFIG_HOME` を空のディレクトリに向けます（`git-config` スキルが使える場合は、層の隔離の手順にも従います）。

## CI

CI では mise を入れて（GitHub Actions では `jdx/mise-action`）、`mise run check` を1ステップで実行します。汎用の項目（SHA でのピン留め、`permissions`、`concurrency`、`timeout-minutes`）は、`github-actions` スキルが使える場合はそれに従います。使えない場合は GitHub の公式ドキュメント（https://docs.github.com/en/actions/reference/security/secure-use）を参照します。PowerShell に固有の点は次の4つです。

- ステップは `run: mise run check` だけにし、`shell: bash` を明示します。PowerShell の処理が要るときは `scripts/*.ps1` にして先頭の3行を持たせ、mise タスク経由で呼びます。`shell: pwsh` のインラインコードは、先頭の3行が効かないので避けます。
- OS は Linux と Windows にします。規約が大文字小文字と OS の分岐を求めるので、Linux だけでは Windows 側の失敗を見逃します。macOS は、プロジェクトが対象に掲げたときだけ足し、`lockfile_platforms` にも足します。マトリクスは `lockfile_platforms` と同じ OS にそろえます。
- モジュールは `actions/cache` でキャッシュしません。モジュールは小さく、キャッシュポイズニングの懸念もあります。`mise-action` の既定のキャッシュ（`pwsh` 本体などのツール）は使います。
- モジュールの導入は、`mise-action` の `mise install` が走らせる `postinstall`（`deps`）に任せます。走らなければ、ラッパーが版の不一致で失敗します。そのときは `mise run deps` の明示ステップを `mise run check` の前に足します。

```yaml
jobs:
  check:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@<commit-sha> # vX.Y.Z
        with:
          persist-credentials: false
      - uses: jdx/mise-action@<commit-sha> # vX.Y.Z
      - run: mise run check
        shell: bash
```

- GitHub のホステッドランナーには `pwsh` が入っているので、CI では何も足しません。ランナーの `pwsh` が `#Requires` の版を満たさないときは、ラッパーが止まります。`ubuntu-24.04-arm` のような古い image を使っているなら、新しい image（`ubuntu-26.04-arm` など）への更新を先に勧めます。更新できないときは、mise の `[tools]` に `powershell` を足します。`jdx/mise-action` は PATH の先頭に足すので、mise の `pwsh` が優先されます。
- ランナーには Pester と PSScriptAnalyzer も事前に入っていますが、版が固定した版と違うことがあります（Pester は 5 系）。`psresources.psd1` の版を入れ直し、ラッパーが `-RequiredVersion` で読みます。
- Pester の結果ファイル（NUnit、JUnit）は既定では出しません。レポートが要るプロジェクトは、`TestResult` を有効にして自分で足します。
