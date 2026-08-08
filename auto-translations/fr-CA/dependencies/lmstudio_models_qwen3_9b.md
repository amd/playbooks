<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Téléchargement de Qwen3.5 9B sur LM Studio

Pour télécharger le modèle Qwen3.5 9B :

1. Appuyez sur « Ctrl » + « Shift » + « M » sur votre clavier ou cliquez sur l'onglet « Discover » (icône de loupe) dans la barre latérale gauche
2. Recherchez `Qwen3.5 9B`
3. Sélectionnez une quantification (la quantification recommandée `Q4_K_M` offre un bon équilibre entre taille et qualité), puis cliquez sur Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio téléchargera automatiquement le modèle et le placera dans le répertoire approprié.

Si vous souhaitez télécharger des modèles supplémentaires, vous pouvez les rechercher dans l'onglet Discover, et LM Studio s'occupera du reste.

<!-- @os:windows -->
<!-- @test:id=lmstudio-model-present-qwen-windows timeout=60 hidden=True -->
```powershell
lms ls --llm | Select-String -Pattern "qwen3.5-9b"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-model-present-qwen-linux timeout=60 hidden=True -->
```bash
lms ls --llm | grep -i "qwen3.5-9b"
```
<!-- @test:end -->
<!-- @os:end -->