<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

# Platform konfiguráció

Ez a dokumentum ismerteti a jelen playbook futtatásához szükséges elvárt platformkonfigurációt.

## Szükséges alkalmazások / keretrendszerek

| Komponens        | Elvárt konfiguráció                  | Megjegyzések                                                                 |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python `venv` támogatással           | A `kernel-env` létrehozásához és aktiválásához használt                      |
| ROCm Python SDK | ROCm 7.13 csomagcsalád               | A playbook függőségi folyamatán keresztül telepítve                          |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Szükséges a `torch.cuda`, a HIP futtatókörnyezet, a JIT fordítás és a `CUDAExtension` működéséhez |
| GPU illesztőprogram | AMD GPU illesztőprogram ROCm/HIP támogatással | Szükséges, mielőtt a PyTorch felismerné az AMD GPU-t                         |

> Megjegyzés: Ha az AMD Ryzen™ AI Halo Developer Platformon dolgozol, az AMD ROCm™ szoftver és a PyTorch előre telepítve van.

## Linux előfeltételek

A következő rendszercsomagok szükségesek:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* A `python3-venv` szükséges a `kernel-env` létrehozásához.
* A `build-essential`, `gcc` és `g++` szükséges a C++ bővítményekhez kapcsolódó bemutatókhoz.
* Az `amd-smi` a Linux GPU-láthatóság/kihasználtság ellenőrzéséhez használatos.

A C++ bővítménypéldák natív `.so` modulokat építenek `.cu` fájlokból a PyTorch `CUDAExtension` útvonalának használatával.

## Windows előfeltételek

A Windows futtatókörnyezetekhez az alábbiak szükségesek:

* Python elérhetősége a `python` parancson keresztül
* A legújabb verzió telepítése: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) vagy [újabb](https://visualstudio.microsoft.com/vs/community/) a **Desktop development with C++** munkaterhelés telepítésével

A Visual Studio C++ környezetnek biztosítania kell:
* `vcvars64.bat`
* `cl.exe`
* Windows SDK include és library elérési utak

A C++ bővítménypéldák natív `.pyd` modulokat építenek `.cu` fájlokból a PyTorch `CUDAExtension` útvonalának használatával.