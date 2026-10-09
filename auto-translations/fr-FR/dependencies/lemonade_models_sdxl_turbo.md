<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Téléchargement de SDXL-Turbo pour Lemonade

Le serveur Lemonade propose le modèle SDXL-Turbo (`SDXL-Turbo`). Pour le télécharger à l'avance :

```bash
lemonade pull SDXL-Turbo
```

`lemonade run SDXL-Turbo` télécharge également le modèle lors de la première utilisation s'il n'est pas déjà présent, puis le charge pour l'inférence.

Le modèle apparaît dans la liste des modèles téléchargés du serveur Lemonade une fois le téléchargement terminé ; les vérifications ci-dessous confirment sa présence sur la machine.

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