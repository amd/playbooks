<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade için Qwen3 4B Hybrid'in İndirilmesi

Lemonade sunucusu, Ryzen AI işlemcilerin NPU ve GPU üzerinde çalışan Qwen3 4B Hybrid modelini (`Qwen3-4B-Hybrid`) sunar. Önceden indirmek için:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

Çekme işlemi tamamlandığında model, Lemonade sunucusunun indirilen model listesinde görünür; aşağıdaki kontrol, modelin makinede mevcut olduğunu doğrular.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->