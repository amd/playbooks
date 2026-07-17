<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Plattformskonfiguration

Det här dokumentet beskriver den förväntade plattformskonfigurationen för att köra den här spelboken.

## Nödvändiga appar / ramverk

| Komponent       | Förväntad konfiguration              | Anteckningar                                                                 |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python med `venv`-stöd             | Används för att skapa och aktivera `kernel-env`                              |
| ROCm Python SDK | ROCm 7.13-paketfamilj                | Installeras via spelbokens beroendeflöde                                     |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Krävs för `torch.cuda`, HIP-körtid, JIT-kompilering och `CUDAExtension`     |
| GPU-drivrutin   | AMD GPU-drivrutin med ROCm/HIP-stöd  | Krävs innan PyTorch kan identifiera AMD GPU                                  |

> Obs: Om du kör på AMD Ryzen™ AI Halo Developer Platform är AMD ROCm™-programvara och PyTorch förinstallerade.

## Linux-förutsättningar

Följande systempaket krävs:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` krävs för att skapa `kernel-env`.
* `build-essential`, `gcc` och `g++` krävs för genomgångarna av C++-tillägg.
* `amd-smi` används för kontroller av GPU-synlighet/användning i Linux.

C++-tilläggsexemplen bygger inbyggda `.so`-moduler från `.cu`-filer med hjälp av PyTorch:s `CUDAExtension`-sökväg.

## Windows-förutsättningar

Windows-körningar kräver:

* Python tillgängligt via `python`
* Installera senaste: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) eller [nyare](https://visualstudio.microsoft.com/vs/community/) med arbetsbelastningen **Skrivbordsutveckling med C++**

Visual Studio C++-miljön måste tillhandahålla:
* `vcvars64.bat`
* `cl.exe`
* Windows SDK-inkluderings- och bibliotekssökvägar

C++-tilläggsexemplen bygger inbyggda `.pyd`-moduler från `.cu`-filer med hjälp av PyTorch:s `CUDAExtension`-sökväg.