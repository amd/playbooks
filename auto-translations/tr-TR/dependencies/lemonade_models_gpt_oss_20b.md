<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade için GPT-OSS 20B İndirme

Lemonade sunucusu, GPT-OSS 20B MXFP4 GGUF modelini (`gpt-oss-20b-mxfp4-GGUF`) sunar. Önceden indirmek için:

```bash
lemonade pull gpt-oss-20b-mxfp4-GGUF
```

`lemonade run gpt-oss-20b-mxfp4-GGUF` komutu, model henüz mevcut değilse ilk kullanımda da modeli indirir ve ardından çıkarım için yükler.

Model, indirme işlemi tamamlandığında Lemonade sunucusunun indirilen model listesinde görünür; aşağıdaki kontroller, modelin makinede mevcut olduğunu doğrular.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->