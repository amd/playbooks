<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio'da Qwen3-Coder 30B İndirme

Qwen3-Coder 30B modelini indirmek için:

1. Klavyenizde "Ctrl" + "Shift" + "M" tuşlarına basın veya sol kenar çubuğundaki "Discover" sekmesine (Büyüteç simgesi) tıklayın
2. `Qwen3-Coder-30B-A3B` araması yapın
3. Bir kuantizasyon seçin (önerilen `Q4_K_M`, boyut ve kalite arasında iyi bir denge sağlar) ve Download'a tıklayın

LM Studio, modeli otomatik olarak indirip doğru dizine yerleştirecektir.

Ek modeller indirmek isterseniz, bunları Discover sekmesinde arayabilirsiniz ve LM Studio gerisini halleder.

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