<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

Ez a dokumentum a playbook futtatásához szükséges platform-konfigurációt írja le.

## Szükséges alkalmazások / keretrendszerek

| Komponens       | Elvárt konfiguráció                  | Megjegyzések                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python `venv` támogatással         | A `kernel-env` létrehozásához és aktiválásához szükséges                                     |
| ROCm Python SDK | ROCm 7.13 csomagcsalád             | A playbook függőségi folyamatán keresztül telepítve                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | A `torch.cuda`, a HIP futtatókörnyezet, a JIT fordítás és a `CUDAExtension` használatához szükséges |
| GPU Driver      | AMD GPU illesztőprogram ROCm/HIP támogatással | Szükséges, mielőtt a PyTorch képes lenne érzékelni az AMD GPU-t                               |

> Megjegyzés: Ha AMD Ryzen™ AI Halo Developer Platform platformon futtat, az AMD ROCm™ szoftver és a PyTorch előre telepítve van.

## Linux előfeltételek

A következő rendszercsomagok szükségesek:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* A `python3-venv` szükséges a `kernel-env` létrehozásához.
* A `build-essential`, a `gcc` és a `g++` szükségesek a C++ kiterjesztési útmutatókhoz.
* Az `amd-smi` a Linux GPU láthatóság/kihasználtság ellenőrzéséhez használatos.

A C++ kiterjesztési példák natív `.so` modulokat építenek `.cu` fájlokból a PyTorch `CUDAExtension` útvonalán keresztül.

## Windows előfeltételek

A Windows futtatókörnyezetekhez szükséges:

* Python elérhető a `python` parancson keresztül
* Telepítse a legújabb verziót: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) vagy [újabb](https://visualstudio.microsoft.com/vs/community/) a **Desktop development with C++** munkaterheléssel

A Visual Studio C++ környezetnek biztosítania kell:
* `vcvars64.bat`
* `cl.exe`
* Windows SDK include és library útvonalak

A C++ kiterjesztési példák natív `.pyd` modulokat építenek `.cu` fájlokból a PyTorch `CUDAExtension` útvonalán keresztül.