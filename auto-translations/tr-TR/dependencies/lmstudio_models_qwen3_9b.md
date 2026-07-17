<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio'da Qwen3.5 9B İndirme

Qwen3.5 9B modelini indirmek için:

1. Klavyenizde "Ctrl" + "Shift" + "M" tuşlarına basın veya sol kenar çubuğundaki "Discover" sekmesine (Büyüteç simgesi) tıklayın
2. `Qwen3.5 9B` arayın
3. Bir kuantizasyon seçin (önerilen `Q4_K_M`, boyut ve kalite açısından iyi bir denge sunar) ve İndir'e tıklayın

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio, modeli otomatik olarak indirecek ve doğru dizine yerleştirecektir.

Ek modeller indirmek isterseniz, bunları Discover sekmesinde arayabilirsiniz; geri kalanını LM Studio halledecektir.

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