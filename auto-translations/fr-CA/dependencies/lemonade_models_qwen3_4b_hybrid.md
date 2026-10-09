<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Téléchargement de Qwen3 4B Hybrid pour Lemonade

Le serveur Lemonade dessert le modèle Qwen3 4B Hybrid (`Qwen3-4B-Hybrid`), qui s'exécute sur le NPU et le GPU des processeurs Ryzen AI. Pour le télécharger à l'avance :

```powershell
lemonade pull Qwen3-4B-Hybrid
```

Le modèle apparaît dans la liste des modèles téléchargés du serveur Lemonade une fois le téléchargement terminé; la vérification ci-dessous confirme qu'il est présent sur la machine.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->