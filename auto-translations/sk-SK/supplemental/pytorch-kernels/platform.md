<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfigurácia platformy

Tento dokument popisuje očakávanú konfiguráciu platformy pre spustenie tohto playbooku.

## Požadované aplikácie / frameworky

| Komponent       | Očakávaná konfigurácia               | Poznámky                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python s podporou `venv`         | Používa sa na vytvorenie a aktiváciu `kernel-env`                                     |
| ROCm Python SDK | Rodina balíkov ROCm 7.13             | Inštalovaná prostredníctvom toku závislostí playbooku                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Vyžadované pre `torch.cuda`, HIP runtime, JIT kompiláciu a `CUDAExtension` |
| GPU Driver      | AMD GPU ovládač s podporou ROCm/HIP | Vyžadované pred tým, ako PyTorch dokáže detekovať AMD GPU                               |

> Poznámka: Ak používate AMD Ryzen™ AI Halo Developer Platform, AMD ROCm™ softvér a PyTorch sú predinštalované.

## Predpoklady pre Linux

Vyžadujú sa nasledujúce systémové balíky:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` je vyžadované na vytvorenie `kernel-env`.
* `build-essential`, `gcc` a `g++` sú vyžadované pre návody na rozšírenia C++.
* `amd-smi` sa používa na kontrolu viditeľnosti/využitia GPU v Linuxe.

Príklady rozšírení C++ zostavujú natívne moduly `.so` zo súborov `.cu` pomocou cesty `CUDAExtension` v PyTorch.

## Predpoklady pre Windows

Spúšťače pre Windows vyžadujú:

* Python dostupný cez `python`
* Nainštalujte najnovšiu verziu: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) alebo [novší](https://visualstudio.microsoft.com/vs/community/) s pracovnou záťažou **Vývoj desktopových aplikácií v C++**

Prostredie C++ vo Visual Studio musí poskytovať:
* `vcvars64.bat`
* `cl.exe`
* Cesty k hlavičkovým súborom a knižniciam Windows SDK

Príklady rozšírení C++ zostavujú natívne moduly `.pyd` zo súborov `.cu` pomocou cesty `CUDAExtension` v PyTorch.