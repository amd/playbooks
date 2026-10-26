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

**AMD Sync** は、お使いのノート PC を AMD Ryzen™ AI Halo のリモートコックピットに変えます。手動での SSH、鍵、IDE のセットアップは不要です。AMD Sync をインストールするだけで、リモートターミナル、VS Code、JupyterLab、そして Ryzen AI Halo のライブ GPU/CPU/メモリダッシュボードにワンクリックでアクセスできます。

お使いのローカルマシンはこれまで通りの使い勝手のままで、すべてのコマンド、ノートブック、モデルは Ryzen AI Halo 上で実行されます。

> **ヒント**: このページには AMDSync への新しい更新内容が随時掲載されます。

## このページで学べること

- Ryzen AI Halo 上で SSH を有効化し、AMD Sync から接続する方法
- Ryzen AI Halo に対してワンクリックで VS Code、Terminal、JupyterLab、Live Metrics を起動する方法
- AMD Sync の管理されたプロジェクトフォルダを使ってリモート作業を整理する方法

---

## コアコンセプト

AMD Sync には 2 つの側面があります。**クライアント**(AMD Sync アプリを実行しているお使いのノート PC)と、**サーバー**(AMD Sync がトンネル接続する SSH サーバーを実行している Ryzen AI Halo)です。AMD Sync から起動するもの — VS Code、ターミナル、ノートブック — はすべてローカルで開きますが、実行は Ryzen AI Halo 上で行われます。

> **サポートされるクライアント:** Windows 11 および Linux。macOS はサポートされていません。

---

## ステップ 1 — Ryzen AI Halo で SSH を有効化する


> **注記:** Windows では、Ryzen AI Halo は *デフォルトで SSH サーバーが無効* な状態で出荷されます。Linux では、*デフォルトで SSH サーバーが有効* になっています。

1. Ryzen AI Halo 上で **AMD Ryzen™ AI Developer Center** を開きます。
2. **Remote** タブに移動します。
3. **SSH Server** をオンに切り替えます。
4. **Server Information** に表示されている **IP Address**、**Port**、**Username** をメモしておきます — これらを AMD Sync に入力します。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **注記:** これは Windows 向けの AMD Developer Center です。Linux 版は UI が異なる場合がありますが、同様のリモート機能を備えています。

> **ヒント:** AMD Sync が要求するのは、そのユーザーの **OS ログインパスワード** であり、Developer Center のパスワードではありません。

---

## ステップ 2 — クライアントに AMD Sync をインストールする

AMD Sync は Windows 11 および Linux 上で動作します。お使いの OS 用のインストーラをダウンロードし、以下の手順に従ってください。インストール後、**Get Started** 画面で **Accept & Install** をクリックします — 完了すると AMD Sync が自動的に起動します。

### Windows

