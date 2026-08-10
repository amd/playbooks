<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Téléchargement de GPT-OSS 120B sur LM Studio

Pour télécharger le modèle GPT-OSS 120B :

1. Appuyez sur « Ctrl » + « Shift » + « M » sur votre clavier ou cliquez sur l'onglet « Discover » (icône de loupe) dans la barre latérale gauche
2. Recherchez `ggml-org/gpt-oss-120b-GGUF`
3. Sélectionnez `mxfp4` et cliquez sur Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio téléchargera automatiquement le modèle et le placera dans le répertoire approprié.

Si vous souhaitez télécharger d'autres modèles, vous pouvez les rechercher dans l'onglet Discover et LM Studio se chargera du reste.

<!-- @os:windows -->
<!-- @test:id=lmstudio-model-present-windows timeout=60 hidden=True -->
```powershell
lms ls --llm | Select-String -Pattern "gpt-oss-120b"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-model-present-linux timeout=60 hidden=True -->
```bash
lms ls --llm | grep -i "gpt-oss-120b"
```
<!-- @test:end -->
<!-- @os:end -->