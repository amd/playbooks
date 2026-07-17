<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platformkonfiguration

Dette dokument beskriver de forventede platformkonfigurationer til at køre dette playbook.

## Påkrævede apps/frameworks

### Windows/Linux

GAIA skal være forudinstalleret ved hjælp af instruktionerne i [GAIA-installationsvejledningen](../../dependencies/gaia.md).

Lemonade Server skal være forudinstalleret ved hjælp af instruktionerne i [Lemonade-installationsvejledningen](../../dependencies/lemonade.md).

## Påkrævede modeller

### Windows/Linux

Hardware Advisor Agent bruger **Qwen3-Coder-30B** til agentræsonnering. Denne model downloades automatisk under `gaia init`. Der kræves ingen manuelle modeldownloads.