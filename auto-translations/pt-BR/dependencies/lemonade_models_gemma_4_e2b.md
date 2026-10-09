<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Baixando o Gemma-4 E2B para o Lemonade

O servidor Lemonade disponibiliza o modelo Gemma-4 E2B (`Gemma-4-E2B-it-GGUF`). Para baixá-lo com antecedência:

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

`lemonade run Gemma-4-E2B-it-GGUF` também baixa o modelo no primeiro uso, caso ainda não esteja presente, e em seguida o carrega para inferência.

O modelo aparece na lista de modelos baixados do servidor Lemonade assim que o download for concluído; as verificações abaixo confirmam que ele está presente na máquina.

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