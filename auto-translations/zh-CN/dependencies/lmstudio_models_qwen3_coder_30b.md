<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 在 LM Studio 中下载 Qwen3-Coder 30B

下载 Qwen3-Coder 30B 模型的步骤如下：

1. 在键盘上按 "Ctrl" + "Shift" + "M"，或点击左侧边栏中的 "Discover" 选项卡（放大镜图标）
2. 搜索 `Qwen3-Coder-30B-A3B`
3. 选择一种量化方式（推荐使用 `Q4_K_M`，在大小和质量之间取得了良好的平衡），然后点击 Download

LM Studio 会自动下载模型并将其放置在正确的目录中。

如果您想下载其他模型，可以在 Discover 选项卡中搜索，LM Studio 会处理其余的工作。

<!-- @os:windows -->
<!-- @test:id=lmstudio-model-present-qwen3-coder-windows timeout=60 hidden=True -->
```powershell
lms ls --llm | Select-String -Pattern "qwen3-coder-30b"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-model-present-qwen3-coder-linux timeout=60 hidden=True -->
```bash
lms ls --llm | grep -i "qwen3-coder-30b"
```
<!-- @test:end -->
<!-- @os:end -->