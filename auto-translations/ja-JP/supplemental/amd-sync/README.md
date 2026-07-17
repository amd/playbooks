<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# AMD Sync によるリモート開発

## 概要

**AMD Sync** は、あなたのノートパソコンを AMD Ryzen™ AI Halo のリモートコックピットに変えます。手動での SSH、鍵、IDE のセットアップは不要です — AMD Sync をインストールするだけで、Ryzen AI Halo 上のリモートターミナル、VS Code、JupyterLab、そしてリアルタイムの GPU/CPU/メモリダッシュボードにワンクリックでアクセスできます。

ローカルマシンはそのままの使い慣れた環境を維持しながら、すべてのコマンド、ノートブック、モデルは Ryzen AI Halo 上で実行されます。

> **ヒント**: このページには AMDSync の最新アップデート情報が随時掲載されます。

## 学習内容

- Ryzen AI Halo で SSH を有効にし、AMD Sync から接続する
- ワンクリックで VS Code、ターミナル、JupyterLab、ライブメトリクスを Ryzen AI Halo に対して起動する
- AMD Sync の管理プロジェクトフォルダを使用してリモート作業を整理する

---

## 基本概念

AMD Sync には2つの側面があります：**クライアント**（AMD Sync アプリを実行するあなたのノートパソコン）と**サーバー**（AMD Sync がトンネル接続する SSH サーバーを実行する Ryzen AI Halo）です。AMD Sync から起動するすべてのもの — VS Code、ターミナル、ノートブック — はローカルで開きますが、Ryzen AI Halo 上で実行されます。

> **サポートされるクライアント:** Windows 11 および Linux。macOS はサポートされていません。

---

## ステップ 1 — Ryzen AI Halo で SSH を有効にする


> **注意:** Windows では、Ryzen AI Halo は SSH サーバーが*デフォルトでオフ*の状態で出荷されます。Linux では、SSH サーバーが*デフォルトでオン*の状態で提供されます。

1. Ryzen AI Halo で **AMD Ryzen™ AI Developer Center** を開きます。
2. **Remote** タブに移動します。
3. **SSH Server** をオンに切り替えます。
4. **Server Information** の下に表示される **IP Address**、**Port**、**Username** をメモしておきます — AMD Sync に貼り付けて使用します。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **注意:** これは Windows 用の AMD Developer Center です。Linux 版は UI が異なる場合がありますが、同様のリモート機能を備えています。

> **ヒント:** AMD Sync は Developer Center のパスワードではなく、そのユーザーの **OS ログインパスワード** を要求します。

---

## ステップ 2 — クライアントに AMD Sync をインストールする

AMD Sync は Windows 11 および Linux で動作します。お使いの OS 用のインストーラーをダウンロードし、以下の手順に従ってください。インストール後、**Get Started** 画面で **Accept & Install** をクリックすると — AMD Sync は完了後に自動的に起動します。

### Windows

