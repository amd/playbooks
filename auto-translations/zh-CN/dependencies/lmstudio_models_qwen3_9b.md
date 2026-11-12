<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 在 LM Studio 上下载 Qwen3.5 9B

要下载 Qwen3.5 9B 模型：

1. 在键盘上按下 "Ctrl" + "Shift" + "M"，或点击左侧边栏的 "Discover" 选项卡（放大镜图标）
2. 搜索 `Qwen3.5 9B`
3. 选择一种量化方式（推荐使用 `Q4_K_M`，在体积与质量之间取得了良好的平衡），然后点击 Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio 将自动下载模型并将其放置到正确的目录中。

如果你希望下载更多模型，可以在 Discover 选项卡中搜索，LM Studio 会处理好其余工作。

<!-- @os:windows -->
<!-- @test:id=lmstudio-model-present-qwen-windows timeout=60 hidden=True -->
```powershell
lms ls --llm | Select-String -Pattern "qwen3.5-9b"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-model-present-qwen-linux timeout=60 hidden=True -->
```bash
lms ls --llm | grep -i "qwen3.5-9b"
```
<!-- @test:end -->
<!-- @os:end -->