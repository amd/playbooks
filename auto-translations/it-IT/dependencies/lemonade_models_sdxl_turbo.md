<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Download di SDXL-Turbo per Lemonade

Il server Lemonade serve il modello SDXL-Turbo (`SDXL-Turbo`). Per scaricarlo in anticipo:

```bash
lemonade pull SDXL-Turbo
```

Anche `lemonade run SDXL-Turbo` scarica il modello al primo utilizzo se non è già presente, quindi lo carica per l'inferenza.

Il modello compare nell'elenco dei modelli scaricati del server Lemonade al termine del download; i controlli riportati di seguito confermano che è presente sulla macchina.

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