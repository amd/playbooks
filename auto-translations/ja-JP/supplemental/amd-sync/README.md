<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機械翻訳。** このページは英語から自動的に翻訳されたものであり、人による確認は行われていません。誤りが含まれている場合や、特定の手順、コマンド、ダウンロード、製品の提供状況、その他のコンテンツが言語や地域によって異なる場合があります。内容に矛盾または相違がある場合は、playbookの原文である英語版が優先されるものとします。
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# AMD Sync によるリモート開発

## 概要

**AMD Sync** は、お使いのノート PC を AMD Ryzen™ AI Halo のリモートコックピットに変えます。手動での SSH、キー、IDE のセットアップは不要です。AMD Sync をインストールするだけで、リモートターミナル、VS Code、JupyterLab、そして GPU/CPU/メモリのライブダッシュボードにワンクリックでアクセスできます。

ローカルマシンはそのままの使い慣れた環境を保ちつつ、すべてのコマンド、ノートブック、モデルは Ryzen AI Halo 上で実行されます。

> **ヒント**: このページには AMDSync に関する最新の更新情報が掲載されます。

## このページで学べること

- Ryzen AI Halo で SSH を有効化し、AMD Sync から接続する方法
- ワンクリックで Ryzen AI Halo に対して VS Code、ターミナル、JupyterLab、Live Metrics を起動する方法
- AMD Sync のマネージドプロジェクトフォルダを使ってリモート作業を整理する方法

---

## 主要な概念

AMD Sync には 2 つの側面があります。**クライアント**(AMD Sync アプリを実行するお使いのノート PC)と、**サーバー**(AMD Sync がトンネルする SSH サーバーを実行する Ryzen AI Halo)です。AMD Sync から起動するすべてのもの — VS Code、ターミナル、ノートブック — はローカルで開きますが、実際の処理は Ryzen AI Halo 上で実行されます。

> **サポートされるクライアント:** Windows 11 および Linux。macOS はサポートされていません。

---

## ステップ 1 — Ryzen AI Halo で SSH を有効化する


> **注:** Windows では、Ryzen AI Halo は *デフォルトで SSH サーバーがオフ* の状態で出荷されます。Linux では、*デフォルトで SSH サーバーがオン* になっています。

1. Ryzen AI Halo で **AMD Ryzen™ AI Developer Center** を開きます。
2. **Remote** タブに移動します。
3. **SSH Server** をオンに切り替えます。
4. **Server Information** の下に表示される **IP Address**、**Port**、**Username** をメモしておきます。これらを AMD Sync に貼り付けます。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **注:** これは Windows 版の AMD Developer Center です。Linux 版は UI が異なる場合がありますが、リモート機能は同様です。

> **ヒント:** AMD Sync が求めるのは、そのユーザーの **OS ログインパスワード** であり、Developer Center のパスワードではありません。

---

## ステップ 2 — クライアントに AMD Sync をインストールする

AMD Sync は Windows 11 と Linux で動作します。お使いの OS に対応したインストーラーをダウンロードし、以下の手順に従ってください。インストール後、**Get Started** 画面で **Accept & Install** をクリックすると、AMD Sync が自動的に起動します。

### Windows

