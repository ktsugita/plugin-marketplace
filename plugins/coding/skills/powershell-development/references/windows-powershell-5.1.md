# Windows PowerShell 5.1 との互換

対象は PowerShell 7 以降です。このファイルは、プロジェクトの要件が Windows PowerShell 5.1（`powershell.exe`）のときに、既存のコードを壊さないための注意だけを挙げます。5.1 で動くコードを新しく書く方針ではありません。

5.1 要件のプロジェクトでは、次のことを守ります。

- `#Requires -PSEdition Core` を付けません。5.1 では `Desktop` です。`#Requires -Version` は、プロジェクトの要件の版にします。
- `SKILL.md` の規約のうち、5.1 で使えないもの（下の一覧）を避けます。先頭の3行の3行目（`$PSNativeCommandUseErrorActionPreference`）は、5.1 には変数が無いので置きません。
- 5.1 と 7 の両方で動かすコードは、両方の環境で実行して確かめます。

差が出る項目は次のとおりです。実測値や回避の詳細は載せません。Microsoft Learn の差分の文書（https://learn.microsoft.com/powershell/scripting/whats-new/differences-from-windows-powershell）と、文字コードの文書（https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_character_encoding）で確かめます。

- OS の分岐: `$IsWindows`、`$IsLinux`、`$IsMacOS` は 5.1 に存在せず、`Set-StrictMode` 下では参照するとエラーになります。5.1 は Windows 専用なので、5.1 で動かすコードでは、`$PSVersionTable.PSEdition -eq 'Desktop'` で判定します。
- 構文: 三項演算子（`? :`）、`??`、`??=`、`?.`、`?[]`、`&&`、`||` は 5.1 で構文エラーになります。`ForEach-Object -Parallel`、`Join-String`、`Test-Json`、`ConvertFrom-Json -AsHashtable` など、7 で加わったコマンドレットやパラメーターも使えません。
- 既定のエンコーディングと BOM: `Out-File`、`>`、`>>` の既定が違います（5.1 は UTF-16LE、7 は BOM なし UTF-8）。`-Encoding utf8` は、5.1 では BOM 付きで、7 では BOM なしです（7 で BOM が要るときは `utf8BOM`）。非 ASCII を含むスクリプトファイルは、BOM が無いと 5.1 では ANSI として読まれます。`$OutputEncoding` の既定も違います。
- ネイティブコマンドの引数渡しと stderr: 引数中の `"` や空文字列の渡し方が違います（`$PSNativeCommandArgumentPassing`）。`$ErrorActionPreference = 'Stop'` のもとで、`2>&1` でつないだネイティブコマンドの stderr が、5.1 では例外になります。
- `ConvertTo-Json` と `ConvertFrom-Json`: `ConvertTo-Json` の日付の形式と `-Depth` を超えたときの警告が違います。`ConvertFrom-Json` は、配列を 5.1 では1つのオブジェクトとして、7 では展開して出力します。
- 実行基盤: 5.1 は .NET Framework、7 は .NET です。メソッドの挙動が違うことがあります（たとえば `String.Split` に複数文字の文字列を渡したとき）。

5.1 要件のプロジェクトでも、既存のコードを 7 向けに書き換えません。PowerShell 7 以降が使える環境では、`SKILL.md` に従います。
