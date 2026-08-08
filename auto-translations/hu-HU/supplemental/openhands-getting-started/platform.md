<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

# Platformkonfiguráció

Ez a dokumentum ismerteti az ehhez a playbookhoz szükséges platformkonfigurációkat.

## Szükséges alkalmazások/keretrendszerek

### Windows/Linux

- A **Lemonade Server**-t a
  [Lemonade telepítési útmutató](https://lemonade-server.ai/docs/guide/install/) alapján kell telepíteni.
- **Node.js 22.12 vagy újabb** verzió és `npm`, amelyet az `agent-canvas` CLI használ.
- **uv**, az a Python csomagkezelő, amelyet az Agent Canvas az ügynökkiszolgáló környezetének kezelésére használ. Telepítse az
  [uv telepítési útmutató](https://docs.astral.sh/uv/getting-started/installation/) alapján.

## Szükséges modellek

### Windows/Linux

A következő modellnek elérhetőnek kell lennie a Lemonade Server számára a playbook elindítása előtt.

| Modell típusa | Modellazonosító | Megjegyzések |
| --- | --- | --- |
| GGUF chat modell | `Qwen3.6-35B-A3B-GGUF` | A Lemonade Server szolgáltatja a `http://127.0.0.1:13305/api/v1` címen. 32 GB-nál kevesebb memóriával rendelkező eszközökön használjon kisebb GGUF modellt. |

Indítsa el a modellt a következővel:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```
