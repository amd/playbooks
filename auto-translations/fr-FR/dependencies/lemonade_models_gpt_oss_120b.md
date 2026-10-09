<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Téléchargement de GPT-OSS 120B pour Lemonade

Le serveur Lemonade sert le modèle GPT-OSS 120B MXFP4 GGUF (`gpt-oss-120b-mxfp-GGUF`). Pour le télécharger à l'avance :

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

`lemonade run gpt-oss-120b-mxfp-GGUF` télécharge également le modèle lors de la première utilisation s'il n'est pas déjà présent, puis le charge pour l'inférence.

Le modèle apparaît dans la liste des modèles téléchargés du serveur Lemonade une fois le téléchargement terminé ; les vérifications ci-dessous confirment qu'il est présent sur la machine.

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