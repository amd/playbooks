<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Baixando o Qwen3.6 35B A3B para o Lemonade

O servidor Lemonade serve o modelo Qwen3.6 35B A3B (`Qwen3.6-35B-A3B-GGUF`). Para baixá-lo com antecedência:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

`lemonade run Qwen3.6-35B-A3B-GGUF` também baixa o modelo no primeiro uso, caso ainda não esteja presente, e em seguida o carrega para inferência.

O modelo aparece na lista de modelos baixados do servidor Lemonade assim que o download é concluído; as verificações abaixo confirmam que ele está presente na máquina.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-6-35b-a3b-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3.6-35B-A3B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-6-35b-a3b-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3.6-35B-A3B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->