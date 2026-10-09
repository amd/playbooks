<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade için Qwen3.6 35B A3B İndirme

Lemonade sunucusu Qwen3.6 35B A3B modelini (`Qwen3.6-35B-A3B-GGUF`) sunar. Önceden indirmek için:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

`lemonade run Qwen3.6-35B-A3B-GGUF` komutu, model henüz mevcut değilse ilk kullanımda da modeli indirir, ardından çıkarım için yükler.

Model, indirme tamamlandığında Lemonade sunucusunun indirilen model listesinde görünür; aşağıdaki kontroller modelin makinede mevcut olduğunu doğrular.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-6-35b-a3b-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3.6-35B-A3B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-6-35b-a3b-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3.6-35B-A3B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->