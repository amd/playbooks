<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Transferir o SDXL-Turbo para o Lemonade

O servidor Lemonade disponibiliza o modelo SDXL-Turbo (`SDXL-Turbo`). Para o transferir antecipadamente:

```bash
lemonade pull SDXL-Turbo
```

`lemonade run SDXL-Turbo` também transfere o modelo na primeira utilização, caso ainda não esteja presente, e depois carrega-o para inferência.

O modelo aparece na lista de modelos transferidos do servidor Lemonade assim que a transferência estiver concluída; as verificações abaixo confirmam que está presente na máquina.

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