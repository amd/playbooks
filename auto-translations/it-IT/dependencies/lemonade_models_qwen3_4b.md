<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Download di Qwen3.5 4B per Lemonade

Il server Lemonade serve il modello Qwen3.5 4B (`Qwen3.5-4B-GGUF`). Per scaricarlo in anticipo:

```bash
lemonade pull Qwen3.5-4B-GGUF
```

`lemonade run Qwen3.5-4B-GGUF` scarica inoltre il modello al primo utilizzo, se non è già presente, e poi lo carica per l'inferenza.

Il modello compare nell'elenco dei modelli scaricati del server Lemonade una volta completato il download; i controlli riportati di seguito confermano che è presente sulla macchina.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-5-4b-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3.5-4B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-5-4b-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3.5-4B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->