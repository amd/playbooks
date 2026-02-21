### Downloading GPT-OSS 120B on LM Studio

To download the GPT-OSS 120B model:

1. Press "Ctrl" + "Shift" + "M" on your keyboard or click on the "Discover" tab (Magnifying Glass icon) on the left sidebar
2. Search for `ggml-org/gpt-oss-120b-GGUF`
3. Select `mxfp4` and click Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio will automatically download and place the model in the correct directory.

Should you wish to download additional models, you can search for them in the Discover tab and LM Studio will handle the rest.

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