<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio 可以從 **AMD Ryzen™ AI Developer Center** 安裝。前往 **Updates** 分頁，若尚未安裝 LM Studio 則進行安裝。

如果您的系統已預先安裝模型，請前往 Settings > General > Models Directory，然後將路徑更改為 `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. 從此處下載安裝程式：[https://lmstudio.ai/download](https://lmstudio.ai/download)
2. 進行安裝。
<!-- @device:end -->

> **模型：** 如果您的系統已預先安裝此操作手冊的模型，請將 LM Studio 指向上述預先安裝的模型目錄以使用該模型。否則，請在繼續之前從 LM Studio 的 **Discover** 分頁（搜尋圖示）下載模型。

> 提示：安裝完成後，請先啟動一次 LM Studio 以初始化 CLI（`lms`）。

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> 注意：您可以選擇安裝 .deb 或 AppImage。
1. 從此處下載 appimage：[https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. 執行 `sudo apt install libfuse2`
3. 執行 `cd ~/Downloads`
4. 執行 `chmod +x LM-Studio-*.AppImage`
5. 執行 `./LM-Studio-*.AppImage`
> 提示：安裝完成後，請先啟動一次 LM Studio 以初始化 CLI（`lms`）。

<!-- @device:halo_box -->
如果您的系統已預先安裝模型，請前往 Settings > General > Models Directory，然後將路徑更改為 `/var/cache/models`。

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_linux_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **模型：** 如果您的系統已預先安裝此操作手冊的模型，請將 LM Studio 指向上述預先安裝的模型目錄以使用該模型。否則，請在繼續之前從 LM Studio 的 **Discover** 分頁（搜尋圖示）下載模型。

<!-- @test:id=lmstudio-cli-linux timeout=60 hidden=True -->
```bash
lms --help
```
<!-- @test:end -->
<!-- @os:end -->