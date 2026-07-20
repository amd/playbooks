<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
可以从 **AMD Ryzen™ AI Developer Center** 安装 LM Studio。前往 **Updates** 选项卡，如果尚未安装，请安装 LM Studio。

要让 LM Studio 能够识别预安装的模型，请导航到 Settings > General > Models Directory。然后将路径更改为 `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. 从此处下载安装程序：[https://lmstudio.ai/download](https://lmstudio.ai/download)
2. 安装。
<!-- @device:end -->

> 提示：安装完成后，请启动一次 LM Studio 以初始化 CLI（`lms`）。

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> 注意：您可以选择安装 .deb 或 AppImage。
1. 从此处下载 appimage：[https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. 运行 `sudo apt install libfuse2`  
3. 运行 `cd ~/Downloads`  
4. 运行 `chmod +x LM-Studio-*.AppImage`  
5. 运行 `./LM-Studio-*.AppImage`  
> 提示：安装完成后，请启动一次 LM Studio 以初始化 CLI（`lms`）。

<!-- @device:halo_box -->
要让 LM Studio 能够识别预安装的模型，请导航到 Settings > General > Models Directory。然后将路径更改为 `/var/cache/models`。

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