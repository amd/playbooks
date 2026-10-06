<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Download di GPT-OSS 120B per Lemonade

Il server Lemonade serve il modello GPT-OSS 120B MXFP4 GGUF (`gpt-oss-120b-mxfp-GGUF`). Per scaricarlo in anticipo:

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

`lemonade run gpt-oss-120b-mxfp-GGUF` scarica inoltre il modello al primo utilizzo se non è già presente, quindi lo carica per l'inferenza.

Il modello compare nell'elenco dei modelli scaricati del server Lemonade una volta completato il download; i controlli seguenti confermano che sia presente sulla macchina.

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