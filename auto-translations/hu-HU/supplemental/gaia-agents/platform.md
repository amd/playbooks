<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angolról, és emberi lektorálás nem történt. Hibákat tartalmazhat, és egyes lépések, parancsok, letöltések vagy termékelérhetőségek eltérhetnek az Ön nyelvében vagy régiójában. Ha bármi hibásnak tűnik, tekintse az eredeti angol nyelvű playbookot mérvadó forrásnak.
<!-- auto-translated-disclaimer:end -->

# Platform Configuration

Ez a dokumentum ismerteti azokat a platformkonfigurációkat, amelyek szükségesek ehhez a playbookhoz.

## Szükséges alkalmazások/keretrendszerek

### Windows/Linux

A GAIA-t előzetesen telepíteni kell a [GAIA Installation Guide](../../dependencies/gaia.md) útmutatóban található utasítások szerint.

A Lemonade Servert előzetesen telepíteni kell a [Lemonade Installation Guide](../../dependencies/lemonade.md) útmutatóban található utasítások szerint.

## Szükséges modellek

### Windows/Linux

A Hardware Advisor Agent a **Qwen3-Coder-30B** modellt használja az ügynöki következtetéshez. Ez a modell automatikusan letöltődik a `gaia init` futtatásakor. Nincs szükség manuális modellletöltésre.