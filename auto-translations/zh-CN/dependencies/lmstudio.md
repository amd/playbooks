<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio 可从 **AMD Ryzen™ AI 开发者中心**安装。前往 **Updates** 标签页，如果尚未安装 LM Studio，请进行安装。

要使 LM Studio 能够识别预安装的模型，请导航至 Settings > General > Models Directory，然后将路径更改为 `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. 从此处下载安装程序：[https://lmstudio.ai/download](https://lmstudio.ai/download)
2. 进行安装。
<!-- @device:end -->

> 提示：安装完成后，启动一次 LM Studio 以初始化 CLI（`lms`）。

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> 注意：您可以选择安装 .deb 包或 AppImage。
1. 从此处下载 AppImage：[https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. 运行 `sudo apt install libfuse2`
3. 运行 `cd ~/Downloads`
4. 运行 `chmod +x LM-Studio-*.AppImage`
5. 运行 `./LM-Studio-*.AppImage`
> 提示：安装完成后，启动一次 LM Studio 以初始化 CLI（`lms`）。

<!-- @device:halo_box -->
要使 LM Studio 能够识别预安装的模型，请导航至 Settings > General > Models Directory，然后将路径更改为 `/var/cache/models`。

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