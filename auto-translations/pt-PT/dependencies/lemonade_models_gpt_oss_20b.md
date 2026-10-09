<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Transferir o GPT-OSS 20B para o Lemonade

O servidor Lemonade disponibiliza o modelo GPT-OSS 20B MXFP4 GGUF (`gpt-oss-20b-mxfp4-GGUF`). Para o transferir antecipadamente:

```bash
lemonade pull gpt-oss-20b-mxfp4-GGUF
```

`lemonade run gpt-oss-20b-mxfp4-GGUF` também transfere o modelo na primeira utilização, caso ainda não esteja presente, e depois carrega-o para inferência.

O modelo aparece na lista de modelos transferidos do servidor Lemonade assim que a transferência estiver concluída; as verificações abaixo confirmam que está presente na máquina.

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