---
name: powershell-development
description: PowerShell 7 以降のスクリプト（.ps1）とモジュール（.psm1、.psd1）の作成・編集、Pester によるテスト、PSScriptAnalyzer による静的解析、そのツールチェーンの導入を行うときに使用する。Windows PowerShell 5.1 との互換の注意を含む。
license: MIT
---

PowerShell 7 以降（`pwsh`）のスクリプトとモジュールを書くときは、以下のガイドラインに従ってください。
プロジェクトにすでに仕組みがある場合（`build.ps1`、psake、InvokeBuild、Pester 5、独自の設定など）は、それを尊重します。ツールチェーンが無いプロジェクトでは、導入を提案し、承認されてから `references/toolchain.md` に従います。
規約は、新しく書くファイルと編集する箇所に適用します。

- ツールチェーンを新しく入れるとき、利用者が導入を承認したとき、または `scripts/lint.ps1` や `psresources.psd1` が無いプロジェクトで品質検証を動かすときは、`references/toolchain.md` を読みます。
- プロジェクトの要件が Windows PowerShell 5.1 のときは、`references/windows-powershell-5.1.md` を読みます。
- PowerShell の公式ドキュメントは Microsoft Learn（https://learn.microsoft.com/powershell/）、Pester は https://pester.dev/ を参照します。

## `pwsh` の導入

`pwsh` は、すでに入っているものを使います。入れ直しません。

1. `pwsh --version`（どのシェルでも動く）で、`pwsh` が PATH にあるか、版が規約の `#Requires -Version`（最新の LTS の major.minor）以上かを確かめます。最新の LTS は、Microsoft Learn のサポートライフサイクル（https://learn.microsoft.com/powershell/scripting/install/powershell-support-lifecycle）で確かめます。
2. 満たしていれば、そのまま使います。ラッパーも `#Requires` で下限を検査するので、古い `pwsh` では実行時に止まります。
3. `pwsh` が無い、または古いときは、利用者に導入を促します。コマンドを実行するのは、利用者が承認してからです。方法は `references/pwsh-install.md` に従います。

手元、フック、CI で `pwsh` の版を固定したいときも、`references/pwsh-install.md` の最後の項に従います。

## コマンド対応表

操作は mise のタスクに集め、PowerShell を直接呼ぶときは `pwsh -NoProfile -File` を使います。

| 操作 | 推奨 | アンチパターン |
|---|---|---|
| 検査（リントと全テスト） | `mise run check` | 素の `Invoke-ScriptAnalyzer` と `Invoke-Pester` |
| テスト | `mise run test` | `Invoke-Pester`（設定も版の検査も通らない） |
| 修正（BOM の前置） | `mise run fix` | `Invoke-ScriptAnalyzer -Fix`、`Invoke-Formatter` |
| モジュールの導入 | `mise run deps` | `Install-Module`（旧来の PowerShellGet） |
| スクリプトの実行 | `pwsh -NoProfile -File <script.ps1>` | `powershell.exe`、shebang を付けて直接実行 |

## ファイル配置

```
psresources.psd1                 ← PSScriptAnalyzer と Pester の版（完全一致）
PSScriptAnalyzerSettings.psd1    ← PSScriptAnalyzer の設定（ExcludeRules など）
mise.toml
hk.pkl
scripts/
  lint.ps1                       ← PSScriptAnalyzer のラッパー
  test.ps1                       ← Pester のラッパー
src/<Name>/
  <Name>.psd1                    ← モジュールのマニフェスト
  <Name>.psm1
tests/<Name>/
  <Name>.Tests.ps1               ← src と同じ構造
```

- 宣言ファイルは小文字の `psresources.psd1` です。PSDepend の `requirements.psd1` とは書式が互換でないので、同名にしません。
- モジュールを置くフォルダーの名前は、モジュール名と同じにします。公開する関数と内部の関数が増えたら `Public/` と `Private/` に分けます（閾値は決めません）。
- プロジェクト自身の入口スクリプトの置き場所は、このスキルでは決めません。
- `.gitignore` に `testResults.xml` と `coverage.xml` を足します（Pester の既定の出力先）。
- `.gitattributes` は `* text=auto` のままにします。BOM は保たれます。

## 環境変数と秘密情報

環境変数や秘密情報の置き場所は、`mise` スキルが使える場合はそれに従います。使えない場合は mise の公式ドキュメントを参照します。PowerShell 固有の点は次の2つです。

