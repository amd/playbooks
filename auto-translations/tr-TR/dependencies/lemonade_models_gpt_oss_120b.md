<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade için GPT-OSS 120B İndirme

Lemonade sunucusu, GPT-OSS 120B MXFP4 GGUF modelini (`gpt-oss-120b-mxfp-GGUF`) sunar. Önceden indirmek için:

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

`lemonade run gpt-oss-120b-mxfp-GGUF` komutu, model henüz mevcut değilse ilk kullanımda da modeli indirir ve ardından çıkarım için yükler.

İndirme işlemi tamamlandığında model, Lemonade sunucusunun indirilen model listesinde görünür; aşağıdaki kontroller, modelin makinede mevcut olduğunu doğrular.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gpt-oss-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:gpt-oss-120b-mxfp-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gpt-oss-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q gpt-oss-120b-mxfp-GGUF
```
<!-- @test:end -->
<!-- @os:end -->