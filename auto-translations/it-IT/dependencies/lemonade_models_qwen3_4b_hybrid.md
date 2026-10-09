<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Download di Qwen3 4B Hybrid per Lemonade

Il server Lemonade fornisce il modello Qwen3 4B Hybrid (`Qwen3-4B-Hybrid`), che viene eseguito sull'NPU e sulla GPU dei processori Ryzen AI. Per scaricarlo in anticipo:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

Il modello compare nell'elenco dei modelli scaricati del server Lemonade una volta completato il pull; il controllo qui sotto conferma che è presente sulla macchina.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->