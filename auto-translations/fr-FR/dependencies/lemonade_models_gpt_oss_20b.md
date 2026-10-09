<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Téléchargement de GPT-OSS 20B pour Lemonade

Le serveur Lemonade propose le modèle GPT-OSS 20B MXFP4 GGUF (`gpt-oss-20b-mxfp4-GGUF`). Pour le télécharger à l'avance :

```bash
lemonade pull gpt-oss-20b-mxfp4-GGUF
```

`lemonade run gpt-oss-20b-mxfp4-GGUF` télécharge également le modèle lors de la première utilisation s'il n'est pas déjà présent, puis le charge pour l'inférence.

Le modèle apparaît dans la liste des modèles téléchargés du serveur Lemonade une fois le téléchargement terminé ; les vérifications ci-dessous confirment sa présence sur la machine.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->