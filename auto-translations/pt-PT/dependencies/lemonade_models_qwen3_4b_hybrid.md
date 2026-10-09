<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Transferir o Qwen3 4B Hybrid para o Lemonade

O servidor Lemonade disponibiliza o modelo Qwen3 4B Hybrid (`Qwen3-4B-Hybrid`), que é executado no NPU e na GPU dos processadores Ryzen AI. Para o transferir antecipadamente:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

O modelo aparece na lista de modelos transferidos do servidor Lemonade assim que a transferência for concluída; a verificação abaixo confirma que está presente na máquina.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->