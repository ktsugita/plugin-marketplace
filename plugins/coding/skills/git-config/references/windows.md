# Windows と WSL の Git の問題

Windows か WSL の Git の問題を扱うときに読みます。読み書きの規則は `SKILL.md` に従います。

Git のコマンドは、PowerShell、cmd、Git Bash で同じ形で書きます。どれも同じ `git.exe` を動かすためです。環境ごとに変わるのは、どの git が呼ばれているかの確認だけで、cmd では `where git` を使います（PowerShell と Git Bash、WSL は `SKILL.md` の診断のとおり）。

## 環境の確認

- global 層の場所は、環境変数 `HOME`、`HOMEDRIVE`+`HOMEPATH`、`USERPROFILE` の順で決まります。`XDG_CONFIG_HOME` があれば、それが global 層の1つ目のファイルの場所です。
- Git for Windows は、`XDG_CONFIG_HOME` が未設定か空のとき、`%APPDATA%\Git\config` があればそれを1つ目のファイルとして使い、`~/.config/git/config` を無視します。
- system 層は、既定のインストール先では `C:/Program Files/Git/etc/gitconfig` です。場所の正は `git var GIT_CONFIG_SYSTEM` が返すパスで、インストール先を変えた環境や portable 版では別の場所です。インストーラが選択に応じて `core.autocrlf`、`core.symlinks`、`credential.helper`、`pull.rebase`、`init.defaultBranch` などを書きます。同じキーが global 層にもあれば global 層が勝つので、インストーラの選択が実効値とは限りません。
- PATH 上の `bash` が WSL のものになっていることがあります。PowerShell で `bash` と打つと Git Bash ではなく WSL に入るので、Git Bash は、Git のインストール先の `bin\bash.exe`（既定は `C:\Program Files\Git\bin\bash.exe`）を指定して起動します。
- 層を切り分けるために `GIT_CONFIG_GLOBAL` を差し替えるとき、`NUL` を指す方法は 2.56.0.windows.1 で壊れていて、2.56.0.windows.2 で修正されました（2026-10、Git for Windows 2.56.0.windows.2 のリリースノートで確認）。版を問わず、実在する空のファイルを指します。
- `git var GIT_CONFIG_GLOBAL` が Windows のパス（`C:/...`）を返せば Windows の git.exe、`/home/<user>/...` を返せば WSL の git です。

## 症状から原因を引く

### 1. `Filename too long` でクローンやチェックアウトが失敗する

疑う原因は `core.longpaths` です。既定は無効で、260 文字を超えるパスが扱えません。実効値と出所を確かめます（単一キーの問い合わせ）。

- 既存のリポジトリなら、local 層に `core.longpaths` を書いてかまいません（`SKILL.md` の手順で承認を取ります）。
- クローン前の失敗には、`git clone -c core.longpaths=true <url>` を示します（クローンは利用者が頼んだ操作です）。
- global 層への書き込みは、提示だけです。

### 2. 全ファイルが変更扱いになる、改行の差分が大量に出る

疑う原因は `core.autocrlf` の環境間の食い違いと、`.gitattributes` です。同じ作業ツリーを Windows と WSL の両方で開くと、環境ごとに値が違うために起きます。

1. `core.autocrlf` の実効値と出所を、system 層と global 層の衝突も含めて確かめます。
2. `git ls-files --eol`（インデックス側 `i/` と作業ツリー側 `w/` と属性 `attr/`）、`git check-attr -a <path>`、`git diff --ignore-cr-at-eol --stat` で、どちらの改行が混ざっているかを確かめます。
3. 優先順位は `-text`、`eol=`、`text` 系と `core.autocrlf`、`core.eol`、プラットフォームの既定の順です。`.gitattributes` に `eol=` か `-text` があれば、そのファイルは `core.autocrlf` に従いません。

直し方は、推奨値（`references/recommended-settings.md`）に環境ごとにそろえ、作業ツリーを片方の環境に置くことです。改行の正規化し直しは `git add --renormalize .` で、利用者が頼んだときに実行します。

### 3. シンボリックリンクがテキストファイルになる

