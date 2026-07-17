<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfigurace platformy

Tento dokument popisuje očekávanou konfiguraci platformy pro spuštění tohoto playbooku.

## Požadované aplikace / frameworky

| Komponenta      | Očekávaná konfigurace                | Poznámky                                                                     |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python s podporou `venv`           | Slouží k vytvoření a aktivaci `kernel-env`                                   |
| ROCm Python SDK | Rodina balíčků ROCm 7.13             | Instalováno prostřednictvím toku závislostí playbooku                        |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Vyžadováno pro `torch.cuda`, HIP runtime, JIT kompilaci a `CUDAExtension`   |
| GPU Driver      | Ovladač AMD GPU s podporou ROCm/HIP  | Vyžadováno před tím, než PyTorch dokáže detekovat AMD GPU                   |

> Poznámka: Pokud používáte AMD Ryzen™ AI Halo Developer Platform, AMD ROCm™ software a PyTorch jsou předinstalovány.

## Předpoklady pro Linux

Jsou vyžadovány následující systémové balíčky:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` je vyžadováno pro vytvoření `kernel-env`.
* `build-essential`, `gcc` a `g++` jsou vyžadovány pro návody k rozšířením C++.
* `amd-smi` se používá pro kontrolu viditelnosti/využití GPU v Linuxu.

Příklady rozšíření C++ sestavují nativní moduly `.so` ze souborů `.cu` pomocí cesty `CUDAExtension` v PyTorch.

## Předpoklady pro Windows

Spouštěče pro Windows vyžadují:

* Python dostupný přes `python`
* Nainstalujte nejnovější verzi: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) nebo [novější](https://visualstudio.microsoft.com/vs/community/) s úlohou **Vývoj desktopových aplikací v C++**

Prostředí C++ sady Visual Studio musí poskytovat:
* `vcvars64.bat`
* `cl.exe`
* Cesty k hlavičkovým souborům a knihovnám sady Windows SDK

Příklady rozšíření C++ sestavují nativní moduly `.pyd` ze souborů `.cu` pomocí cesty `CUDAExtension` v PyTorch.