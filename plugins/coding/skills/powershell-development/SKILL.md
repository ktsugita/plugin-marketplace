---
name: powershell-development
description: PowerShell 7 以降のスクリプト（.ps1）とモジュール（.psm1、.psd1）の作成・編集、Pester によるテスト、PSScriptAnalyzer による静的解析、そのツールチェーンの導入を行うときに使用する。Windows PowerShell 5.1 との互換の注意を含む。
license: MIT
---

# PowerShell 開発ガイドライン

PowerShell 7 以降（`pwsh`）を対象とします。プロジェクトに既存の仕組み（`build.ps1`、psake、InvokeBuild、Pester 5、独自設定など）がある場合はそれを尊重します。規約は新しく書くファイルと編集する箇所に適用します。

- ツールチェーン（`psresources.psd1`、`scripts/lint.ps1`、`scripts/test.ps1`、`mise.toml`、`hk.pkl`）を新規導入・確認するときは、`references/toolchain.md` を読みます。
- `pwsh` が未導入・古いとき、または `mise.toml` で `pwsh` の版を固定するときは、`references/pwsh-install.md` を読みます（既存の `pwsh` が最新の LTS 以上なら入れ直しません）。
- Windows PowerShell 5.1（`powershell.exe`）との互換が求められるときは、`references/windows-powershell-5.1.md` を読みます。

## 実行と構成の要点

- PowerShell スクリプトの直接実行には `pwsh -NoProfile -File <script.ps1>` を使い、モジュール管理には PSResourceGet（`psresources.psd1` と `Install-PSResource`）を使います。
- `.env` を読み込む標準機能は PowerShell にないため、環境変数は `mise.toml` の `[env]`（および `_.file = ".env"`）で渡し、`$env:NAME` で参照します。
- 拡張子は小文字（`.ps1`、`.psm1`、`.psd1`）に統一し、ファイル名の大文字小文字も実際の綴りに合わせます（`hk` の glob と Linux 環境は大文字小文字を区別するため）。`.gitignore` には Pester の既定出力 `testResults.xml` と `coverage.xml` を含めます。

## コーディング規約

PSScriptAnalyzer の既定規則に加え、規則が検査しない次の点を守ります。

### 1. 版の宣言と先頭の3行

入口スクリプトの先頭には `#Requires -PSEdition Core` と `#Requires -Version <最新の LTS の major.minor>`（Microsoft Learn のサポートライフサイクルで確認）を置きます（モジュールは `.psd1` の `CompatiblePSEditions = @('Core')` と `PowerShellVersion` に記載）。既存プロジェクトの要件が最新の LTS より古い場合は、引き上げを提案し、据え置くならその版で動くコードを書きます。

入口スクリプトの `param` の直後と、`.psm1` の先頭（呼び出し側の StrictMode が届かないため）には次の3行を置きます。

```powershell
Set-StrictMode -Version 3.0
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true
```

- `$ErrorActionPreference = 'Stop'` が無いと、`pwsh -File` が失敗しても終了コード 0 になり、フックや CI が失敗を検出できません。
- 終了コードが非 0 でも正常な外部コマンドを呼ぶ箇所だけ、一時的に `$PSNativeCommandUseErrorActionPreference = $false` にして `$LASTEXITCODE` を検査します。
- 外部コマンドの引数は配列で `& <コマンド> @引数の配列` として渡し、`cmd.exe` / `.bat` / `.cmd` の引数渡しが `Legacy` になる点に注意します。

### 2. 関数・モジュール・出力

- 入口スクリプトと公開関数には `[CmdletBinding()]`、型つき `param`、`.SYNOPSIS` と `.EXAMPLE` を含むコメントベースヘルプを付け、オブジェクトを返す公開関数には `[OutputType()]` を付けます。
- 関数はオブジェクトを直接返し（`Write-Output` は書かない）、ログには `Write-Verbose` / `Write-Warning` / `Write-Information`、致命的エラーには `throw` を使います。
- パスは `Join-Path` と `$PSScriptRoot` で組み立て、外部入力パスは `-LiteralPath` で渡します。OS 分岐には `$IsWindows` / `$IsLinux` / `$IsMacOS` を使います。
- モジュールの公開関数は `.psd1` の `FunctionsToExport` に完全一致で列挙し、`.psm1` 側には `Export-ModuleMember` を書きません（公開リストを1か所に保つため）。

### 3. 文字コード（BOM）

- 非 ASCII（日本語コメントなど）を含む `.ps1`、`.psm1`、`.psd1`、`*.Tests.ps1` は BOM 付き UTF-8 にします（`PSUseBOMForUnicodeEncodedFile` で検出し、`mise run fix` の `lint.ps1 -Fix` で BOM を前置します）。
- BOM 付きファイルには shebang（`#!`）を書けません（Linux カーネルが認識せず終了コード 127 で失敗するため）。
- Excel 向け CSV は `-Encoding utf8BOM` で書き、それ以外の一般ファイルの読み書きは既定の BOM なし UTF-8 に任せます。

### 4. PSScriptAnalyzer の規則抑止

- 個別抑止は `[Diagnostics.CodeAnalysis.SuppressMessageAttribute('PS...', 'Target', Justification = '理由')]`、全体除外は `PSScriptAnalyzerSettings.psd1` の `ExcludeRules`（理由コメントつき）で行います。
- 規則名は `PS` 接頭辞つきの完全名を使い、`Get-ScriptAnalyzerRule -Name <規則名>` で実在を確かめます（存在しない規則名はエラーにならず無視されるため）。コメントによる抑止機能はありません。

## テスト（Pester 6）と品質検証

テストは `tests/` 配下に `*.Tests.ps1` として置き、Pester 5/6 両対応のクラシックな `Should -Be` アサーションを使います。各ファイルは `BeforeAll` で `$PSScriptRoot` からの相対パスによって対象マニフェストを `Import-Module -Force`（スクリプトなら dot-source）して自己完結させます。

Pester 6 では次の3点に注意します。

- `-ForEach` に `$null` や空配列を渡すと discovery が失敗します。
- `-ParameterFilter` に一致しない `Mock` 呼び出しは実コマンドにフォールバックせずエラーになるため、フィルターなしの既定 `Mock` も置きます。
- 隠しフォルダー内の `*.Tests.ps1` も探索対象になります。

変更をコミットまたは PR にする前に、次を実行してすべての重大度の指摘とテストが通ることを確かめます。

```bash
mise run fix     # 非 ASCII を含むファイルへの BOM 前置（整形は行わない）
mise run check   # PSScriptAnalyzer と Pester
```

`mise` タスクが無いプロジェクトでは、`pwsh -NoProfile -File scripts/lint.ps1` と `pwsh -NoProfile -File scripts/test.ps1` を実行します。
