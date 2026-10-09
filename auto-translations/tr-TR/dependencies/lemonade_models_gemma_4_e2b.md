<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade için Gemma-4 E2B İndirme

Lemonade sunucusu, Gemma-4 E2B modelini (`Gemma-4-E2B-it-GGUF`) sunar. Önceden indirmek için:

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

`lemonade run Gemma-4-E2B-it-GGUF` komutu, model henüz mevcut değilse ilk kullanımda da modeli indirir ve ardından çıkarım için yükler.

Model, indirme işlemi tamamlandıktan sonra Lemonade sunucusunun indirilen model listesinde görünür; aşağıdaki kontroller modelin makinede mevcut olduğunu doğrular.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gemma-4-e2b-it-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Gemma-4-E2B-it-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gemma-4-e2b-it-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Gemma-4-E2B-it-GGUF
```
<!-- @test:end -->
<!-- @os:end -->