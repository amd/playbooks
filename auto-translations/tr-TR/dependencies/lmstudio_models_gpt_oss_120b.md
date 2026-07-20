<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio Üzerinde GPT-OSS 120B İndirme

GPT-OSS 120B modelini indirmek için:

1. Klavyenizde "Ctrl" + "Shift" + "M" tuşlarına basın veya sol kenar çubuğundaki "Discover" sekmesine (Büyüteç simgesi) tıklayın
2. `ggml-org/gpt-oss-120b-GGUF` araması yapın
3. `mxfp4` seçeneğini seçin ve Download'a tıklayın

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio, modeli otomatik olarak indirip doğru dizine yerleştirecektir.

Ek modeller indirmek isterseniz, bunları Discover sekmesinde arayabilirsiniz; LM Studio gerisini halledecektir.

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