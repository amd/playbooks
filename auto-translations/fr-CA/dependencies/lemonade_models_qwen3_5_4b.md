<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Téléchargement de Qwen3.5 4B pour Lemonade

Le serveur Lemonade dessert le modèle Qwen3.5 4B (`Qwen3.5-4B-GGUF`). Pour le télécharger à l'avance :

```bash
lemonade pull Qwen3.5-4B-GGUF
```

`lemonade run Qwen3.5-4B-GGUF` télécharge également le modèle lors de la première utilisation s'il n'est pas déjà présent, puis le charge pour l'inférence.

Le modèle apparaît dans la liste des modèles téléchargés du serveur Lemonade une fois le téléchargement terminé; les vérifications ci-dessous confirment qu'il est présent sur la machine.

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