<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio は **AMD Ryzen™ AI Developer Center** からインストールできます。**Updates** タブに移動し、LM Studio がまだインストールされていない場合はインストールしてください。

プリインストール済みモデルを LM Studio から参照できるようにするには、Settings > General > Models Directory に移動し、パスを `C:\Users\Public\models` に変更してください。

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. こちらからインストーラーをダウンロードしてください: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. インストールしてください。
<!-- @device:end -->

> ヒント: インストール後、LM Studio を一度起動して CLI (`lms`) を初期化してください。

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> 注意: .deb または AppImage のいずれかを選択してインストールできます。
1. こちらから AppImage をダウンロードしてください: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. `sudo apt install libfuse2` を実行してください。
3. `cd ~/Downloads` を実行してください。
4. `chmod +x LM-Studio-*.AppImage` を実行してください。
5. `./LM-Studio-*.AppImage` を実行してください。
> ヒント: インストール後、LM Studio を一度起動して CLI (`lms`) を初期化してください。

<!-- @device:halo_box -->
プリインストール済みモデルを LM Studio から参照できるようにするには、Settings > General > Models Directory に移動し、パスを `/var/cache/models` に変更してください。

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_linux_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @test:id=lmstudio-cli-linux timeout=60 hidden=True -->
```bash
lms --help
```
<!-- @test:end --> 
<!-- @os:end -->