<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### A transferir o GPT-OSS 120B para o Lemonade

O servidor Lemonade disponibiliza o modelo GPT-OSS 120B MXFP4 GGUF (`gpt-oss-120b-mxfp-GGUF`). Para o transferir antecipadamente:

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

`lemonade run gpt-oss-120b-mxfp-GGUF` também transfere o modelo na primeira utilização, caso ainda não esteja presente, e carrega-o de seguida para inferência.

O modelo aparece na lista de modelos transferidos do servidor Lemonade assim que a transferência termina; as verificações abaixo confirmam que está presente na máquina.

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