疑う原因は `core.symlinks` です。Windows の git.exe は、既定でこれを `false` として扱い、リンク先の文字列を内容とする通常ファイルとして展開します。`git ls-files -s <path>` のモードが `120000` なら、インデックスにはシンボリックリンクとして入っています。

リンクの作成には、開発者モードか「シンボリックリンクの作成」権限が要ります。環境の問題なので、書き込みは提示だけです。クローン前なら `git clone -c core.symlinks=true <url>` を示します。

### 4. HTTPS の認証が通らない

診断までを扱います。`credential.helper` の名前、層、出所だけを示し、値は示しません。`gh auth status` は使えます。`gh auth token` と `--show-token` は使いません。

- Windows の system 層の既定値 `manager` は、WSL では `credential-manager` が git コマンドとして見つからず失敗します。
- helper の指定が絶対パスなら、そのパスの存在を確かめます。
- 認証が失敗したときに、別の経路（SSH から HTTPS への切り替えなど）に切り替えません。

直すコマンドは、`SKILL.md` の規則に従って提示だけにします。

### 5. SSH の認証が通らない

診断までを扱います。

- Git が使う ssh は、インストーラの選択で決まります。同梱の OpenSSH が既定で、Plink（`GIT_SSH` が設定される）と外部の OpenSSH（同梱の ssh が消えて PATH 上の ssh が使われる）も選べます。同梱の場合は `<Git のインストール先>/usr/bin/ssh.exe` で、PowerShell の `ssh` とは別物です。ターミナルで `ssh` が通ることは、Git が通ることを意味しません。
- Windows の OpenSSH の ssh-agent は、Windows のサービスで、既定では無効です（`Get-Service ssh-agent` で確かめます）。Git 同梱の ssh が Windows の ssh-agent を使えるかは、確認していません。使われている ssh と agent を特定できないときは、特定できなかったと報告します。
- `core.sshCommand` は Git が `sh` 経由で実行するので、バックスラッシュや空白を含むパスにはクォートが要ります（`"C:/Program Files/Git/usr/bin/ssh.exe" -v` の形）。
- `GIT_SSH_COMMAND` は `core.sshCommand` に勝ち、`core.sshCommand` は `GIT_SSH` に勝ちます。環境変数は、変数名の有無だけを確かめます。

直すコマンドは、提示だけです。

### 6. Windows と WSL で設定が違う

環境の取り違えです。`SKILL.md` の診断に従い、問題の環境で実行するコマンドを提示します。WSL 側の詳細は、下の「WSL」にあります。

### 7. `core.filemode` や `core.ignorecase` が環境で食い違う

この2つは、`git init` と `git clone` が作成時の環境を調べて local 層に書きます。Windows で作ったリポジトリを WSL から開くと、作成時の値のままです。`/mnt/c`（drvfs）の上では `core.filemode=false`、`core.ignorecase=true` で、WSL の ext4 では `core.filemode=true` です。

診断のみで、値は変更しません（Git の文書が、変更は予期せぬ動作を招くと注意しています）。作業ツリーは、WSL で作業するなら WSL のファイルシステムに置きます。

## WSL

- WSL の global 層は、WSL 側の `$HOME` の下にあります。Windows の `C:\Users\<user>\...` とは別のファイルです。
- system 層は `/etc/gitconfig` で、Ubuntu の Git にはこのファイルが存在しません。Windows 側の system 層のファイル（既定は `C:\Program Files\Git\etc\gitconfig`）は、WSL の Git からは読まれません。
- WSL で HTTPS の認証を通すときは、`gh auth setup-git` を提示します（利用者が自分で実行します）。Windows 側の `credential.helper = manager` は WSL では使えず、Windows 側の GCM の exe を指す設定も勧めません。SSH で足りる場合は、SSH を使います（`SKILL.md` の規則どおり、承認なしに切り替えません）。
- Windows 側で作った worktree の `.git` ファイルは、Windows の絶対パスを持ちます。WSL の Git では開けず、`fatal: not a git repository` で失敗します。作業ツリーは、片方の環境に置きます。
