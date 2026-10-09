<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Scaricare SDXL-Turbo per Lemonade

Il server Lemonade serve il modello SDXL-Turbo (`SDXL-Turbo`). Per scaricarlo in anticipo:

```bash
lemonade pull SDXL-Turbo
```

`lemonade run SDXL-Turbo` scarica inoltre il modello al primo utilizzo, se non è già presente, e poi lo carica per l'inferenza.

Il modello compare nell'elenco dei modelli scaricati del server Lemonade una volta completato il download; i controlli seguenti confermano la sua presenza sulla macchina.

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