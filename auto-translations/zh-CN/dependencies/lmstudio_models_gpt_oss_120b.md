<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 在 LM Studio 上下载 GPT-OSS 120B

要下载 GPT-OSS 120B 模型：

1. 在键盘上按下 "Ctrl" + "Shift" + "M"，或点击左侧边栏的 "Discover" 选项卡（放大镜图标）
2. 搜索 `ggml-org/gpt-oss-120b-GGUF`
3. 选择 `mxfp4` 并点击 Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio 会自动下载模型并将其放置在正确的目录中。

如果您希望下载其他模型，可以在 Discover 选项卡中搜索它们，LM Studio 会处理剩余的工作。

<!-- @os:windows -->
<!-- @test:id=lmstudio-model-present-windows timeout=60 hidden=True -->
```powershell
lms ls --llm | Select-String -Pattern "gpt-oss-120b"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-model-present-linux timeout=60 hidden=True -->
```bash
lms ls --llm | grep -i "gpt-oss-120b"
```
<!-- @test:end -->
<!-- @os:end -->