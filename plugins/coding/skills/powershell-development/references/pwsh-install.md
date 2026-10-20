# `pwsh` の導入

`pwsh` が無い、古い、または版を固定したいときに読みます。導入のコマンドを実行するのは、利用者が承認してからです。環境ごとの標準的な方法は次のとおりです。

| 環境 | 導入の方法 |
|---|---|
| Windows | `winget install --id Microsoft.PowerShell --source winget`（Microsoft が Windows クライアントに推奨する方法） |
| Ubuntu | Microsoft のパッケージリポジトリから `apt` で入れる（Microsoft が preferred とする方法。下の手順）。WSL でも使える |
| macOS | Learn の macOS のページから、署名された pkg を入れる（Homebrew の formula はコミュニティの保守） |
| その他の Linux | Learn の各ディストリビューションのページに従う |

Ubuntu の手順は次のとおりです（Learn の Ubuntu のページの手順を縮めたもの）。Microsoft がパッケージを公開している Ubuntu の版でだけ動きます。Ubuntu の .NET のパッケージと混在すると問題が出るので、`.NET` も同じ環境で使うときは、Learn の注意を読みます。

```bash
sudo apt-get update && sudo apt-get install -y wget
source /etc/os-release
wget -q "https://packages.microsoft.com/config/ubuntu/${VERSION_ID}/packages-microsoft-prod.deb"
sudo dpkg -i packages-microsoft-prod.deb && rm packages-microsoft-prod.deb
sudo apt-get update && sudo apt-get install -y powershell
```

- 手順は更新されるので、細部は Learn（https://learn.microsoft.com/powershell/scripting/install/installing-powershell）で確かめます。
- OS のパッケージ（apt、rpm など）は、依存（libicu など）も引きます。tar.gz を展開する方法（mise の導入を含む）では、libicu が無い最小の Linux で、`pwsh` が起動時に止まります。そのときは、ディストリビューションのパッケージマネージャーで libicu を入れます。`DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1` でも起動しますが、カルチャが空になり、日付や並べ替えなどの挙動が変わりえるので、globalization を使わないと確かめたプロジェクトでだけ使います。
- 手元、フック、CI で `pwsh` の版を固定したいプロジェクトでは、mise で入れる手もあります。`[tools]` と `mise.lock` の書き方は、`mise` スキルの「PowerShell との連携」に従います。
