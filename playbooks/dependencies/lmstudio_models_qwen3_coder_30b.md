<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Downloading Qwen3-Coder 30B on LM Studio

To download the Qwen3-Coder 30B model:

1. Press "Ctrl" + "Shift" + "M" on your keyboard or click on the "Discover" tab (Magnifying Glass icon) on the left sidebar
2. Search for `Qwen3-Coder-30B-A3B`
3. Select a quantization (the recommended `Q4_K_M` is a good balance of size and quality) and click Download

LM Studio will automatically download and place the model in the correct directory.

Should you wish to download additional models, you can search for them in the Discover tab and LM Studio will handle the rest.

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