[AMDSyncInstaller.exe をダウンロード](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. `AMDSyncInstaller.exe` をダブルクリックします。
2. **Accept & Install** をクリックします。

> Windows ファイアウォールの確認が表示された場合は、AMD Sync が Ryzen AI Halo に SSH 経由でアクセスできるよう、ネットワークアクセスを許可してください。

### Linux

お好みの形式のリンクをクリックしてダウンロードしてください。

| 形式 | ダウンロード | インストールコマンド |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **注記:** Ubuntu App Center は、ローカルで開かれた `.deb` を *「Potentially unsafe（安全でない可能性があります）」* として警告する場合があります。これはサードパーティ製のローカルインストーラ全般に表示される標準的な警告です。`.deb` のダブルクリックが失敗する場合は、上記のターミナルコマンドを使用してください。

---

## ステップ 3 — Ryzen AI Halo に接続する

初回起動時、AMD Sync には **Add a Remote Device** フォームが表示されます。Developer Center の **Remote** タブに表示された値を使って入力してください。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| フィールド | 注記 |
|-------|-------|
| **Device Name**（任意） | `Ryzen AI Halo` のようなわかりやすいラベル。デフォルトは `Device 1`、`Device 2`、…となります |
| **Hostname or IP** | Remote タブから取得 |
| **SSH Port** | Remote タブから取得(数字のみ) |
| **Username** | Ryzen AI Halo 上の OS アカウント名 |
| **Password** | OS ログインパスワード — 入力時はマスクされます |

**Add Device** をクリックします。短い読み込み画面の後、**「Connection Successful」** と表示され、システムトレイに常駐するホーム画面に移動します。ウィンドウ外をクリックすると非表示になりますが、AMD Sync はバックグラウンドで動作し続け、いつでもワンクリックでアクセスできます。

> **接続に失敗した場合、** AMD Sync は入力値を保持したままフォームに戻ります。よくある原因は、Ryzen AI Halo 上で SSH が無効になっている、パスワードが間違っている、または 2 台のデバイスが異なるネットワーク上にある、といったものです。

---

## ステップ 4 — 最初のリモートツールを起動する

ホーム画面には、クライアントと Ryzen AI Halo がどの OS を実行していても利用できる、5 つのワンクリックコンポーネントが用意されています。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| コンポーネント | 機能 |
|-----------|--------------|
| **Directory** | VS Code、Terminal、JupyterLab が開く Ryzen AI Halo 上のフォルダを選択します。デフォルトは管理された `Documents/AMD_Sync` ワークスペースです。 |
| **VS Code** | 選択したフォルダへの SSH トンネルを使って、VS Code をローカルで開きます。 |
| **Terminal** | 選択したフォルダ内で、Ryzen AI Halo に SSH 接続されたローカルターミナルを開きます。 |
| **JupyterLab** | 選択したフォルダを対象として、Ryzen AI Halo に SSH 接続されたノートブックプロジェクトを起動します。 |
| **Live Metrics** | Ryzen AI Halo 上の GPU、メモリ、CPU 使用率をリアルタイムで表示します。 |

### VS Code を試す

最初の起動では、**VS Code** を試してみてください。以下の手順は Linux 向けですが、Windows での操作も同様です。

1. **Directory** はデフォルトの `~/Documents/AMD_Sync` のままにしておきます。
2. **VS Code** をクリックします。
3. AMD Sync は Ryzen AI Halo 上に `Documents/AMD_Sync/Project_1` を作成し、それにトンネル接続した状態でローカルに VS Code を開きます。

これで、お使いのローカルの VS Code 環境から、Ryzen AI Halo 上にあるファイルを編集していることになります。`helloworld.py` を作成し、`print("hello world")` を追加して、統合ターミナル(`` Ctrl + ` ``)を開き、実行してみましょう。

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

ステータスバーには **SSH: Linux** と表示されます — これは、コードがお使いのノート PC ではなく Ryzen AI Halo 上で実行されていることの証です。
### ターミナルを試す

**Terminal** をクリックすると、キーボードから手を離すことなく、SSH 経由で同じフォルダに直接入れます。

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Windows では、デフォルトのターミナルは **PowerShell** です。好みに応じて、Settings メニューから **Windows Command Prompt** に切り替えることができます。Linux では、AMD Sync はシステムのデフォルトターミナルを使用します。

---

## ディレクトリの仕組み

**Directory** ドロップダウンは、AMD Sync の中で最も重要なコントロールです。このドロップダウンが、起動する各ツールが Ryzen AI Halo 上のどこに配置されるかを決定します。

- **`~/Documents/AMD_Sync`（デフォルト）** — ここから VS Code や JupyterLab を起動すると、新しいプロジェクトフォルダが自動的に作成されます（VS Code の場合は `Project_1`、`Project_2`、…、JupyterLab の場合は `Notebook_Project_1`、`Notebook_Project_2`、…）。
- **既存のプロジェクトフォルダ** — `AMD_Sync` の直下にあるフォルダ（Ryzen AI Halo 上で手動作成したフォルダも含む）は、すべてドロップダウンに表示されます。前回使用したフォルダが次回のデフォルトになります。
- **カスタムパス** — 任意の絶対パスを入力すると、Ryzen AI Halo 上の他の場所にあるフォルダを開けます。AMD Sync はフォルダを*開く*だけで、`AMD_Sync` の外にフォルダを作成することはなく、カスタムパスはセッション間で保存されません。

カスタムパスが機能しない場合、AMD Sync はその理由を表示します（構文が不正、フォルダが存在しない、パスがファイルを指している、など）。

---

## Live Metrics と JupyterLab

- **Live Metrics** — GPU、メモリ、CPU の使用状況をリアルタイムで表示するダッシュボードです。リモートのトレーニング実行が実際にハードウェアを使用しているかを確認する最も速い方法です。
- **JupyterLab** — Ryzen AI Halo に SSH 接続された、完全なノートブックプロジェクトです。独自の統合ターミナルを備えており、UI を離れることなくノートブックセルとシェルコマンドを組み合わせて使用できます。

---

## Settings と複数デバイス

**Settings** メニューには 3 つのタブがあります。

| タブ | 内容 |
|-----|----------------|
| **Devices** | これまでに正常に接続できたすべての Ryzen AI Halo を一覧表示します。再接続、認証情報の編集、新しいデバイスの追加が行えます。 |
| **Information** | ドキュメントやフォーラムサポートへのリンクです。 |
| **Customize** | デスクトップ上でのアプリの配置変更、ターミナル種類の切り替え（Windows のみ）、AMD Sync の更新確認が行えます。 |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **ターミナルの種類（Windows）** — **PowerShell**（デフォルト）と **Windows Command Prompt** のどちらかを選択できます。
- **ターミナルの種類（Linux）** — デフォルトのシステムターミナルのみ利用可能です。
- **アプリの更新** — このタブから、UI 内で直接 AMD Sync の新しいバージョンを確認・インストールできます。別途アップデーターは必要ありません。

> デバイスは、初回接続に成功した後にのみ **Devices** に表示されるため、失敗した接続試行によってリストが煩雑になることはありません。

---

## トラブルシューティング

- **接続がすぐに失敗する** — Developer Center の **Remote** タブで、Ryzen AI Halo 上の SSH サーバーが有効になっていることを確認してください。
- **パスワードが違うというエラー** — Developer Center から取得したパスワードではなく、Ryzen AI Halo 上の **OS ログインパスワード** を使用してください。
- **VS Code ボタンを押しても何も起こらない** — クライアントマシンに [code.visualstudio.com](https://code.visualstudio.com) から VS Code をインストールしてください。
- **AMD Sync のトレイアイコンが表示されない（Linux/GNOME）** — AppIndicator 拡張機能をインストールして有効にしてください。
- **ファイルマネージャーから `.deb` が開かない** — ターミナルから `sudo apt install ./AMDSyncInstaller.deb` を使用してください。
- **セットアップが起動のたびに再表示される（Linux）**: ログインキーリングのロックを解除するか、`--password-store=gnome-libsecret` を付けて起動した後、セットアップを一度やり直してください。

---