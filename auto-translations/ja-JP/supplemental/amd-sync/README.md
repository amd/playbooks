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

**AMD Sync** は、お使いのノートPCを AMD Ryzen™ AI Halo のリモートコックピットに変えます。手動での SSH、鍵、IDE のセットアップは不要です — AMD Sync をインストールするだけで、リモートターミナル、VS Code、JupyterLab、そして Ryzen AI Halo のライブ GPU/CPU/メモリダッシュボードへワンクリックでアクセスできます。

お使いのローカルマシンはそのままの操作感を維持しつつ、すべてのコマンド、ノートブック、モデルは Ryzen AI Halo 上で実行されます。

> **ヒント**: このページには AMDSync に関する最新の更新情報が記載されます。 

## このページで学べること

- Ryzen AI Halo で SSH を有効化し、AMD Sync から接続する方法
- Ryzen AI Halo に対して VS Code、ターミナル、JupyterLab、Live Metrics をワンクリックで起動する方法
- AMD Sync の管理対象プロジェクトフォルダを使ってリモート作業を整理する方法

---

## コアコンセプト

AMD Sync には2つの側面があります。**クライアント**（AMD Sync アプリを実行するお使いのノートPC）と、**サーバー**（AMD Sync がトンネル接続する SSH サーバーを実行する Ryzen AI Halo）です。AMD Sync から起動するもの — VS Code、ターミナル、ノートブック — はすべてローカルで開かれますが、実行は Ryzen AI Halo 上で行われます。

> **対応クライアント:** Windows 11 および Linux。macOS には対応していません。

---

## ステップ1 — Ryzen AI Halo で SSH を有効化する


> **注記:** Windows では、Ryzen AI Halo は SSH サーバーが*デフォルトで無効*の状態で出荷されます。Linux では、SSH サーバーが*デフォルトで有効*になっています。

1. Ryzen AI Halo で **AMD Ryzen™ AI Developer Center** を開きます。
2. **Remote** タブに移動します。
3. **SSH Server** をオンに切り替えます。
4. **Server Information** に表示されている **IP Address**、**Port**、**Username** をメモしておきます — これらを AMD Sync に貼り付けます。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **注記:** これは Windows 版 AMD Developer Center です。Linux 版は UI が異なる場合がありますが、同様のリモート機能を提供します。

> **ヒント:** AMD Sync が要求するのは、そのユーザーの **OS ログインパスワード** であり、Developer Center のパスワードではありません。

---

## ステップ2 — クライアント側に AMD Sync をインストールする

AMD Sync は Windows 11 および Linux で動作します。お使いの OS 用のインストーラーをダウンロードし、以下の手順に従ってください。インストール後、**Get Started** 画面で **Accept & Install** をクリックすると、AMD Sync が完了時に自動的に起動します。

### Windows

