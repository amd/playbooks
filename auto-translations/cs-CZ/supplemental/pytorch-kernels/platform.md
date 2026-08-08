<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

# Konfigurace platformy

Tento dokument popisuje očekávanou konfiguraci platformy pro spuštění tohoto playbooku.

## Požadované aplikace/frameworky

| Komponenta       | Očekávaná konfigurace               | Poznámky                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python s podporou `venv`         | Používá se k vytvoření a aktivaci `kernel-env`                                     |
| ROCm Python SDK | Balíček řady ROCm 7.13             | Instalováno prostřednictvím procesu závislostí playbooku                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Vyžadováno pro `torch.cuda`, běhové prostředí HIP, JIT kompilaci a `CUDAExtension` |
| Ovladač GPU      | Ovladač AMD GPU s podporou ROCm/HIP | Vyžadováno před tím, než PyTorch dokáže detekovat AMD GPU                               |

> Poznámka: Pokud používáte AMD Ryzen™ AI Halo Developer Platform, software AMD ROCm™ a PyTorch jsou předinstalovány.

## Předpoklady pro Linux

Jsou vyžadovány následující systémové balíčky:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` je vyžadován pro vytvoření `kernel-env`.
* `build-essential`, `gcc` a `g++` jsou vyžadovány pro postupy s rozšířeními v C++.
* `amd-smi` slouží ke kontrole viditelnosti a využití GPU v Linuxu.

Příklady rozšíření v C++ sestavují nativní moduly `.so` ze souborů `.cu` pomocí cesty `CUDAExtension` v PyTorch.

## Předpoklady pro Windows

Spouštěcí prostředí Windows vyžaduje:

* Python dostupný prostřednictvím `python`
* Nainstalujte nejnovější verzi: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) nebo [novější](https://visualstudio.microsoft.com/vs/community/) s pracovní zátěží **Vývoj desktopových aplikací v C++**

Prostředí Visual Studio C++ musí poskytovat:
* `vcvars64.bat`
* `cl.exe`
* Cesty k include souborům a knihovnám Windows SDK

Příklady rozšíření v C++ sestavují nativní moduly `.pyd` ze souborů `.cu` pomocí cesty `CUDAExtension` v PyTorch.