- 環境変数は `$env:NAME` で読み書きします。
- `.env` を読み込む標準の機能は PowerShell にありません。`mise.toml` の `[env]` の `_.file` で、プロセスの環境変数として渡します。

## 規約

PSScriptAnalyzer の既定で有効な規則を基準にします。`Write-Host` の禁止、承認された動詞、エイリアス、`Invoke-Expression` など、規則が検査するものは、`Invoke-ScriptAnalyzer` の結果に従います。以下は、規則が検査しない選択です。

### 版の宣言

入口スクリプトの先頭に `#Requires -PSEdition Core` と `#Requires -Version <最新の LTS の major.minor>` を置きます。モジュールはマニフェストの `CompatiblePSEditions = @('Core')` と `PowerShellVersion` に書きます。

- 版番号は書かず、LTS を調べて入れます（上の「`pwsh` の導入」）。「安定版」という語は、Microsoft Learn が LTS の間に出る非 LTS を指して使うので、使いません。
- 5.1 で動かすと、構文エラーより先にエディションの不一致で止まります。
- 既存のプロジェクトで、宣言済みの要件(スクリプトの `#Requires -Version`、モジュールの `PowerShellVersion`)が最新の LTS より古いときは、要件を最新の LTS に上げることを先に提案します。上げないと決まったら、その要件の版で動くコードを書きます。古い版には、次の「先頭の3行」の3行目（`$PSNativeCommandUseErrorActionPreference`）が使えないものがあります。

### 先頭の3行

入口スクリプトは `param` の直後に、`.psm1` はファイルの先頭に、次の3行を置きます。

```powershell
Set-StrictMode -Version 3.0
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true
```

- `$ErrorActionPreference = 'Stop'` が無いと、`pwsh -File` は失敗しても終了コード 0 を返し、フックと CI が検出できません。
- `Set-StrictMode` の `Latest` は、新しい版で意味が変わりえます。版を書きます。
- モジュールには、呼び出し側の StrictMode が届きません。`.psm1` にも置きます。
- 終了コードが非 0 でも正常なコマンドは、その範囲だけ `$PSNativeCommandUseErrorActionPreference = $false` にして `$LASTEXITCODE` を見ます。

### 外部コマンド

引数は配列にして `& <コマンド> @引数の配列` で呼びます。文字列を組み立てて実行しません。`cmd.exe`、`.bat`、`.cmd` を呼ぶときは、引数渡しが `Legacy` になる点に注意します。

### 骨格

```powershell
#Requires -PSEdition Core
#Requires -Version <最新の LTS の major.minor>
<#
.SYNOPSIS
何をするスクリプトかを1行で書く。
.EXAMPLE
pwsh -NoProfile -File scripts/example.ps1 -Name World
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$Name
)

Set-StrictMode -Version 3.0
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true

"Hello, $Name"
```

- `[CmdletBinding()]` と型つきの `param` は必須です。
- 検証属性（`ValidateSet` など）は、値の集合が決まるときだけ付けます。
- コメントベースのヘルプは、入口スクリプトと公開関数に付けます。必須の見出しは `.SYNOPSIS` と `.EXAMPLE` です。
- `[OutputType()]` は、オブジェクトを返す公開関数だけに付けます。
- `SupportsShouldProcess` は、規則（`PSUseShouldProcessForStateChangingFunctions`）に従います。

### 出力とエラー

- 関数はオブジェクトを返します。`Write-Output` は書きません。
- ログと進行表示は `Write-Verbose`、`Write-Warning`、`Write-Information` を使います。見せたいときは `-InformationAction Continue` を付けます。
- 致命的なエラーは `throw` します。終了コードは `Stop` 下の未処理の例外に任せ、特定の値が要るときだけ `exit N` を使います。

### パスと OS

- パスは `Join-Path` と `$PSScriptRoot` で組み立てます。外部入力のパスは `-LiteralPath` で渡します。
- OS の分岐は `$IsWindows`、`$IsLinux`、`$IsMacOS` で行います。Windows 専用の機能は分岐で囲み、ファイルの冒頭に明記します。
- ファイル名の大文字小文字は、実際の綴りどおりに書きます（Linux では区別されます）。拡張子は小文字（`.ps1`、`.psm1`、`.psd1`）に統一します。hk の glob が大文字小文字を区別するため、`.PS1` は検査から漏れます。
- 改行は `.gitattributes` に任せ、コードでは扱いません。

### 文字コード

