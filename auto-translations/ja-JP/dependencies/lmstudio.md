<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studioは**AMD Ryzen™ AI Developer Center**からインストールできます。**Updates**タブに移動し、まだインストールされていない場合はLM Studioをインストールしてください。

お使いのシステムにモデルがプリインストールされている場合は、Settings > General > Models Directoryに移動してください。その後、パスを`C:\Users\Public\models`に変更します。

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. こちらからインストーラーをダウンロードします：[https://lmstudio.ai/download](https://lmstudio.ai/download)
2. インストールします。
<!-- @device:end -->

> **モデル：** お使いのシステムにこのプレイブックのモデルがプリインストールされている場合は、LM Studioを上記のプリインストール済みモデルディレクトリに向けて使用してください。そうでない場合は、続行する前にLM Studioの**Discover**タブ（検索アイコン）からモデルをダウンロードしてください。

> ヒント：インストール後、一度LM Studioを起動してCLI（`lms`）を初期化してください。

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> 注：.debまたはAppImageのどちらをインストールするか選択できます。
1. こちらからAppImageをダウンロードします：[https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. `sudo apt install libfuse2`を実行します
3. `cd ~/Downloads`を実行します
4. `chmod +x LM-Studio-*.AppImage`を実行します
5. `./LM-Studio-*.AppImage`を実行します
> ヒント：インストール後、一度LM Studioを起動してCLI（`lms`）を初期化してください。

<!-- @device:halo_box -->
お使いのシステムにモデルがプリインストールされている場合は、Settings > General > Models Directoryに移動してください。その後、パスを`/var/cache/models`に変更します。

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_linux_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **モデル：** お使いのシステムにこのプレイブックのモデルがプリインストールされている場合は、LM Studioを上記のプリインストール済みモデルディレクトリに向けて使用してください。そうでない場合は、続行する前にLM Studioの**Discover**タブ（検索アイコン）からモデルをダウンロードしてください。

<!-- @test:id=lmstudio-cli-linux timeout=60 hidden=True -->
```bash
lms --help
```
<!-- @test:end --> 
<!-- @os:end -->