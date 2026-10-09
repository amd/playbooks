<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Download di Gemma-4 E2B per Lemonade

Il server Lemonade serve il modello Gemma-4 E2B (`Gemma-4-E2B-it-GGUF`). Per scaricarlo in anticipo:

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

Anche `lemonade run Gemma-4-E2B-it-GGUF` scarica il modello al primo utilizzo, se non è già presente, e poi lo carica per l'inferenza.

Il modello compare nell'elenco dei modelli scaricati del server Lemonade non appena il download viene completato; i controlli riportati di seguito confermano che è presente sulla macchina.

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