[AMDSyncInstaller.exe をダウンロード](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. `AMDSyncInstaller.exe` をダブルクリックします。
2. **Accept & Install** をクリックします。

> Windows ファイアウォールからプロンプトが表示された場合は、AMD Sync のネットワークアクセスを許可して、Ryzen AI Halo に SSH 経由で到達できるようにしてください。

### Linux

お好みの形式のリンクをクリックしてダウンロードしてください。

| 形式 | ダウンロード | インストールコマンド |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **注記:** Ubuntu App Center は、ローカルで開かれた `.deb` を*「潜在的に安全でない」*とフラグ表示することがあります。これはサードパーティのローカルインストーラー全般に対する標準的な警告です。`.deb` をダブルクリックしても失敗する場合は、上記のターミナルコマンドを使用してください。

---

## ステップ3 — Ryzen AI Halo に接続する

初回起動時、AMD Sync は **Add a Remote Device** フォームを表示します。Developer Center の **Remote** タブにある値を使って入力してください。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| フィールド | 補足 |
|-------|-------|
| **Device Name**（任意） | `Ryzen AI Halo` のようなわかりやすいラベル。デフォルトは `Device 1`、`Device 2`、… となります。 |
| **Hostname or IP** | Remote タブから取得 |
| **SSH Port** | Remote タブから取得（数字のみ） |
| **Username** | Ryzen AI Halo 上のお使いの OS アカウント名 |
| **Password** | お使いの OS ログインパスワード — 入力時にマスクされます |

**Add Device** をクリックします。短いロード画面の後、**「Connection Successful」** と表示され、システムトレイに常駐するホーム画面に移動します。ウィンドウの外側をクリックすると閉じますが、AMD Sync はバックグラウンドで動作し続け、ワンクリックですぐに呼び出せます。

> **接続に失敗した場合、** AMD Sync は入力した値を保持したままフォームに戻ります。よくある原因は、Ryzen AI Halo で SSH が無効になっている、パスワードが間違っている、または2台のデバイスが異なるネットワークに接続されていることです。

---

## ステップ4 — 最初のリモートツールを起動する

ホーム画面には、5つのワンクリックコンポーネントが用意されています — クライアントと Ryzen AI Halo がどの OS で動作していても、すべて利用可能です。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| コンポーネント | 内容 |
|-----------|--------------|
| **Directory** | VS Code、ターミナル、JupyterLab が開く Ryzen AI Halo 上のフォルダを選択します。デフォルトは管理対象の `Documents/AMD_Sync` ワークスペースです。 |
| **VS Code** | 選択したフォルダへの SSH トンネルを使って、ローカルで VS Code を開きます。 |
| **Terminal** | 選択したフォルダ内で、Ryzen AI Halo に SSH 接続されたローカルターミナルを開きます。 |
| **JupyterLab** | 選択したフォルダに範囲を限定して、Ryzen AI Halo に SSH 接続されたノートブックプロジェクトを起動します。 |
| **Live Metrics** | Ryzen AI Halo の GPU、メモリ、CPU 使用率のリアルタイムビューです。 |

### VS Code を試す

初回起動では、**VS Code** を試してみてください。

1. **Directory** はデフォルトの `~/Documents/AMD_Sync` のままにしておきます。
2. **VS Code** をクリックします。
3. AMD Sync は Ryzen AI Halo 上に `Documents/AMD_Sync/Project_1` を作成し、そこにトンネル接続された VS Code をローカルで開きます。

これで、お使いのローカルの VS Code 環境から、Ryzen AI Halo 上にあるファイルを編集していることになります。`helloworld.py` を作成し、`print("hello world")` を追加して、統合ターミナル（`` Ctrl + ` ``）を開き、実行してみましょう。

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

ステータスバーには **SSH: Linux** と表示されます — これは、お使いのコードがノートPCではなく Ryzen AI Halo 上で実行されている証拠です。
### ターミナルを試す

**Terminal** をクリックすると、キーボードから手を離すことなく、SSH経由で同じフォルダに直接アクセスできます。

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Windowsでは、デフォルトのターミナルは**PowerShell**です。好みに応じて、設定メニューから**Windows Command Prompt**に切り替えることもできます。Linuxでは、AMD Syncはシステムのデフォルトターミナルを使用します。

---

## Directoryの仕組み

**Directory** ドロップダウンは、AMD Sync内で最も重要な設定項目です。ここで、起動する各ツールがRyzen AI Halo上のどこに配置されるかが決まります。

- **`~/Documents/AMD_Sync`（デフォルト）** — ここからVS CodeまたはJupyterLabを起動すると、自動的に新しいプロジェクトフォルダが作成されます（VS Codeの場合は`Project_1`、`Project_2`、…、JupyterLabの場合は`Notebook_Project_1`、`Notebook_Project_2`、…）。
- **既存のプロジェクトフォルダ** — `AMD_Sync`の直下にあるフォルダ（Ryzen AI Halo上で手動作成したフォルダを含む）は、すべてドロップダウンに表示されます。最後に使用したフォルダが次回のデフォルトになります。
- **カスタムパス** — 絶対パスを入力すると、Ryzen AI Halo上の別の場所にあるフォルダを開くことができます。AMD Syncはそのフォルダを*開く*だけで、`AMD_Sync`の外にフォルダを作成することはありません。また、カスタムパスはセッション間で保存されません。

カスタムパスが機能しない場合、AMD Syncはその理由（構文が無効、フォルダが存在しない、パスがファイルを指しているなど）を表示します。

---

## ライブメトリクスとJupyterLab

- **Live Metrics** — GPU、メモリ、CPU使用率のライブダッシュボードです。リモートのトレーニング実行が実際にハードウェアに負荷をかけているかを確認する最も速い方法です。
- **JupyterLab** — Ryzen AI HaloにSSH接続されたフルノートブックプロジェクトで、統合ターミナルを備えているため、UIから離れることなくノートブックセルとシェルコマンドを組み合わせて使用できます。

---

## Settingsと複数デバイス

**Settings** メニューには3つのタブがあります。

| タブ | 内容 |
|-----|----------------|
| **Devices** | これまで正常に接続できたすべてのRyzen AI Haloを一覧表示します。再接続、認証情報の編集、新しいデバイスの追加が行えます。 |
| **Information** | ドキュメントとフォーラムサポートへのリンクです。 |
| **Customize** | デスクトップ上でのアプリの位置変更、ターミナル種別の切り替え（Windowsのみ）、AMD Syncのアップデート確認を行います。 |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **ターミナル種別（Windows）** — **PowerShell**（デフォルト）と**Windows Command Prompt**のどちらかを選択できます。
- **ターミナル種別（Linux）** — デフォルトのシステムターミナルのみ利用可能です。
- **アプリのアップデート** — このタブは、UI内から新しいAMD Syncバージョンを確認・インストールするための場所です。別途アップデーターを用意する必要はありません。

> デバイスは、初回接続に成功した後にのみ**Devices**に表示されるため、失敗した接続試行によって一覧が煩雑になることはありません。

---

## トラブルシューティング

- **接続がすぐに失敗する** — Developer CenterのRyzen AI Haloの**Remote**タブで、SSHサーバーが有効になっていることを確認してください。
- **パスワードが違うというエラー** — Ryzen AI Haloでは、Developer Centerから取得したパスワードではなく、**OSログインパスワード**を使用してください。
- **VS Codeボタンを押しても何も起こらない** — クライアントマシンに[code.visualstudio.com](https://code.visualstudio.com)からVS Codeをインストールしてください。
- **AMD Syncのトレイアイコンが表示されない（Linux/GNOME）** — AppIndicator拡張機能をインストールして有効にしてください。
- **ファイルマネージャーから`.deb`が開けない** — ターミナルから`sudo apt install ./AMDSyncInstaller.deb`を実行してください。
- **起動のたびにセットアップ画面が再表示される（Linux）**：ログインキーリングのロックを解除するか、`--password-store=gnome-libsecret`を付けて起動し、その後セットアップを一度やり直してください。

---