[AMDSyncInstaller.exe をダウンロード](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. `AMDSyncInstaller.exe` をダブルクリックします。
2. **Accept & Install** をクリックします。

> Windows ファイアウォールから確認を求められた場合は、AMD Sync が Ryzen AI Halo に SSH 経由でアクセスできるようにネットワークアクセスを許可してください。

### Linux

お好みの形式のリンクをクリックしてダウンロードしてください。

| 形式 | ダウンロード | インストールコマンド |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **注:** Ubuntu App Center は、ローカルで開いた `.deb` を *「潜在的に安全でない」* とフラグ付けする場合があります。これはサードパーティ製のローカルインストーラーに共通する標準的な警告です。`.deb` をダブルクリックしても失敗する場合は、上記のターミナルコマンドを使用してください。

---

## ステップ 3 — Ryzen AI Halo に接続する

初回起動時、AMD Sync には **Add a Remote Device** フォームが表示されます。Developer Center の **Remote** タブに表示された値を使って入力してください。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| フィールド | 備考 |
|-------|-------|
| **Device Name**(任意) | `Ryzen AI Halo` のような分かりやすいラベル。デフォルトでは `Device 1`、`Device 2`、… となります。 |
| **Hostname or IP** | Remote タブから取得 |
| **SSH Port** | Remote タブから取得(数字のみ) |
| **Username** | Ryzen AI Halo 上の OS アカウント名 |
| **Password** | OS ログインパスワード — 入力中は伏せ字表示されます |

**Add Device** をクリックします。短い読み込み画面の後、**「Connection Successful」** と表示され、システムトレイに常駐するホーム画面に移動します。ウィンドウの外側をクリックすると閉じますが、AMD Sync はバックグラウンドで動作し続け、いつでもワンクリックでアクセスできます。

> **接続に失敗した場合、** AMD Sync は入力済みの値を保持したままフォームに戻ります。よくある原因は、Ryzen AI Halo で SSH が無効になっている、パスワードが間違っている、または 2 つのデバイスが異なるネットワーク上にあることです。

---

## ステップ 4 — 初めてのリモートツールを起動する

ホーム画面には、クライアントと Ryzen AI Halo がどの OS で動作しているかに関わらず利用できる、5 つのワンクリックコンポーネントが用意されています。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| コンポーネント | 内容 |
|-----------|--------------|
| **Directory** | VS Code、ターミナル、JupyterLab が開く Ryzen AI Halo 上のフォルダを選択します。デフォルトではマネージドの `Documents/AMD_Sync` ワークスペースになります。 |
| **VS Code** | 選択したフォルダに SSH トンネルで接続した状態で、VS Code をローカルで開きます。 |
| **Terminal** | 選択したフォルダで、Ryzen AI Halo に SSH 接続されたローカルターミナルを開きます。 |
| **JupyterLab** | 選択したフォルダを対象範囲として、Ryzen AI Halo に SSH 接続されたノートブックプロジェクトを起動します。 |
| **Live Metrics** | Ryzen AI Halo 上の GPU、メモリ、CPU 使用率をリアルタイムで表示します。 |

### VS Code を試す

初回の起動として、**VS Code** を試してみましょう。

1. **Directory** はデフォルトの `~/Documents/AMD_Sync` のままにします。
2. **VS Code** をクリックします。
3. AMD Sync は Ryzen AI Halo 上に `Documents/AMD_Sync/Project_1` を作成し、そこにトンネル接続した状態で VS Code をローカルで開きます。

これで、ローカルの VS Code 環境から Ryzen AI Halo 上にあるファイルを編集できるようになりました。`helloworld.py` を作成し、`print("hello world")` を追加して、統合ターミナル(`` Ctrl + ` ``)を開き、実行してみましょう。

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

ステータスバーには **SSH: Linux** と表示されます。これは、コードがお使いのノート PC ではなく Ryzen AI Halo 上で実行されている証です。
### ターミナルを試す

**Terminal** をクリックすると、キーボードから手を離すことなく、SSH経由で同じフォルダに入ることができます。

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Windowsでは、デフォルトのターミナルは**PowerShell**です。お好みで、Settingsメニューから**Windows Command Prompt**に切り替えることができます。Linuxでは、AMD Syncはシステムのデフォルトターミナルを使用します。

---

## Directoryの仕組み

**Directory** ドロップダウンは、AMD Syncで最も重要な単一のコントロールです。起動する各ツールがRyzen AI Haloのどこに配置されるかを決定します。

- **`~/Documents/AMD_Sync`（デフォルト）** — ここからVS CodeやJupyterLabを起動すると、新しいプロジェクトフォルダが自動的に作成されます（VS Codeの場合は`Project_1`、`Project_2`、…、JupyterLabの場合は`Notebook_Project_1`、`Notebook_Project_2`、…）。
- **既存のプロジェクトフォルダ** — `AMD_Sync`の直下にあるフォルダ（Ryzen AI Haloで手動作成したフォルダを含む）はすべてドロップダウンに表示されます。最後に使用したフォルダが、次回のデフォルトになります。
- **カスタムパス** — 任意の絶対パスを入力すると、Ryzen AI Halo上の別の場所にあるフォルダを開くことができます。AMD Syncはそのフォルダを*開く*だけです。`AMD_Sync`の外にフォルダを作成することはなく、カスタムパスはセッション間で保存されません。

カスタムパスがうまく機能しない場合、AMD Syncはその理由を教えてくれます。構文が無効、フォルダが存在しない、またはパスがファイルを指しているといった具合です。

---

## Live MetricsとJupyterLab

- **Live Metrics** — GPU、メモリ、CPU使用率をリアルタイムで表示するダッシュボードです。リモートのトレーニング実行が実際にハードウェアに負荷をかけているかを確認する最速の方法です。
- **JupyterLab** — Ryzen AI HaloにSSH接続された完全なノートブックプロジェクトで、統合ターミナルを備えているため、UIから離れることなくノートブックセルとシェルコマンドを組み合わせて使用できます。

---

## Settingsと複数デバイス

**Settings** メニューには3つのタブがあります。

| タブ | 内容 |
|-----|----------------|
| **Devices** | これまでに正常に接続したすべてのRyzen AI Haloを一覧表示します。再接続、認証情報の編集、新しいデバイスの追加ができます。 |
| **Information** | ドキュメントとフォーラムサポートへのリンクです。 |
| **Customize** | デスクトップ上でのアプリの位置を変更したり、ターミナルの種類を切り替えたり（Windowsのみ）、AMD Syncのアップデートを確認したりできます。 |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **ターミナルの種類（Windows）** — **PowerShell**（デフォルト）と**Windows Command Prompt**のいずれかを選択できます。
- **ターミナルの種類（Linux）** — デフォルトのシステムターミナルのみ利用可能です。
- **アプリのアップデート** — このタブは、UI内から新しいAMD Syncバージョンを確認・インストールするのに適した場所です。別途アップデーターは必要ありません。

> デバイスは、初回接続に成功した後にのみ**Devices**に表示されるため、失敗した試行が一覧を煩雑にすることはありません。

---

## トラブルシューティング

- **接続がすぐに失敗する** — Developer CenterのRyzen AI Haloの**Remote**タブで、SSHサーバーが有効になっていることを確認してください。
- **パスワードが違うというエラー** — Ryzen AI Haloでは、Developer Centerから取得したパスワードではなく、**OSログインパスワード**を使用してください。
- **VS Codeボタンを押しても何も起こらない** — クライアントマシンに[code.visualstudio.com](https://code.visualstudio.com)からVS Codeをインストールしてください。
- **AMD Syncのトレイアイコンが表示されない（Linux/GNOME）** — AppIndicator拡張機能をインストールして有効化してください。
- **ファイルマネージャーから`.deb`を開けない** — ターミナルから`sudo apt install ./AMDSyncInstaller.deb`を使用してください。

---