[AMDSyncInstaller.exe をダウンロード](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. `AMDSyncInstaller.exe` をダブルクリックします。
2. **Accept & Install** をクリックします。

> Windows ファイアウォールのプロンプトが表示された場合は、AMD Sync が SSH 経由で Ryzen AI Halo に接続できるようにネットワークアクセスを許可してください。

### Linux

リンクをクリックして希望のフォーマットをダウンロードしてください：

| フォーマット | ダウンロード | インストールコマンド |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **注意:** Ubuntu App Center は、ローカルで開いた `.deb` ファイルを *「潜在的に安全でない」* としてフラグを立てる場合があります。これはサードパーティのローカルインストーラーに対する標準的な警告です。`.deb` のダブルクリックが失敗する場合は、上記のターミナルコマンドを使用してください。

---

## ステップ 3 — Ryzen AI Halo に接続する

初回起動時、AMD Sync は **Add a Remote Device** フォームを表示します。Developer Center の **Remote** タブに表示された値を使用して入力してください。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| フィールド | 説明 |
|-------|-------|
| **Device Name** *（任意）* | `Ryzen AI Halo` のようなわかりやすいラベル。デフォルトは `Device 1`、`Device 2`、… |
| **Hostname or IP** | Remote タブから取得 |
| **SSH Port** | Remote タブから取得（数字のみ） |
| **Username** | Ryzen AI Halo 上の OS アカウント名 |
| **Password** | OS ログインパスワード — 入力中はマスクされます |

**Add Device** をクリックします。短いローディング画面の後、**「Connection Successful」** と表示され、システムトレイに常駐するホームビューに移動します。ウィンドウ外をクリックして閉じても、AMD Sync はバックグラウンドで実行され続け、ワンクリックでアクセスできます。

> **接続に失敗した場合、** AMD Sync は入力値を保持したままフォームに戻ります。よくある原因は、Ryzen AI Halo で SSH が無効になっている、パスワードが間違っている、または2つのデバイスが異なるネットワーク上にあることです。

---

## ステップ 4 — 最初のリモートツールを起動する

ホームビューには5つのワンクリックコンポーネントがあります — クライアントと Ryzen AI Halo がどの OS を実行していても、すべて利用可能です。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| コンポーネント | 機能 |
|-----------|--------------|
| **Directory** | VS Code、ターミナル、JupyterLab が開く Ryzen AI Halo 上のフォルダを選択します。デフォルトは管理された `Documents/AMD_Sync` ワークスペースです。 |
| **VS Code** | 選択したフォルダへの SSH トンネルを使用して、ローカルで VS Code を開きます。 |
| **Terminal** | 選択したフォルダ内で Ryzen AI Halo に SSH 接続されたローカルターミナルを開きます。 |
| **JupyterLab** | 選択したフォルダを対象に、Ryzen AI Halo に SSH 接続されたノートブックプロジェクトを起動します。 |
| **Live Metrics** | Ryzen AI Halo の GPU、メモリ、CPU 使用率のリアルタイムビュー。 |

### VS Code を試す

最初の起動では、**VS Code** を試してみましょう。

1. **Directory** をデフォルトの `~/Documents/AMD_Sync` のままにします。
2. **VS Code** をクリックします。
3. AMD Sync は Ryzen AI Halo 上に `Documents/AMD_Sync/Project_1` を作成し、ローカルの VS Code をトンネル接続して開きます。

これで、ローカルの VS Code 環境を使いながら Ryzen AI Halo 上に存在するファイルを編集できます。`helloworld.py` を作成し、`print("hello world")` を追加して、統合ターミナル（`` Ctrl + ` ``）を開いて実行します：

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

ステータスバーに **SSH: Linux** と表示されます — コードがノートパソコンではなく Ryzen AI Halo 上で実行されている証拠です。

### ターミナルを試す

**Terminal** をクリックすると、キーボードから離れることなく SSH 経由で同じフォルダに直接アクセスできます。

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Windows では、デフォルトのターミナルは **PowerShell** です — 好みに応じて設定メニューから **Windows Command Prompt** に切り替えることができます。Linux では、AMD Sync はシステムのデフォルトターミナルを使用します。

---

## Directory の仕組み

**Directory** ドロップダウンは AMD Sync で最も重要なコントロールです — 起動するすべてのツールが Ryzen AI Halo 上のどこに配置されるかを決定します。

- **`~/Documents/AMD_Sync`（デフォルト）** — ここから VS Code または JupyterLab を起動すると、新しいプロジェクトフォルダが自動的に作成されます（VS Code の場合は `Project_1`、`Project_2`、…、JupyterLab の場合は `Notebook_Project_1`、`Notebook_Project_2`、…）。
- **既存のプロジェクトフォルダ** — `AMD_Sync` の直下にある子フォルダ（Ryzen AI Halo 上で手動作成したフォルダを含む）がドロップダウンに表示されます。最後に使用したフォルダが次回のデフォルトになります。
- **カスタムパス** — 任意の絶対パスを入力して Ryzen AI Halo 上の別の場所にあるフォルダを開くことができます。AMD Sync はそのフォルダを*開く*だけです — `AMD_Sync` の外にフォルダを作成することはなく、カスタムパスはセッション間で保存されません。

カスタムパスが機能しない場合、AMD Sync はその理由を通知します：無効な構文、フォルダが存在しない、またはパスがファイルを指しているなどです。

---

## Live Metrics と JupyterLab

- **Live Metrics** — GPU、メモリ、CPU 使用率のライブダッシュボード。リモートのトレーニング実行が実際にハードウェアに負荷をかけていることを確認する最も手軽な方法です。
- **JupyterLab** — Ryzen AI Halo に SSH 接続されたフル機能のノートブックプロジェクト。UI を離れることなくノートブックセルとシェルコマンドを組み合わせられる統合ターミナルを備えています。

---

## 設定と複数デバイス

**Settings** メニューには3つのタブがあります：

| タブ | 内容 |
|-----|----------------|
| **Devices** | 接続に成功したすべての Ryzen AI Halo の一覧。再接続、認証情報の編集、または新しいデバイスの追加が可能です。 |
| **Information** | ドキュメントおよびフォーラムサポートへのリンク。 |
| **Customize** | デスクトップ上のアプリの位置変更、ターミナルタイプの切り替え（Windows のみ）、AMD Sync のアップデート確認。 |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **ターミナルタイプ（Windows）** — **PowerShell**（デフォルト）と **Windows Command Prompt** を選択できます。
- **ターミナルタイプ（Linux）** — デフォルトのシステムターミナルのみ利用可能です。
- **アプリのアップデート** — このタブは UI 内から新しい AMD Sync バージョンを確認してインストールするための場所です。別途アップデーターは必要ありません。

> デバイスは最初の接続が成功した後にのみ **Devices** に表示されるため、失敗した試みでリストが煩雑になることはありません。

---

## トラブルシューティング

- **接続がすぐに失敗する** — Developer Center の **Remote** タブで Ryzen AI Halo の SSH サーバーが有効になっていることを確認してください。
- **パスワードエラー** — Developer Center のパスワードではなく、Ryzen AI Halo の **OS ログインパスワード** を使用してください。
- **VS Code ボタンが反応しない** — [code.visualstudio.com](https://code.visualstudio.com) からクライアントマシンに VS Code をインストールしてください。
- **AMD Sync のトレイアイコンが表示されない（Linux/GNOME）** — AppIndicator 拡張機能をインストールして有効にしてください。
- **`.deb` がファイルマネージャーから開けない** — ターミナルから `sudo apt install ./AMDSyncInstaller.deb` を使用してください。

---