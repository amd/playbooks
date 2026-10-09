<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Download di Qwen3-Coder 30B A3B per Lemonade

Il server Lemonade serve il modello Qwen3-Coder 30B A3B (`Qwen3-Coder-30B-A3B-Instruct-GGUF`). Per scaricarlo in anticipo:

```bash
lemonade pull Qwen3-Coder-30B-A3B-Instruct-GGUF
```

`lemonade run Qwen3-Coder-30B-A3B-Instruct-GGUF` scarica inoltre il modello al primo utilizzo se non è già presente, quindi lo carica per l'inferenza.

Il modello compare nell'elenco dei modelli scaricati del server Lemonade non appena il download viene completato; i controlli riportati di seguito confermano che è presente sulla macchina.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-coder-30b-a3b-instruct-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-Coder-30B-A3B-Instruct-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-coder-30b-a3b-instruct-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3-Coder-30B-A3B-Instruct-GGUF
```
<!-- @test:end -->
<!-- @os:end -->