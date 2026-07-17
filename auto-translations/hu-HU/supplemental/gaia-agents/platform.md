<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

Ez a dokumentum a playbook futtatásához szükséges platform konfigurációkat írja le.

## Szükséges alkalmazások/keretrendszerek

### Windows/Linux

A GAIA-t előre telepíteni kell a [GAIA telepítési útmutatóban](../../dependencies/gaia.md) megadott utasítások szerint.

A Lemonade Server-t előre telepíteni kell a [Lemonade telepítési útmutatóban](../../dependencies/lemonade.md) megadott utasítások szerint.

## Szükséges modellek

### Windows/Linux

A Hardware Advisor Agent a **Qwen3-Coder-30B** modellt használja az ügynök következtetéshez. Ez a modell automatikusan letöltődik a `gaia init` futtatása során. Nincs szükség manuális modell letöltésre.