- PowerShell のソース（`.ps1`、`.psm1`、`.psd1`、`*.Tests.ps1`）は、非 ASCII（日本語のコメントなど）を含むなら BOM 付き UTF-8 にします。ASCII だけなら問いません。BOM の検出は `PSUseBOMForUnicodeEncodedFile`（既定で有効）に任せ、除外しません。
- BOM を付けたファイルに shebang は書けません（Linux でカーネルが `#!` を認識せず、終了コード 127 になります）。
- Excel で開く CSV は `-Encoding utf8BOM` で書きます。それ以外のファイルの読み書きは、既定の BOM なし UTF-8 に任せます。
- BOM は、保存時に VS Code で付け、付け忘れた分は `mise run fix`（`lint.ps1 -Fix`）が前置します。仕組みは `references/toolchain.md` の「BOM の付与」に従います。

### 規則の抑止

- 個別の違反は `SuppressMessageAttribute` で抑止し、`Justification` を必ず付けます。
- プロジェクト全体の除外は、`PSScriptAnalyzerSettings.psd1` の `ExcludeRules` に、理由のコメントを添えて書きます。
- 規則名は `PS` 接頭辞つきの完全名で書き、`Get-ScriptAnalyzerRule -Name <規則名>` で存在を確かめます。存在しない規則名はエラーにならず、黙って無視されます。
- コメントによる抑止は使いません（公式の機能ではありません）。

```powershell
function Get-Example {
    [Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSReviewUnusedParameter', 'Legacy', Justification = '呼び出し側との互換のために残す')]
    [CmdletBinding()]
    param([string]$Legacy, [string]$Name)

    $Name
}
```

### モジュール

マニフェストの `FunctionsToExport` に、公開する関数を完全一致で列挙します。`Export-ModuleMember` は書きません。公開リストを1か所にするためです。

```powershell
@{
    RootModule           = 'Example.psm1'
    ModuleVersion        = '0.1.0'
    GUID                 = '<New-Guid で作る>'
    PowerShellVersion    = '<最新の LTS の major.minor>'
    CompatiblePSEditions = @('Core')
    FunctionsToExport    = @('Get-Example')
    CmdletsToExport      = @()
    VariablesToExport    = @()
    AliasesToExport      = @()
}
```

- 1ファイルで完結する処理は `.ps1` にします。関数を共有したいとき、または関数単位でテストしたいときは、モジュールに切り出します。
- ワイルドカードでの公開や、必須項目の欠落は、既定の規則が検査します。

## テストと品質管理

### テスト規約

テストは Pester 6 で書き、版は `psresources.psd1` で完全一致に固定します。Pester 6 は約3か月で4回出ていて、minor でも挙動が変わるので、範囲指定にはしません。

- アサーションは、クラシックな `Should -Be` を使います。Pester 5 と 6 の両方で動きます。`Should-*` は 6 だけで動きます。
- テストは `tests/` に、`src` と同じ構造の `*.Tests.ps1` として置きます。
- Pester 6 は、ファイルごとに discovery して実行します。各ファイルを自己完結にし、`BeforeAll` で `$PSScriptRoot` からの相対でマニフェストを import します（スクリプトなら dot-source します）。

```powershell
BeforeAll {
    Import-Module (Join-Path $PSScriptRoot '../../src/Example/Example.psd1') -Force
}

Describe 'Get-Example' {
    It 'returns the name' {
        Get-Example -Name 'World' | Should -Be 'World'
    }
}
```

Pester 6 で注意する点は次の3つです。

- `-ForEach` に `$null` や空の配列を渡すと、discovery が失敗します。
- `-ParameterFilter` に一致しない `Mock` の呼び出しは、実コマンドに落ちずにエラーになります。フィルターなしの既定の `Mock` も置きます。
- 隠しフォルダー内の `*.Tests.ps1` も拾われます（5 は拾いません）。

### 品質検証コマンド

変更をコミットまたはプルリクエストにする前に、次の順で実行します。失敗とみなす重大度は、すべてです。

```bash
mise run fix     # 非 ASCII を含むファイルに BOM を前置する
mise run check   # PSScriptAnalyzer（hk 経由）と Pester
mise run test    # Pester だけを走らせるとき
```

- `lint.ps1 -Fix` が行うのは BOM の前置だけです。整形はしません。`Invoke-Formatter` と整形系の規則は使いません。
- `mise run` のタスクが無いプロジェクトでは、`pwsh -NoProfile -File scripts/lint.ps1` と `pwsh -NoProfile -File scripts/test.ps1` を直接呼びます。スクリプトも無ければ、`references/toolchain.md` に従って導入を提案します。
