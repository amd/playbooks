<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

Ez a dokumentum ismerteti azokat a platformkonfigurációkat, amelyek szükségesek ehhez a playbookhoz.

## Szükséges alkalmazások/keretrendszerek

### Windows/Linux

A GAIA-t előzetesen telepíteni kell a [GAIA Installation Guide](../../dependencies/gaia.md) útmutatóban található utasítások szerint.

A Lemonade Servert előzetesen telepíteni kell a [Lemonade Installation Guide](../../dependencies/lemonade.md) útmutatóban található utasítások szerint.

## Szükséges modellek

### Windows/Linux

A Hardware Advisor Agent a **Qwen3-Coder-30B** modellt használja az ügynöki következtetéshez. Ez a modell automatikusan letöltődik a `gaia init` futtatásakor. Nincs szükség manuális modellletöltésre.