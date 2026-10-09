<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade için SDXL-Turbo'nun İndirilmesi

Lemonade sunucusu SDXL-Turbo modelini (`SDXL-Turbo`) sunar. Önceden indirmek için:

```bash
lemonade pull SDXL-Turbo
```

`lemonade run SDXL-Turbo` komutu, model henüz mevcut değilse ilk kullanımda modeli de indirir, ardından çıkarım için yükler.

İndirme işlemi tamamlandığında model, Lemonade sunucusunun indirilen model listesinde görünür; aşağıdaki kontroller, modelin makinede mevcut olduğunu doğrular.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-sdxl-turbo-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:SDXL-Turbo
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-sdxl-turbo-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q SDXL-Turbo
```
<!-- @test:end -->
<!-- @os:end -->