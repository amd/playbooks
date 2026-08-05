<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinöversättning.** Den här sidan har automatiskt översatts från engelska och har inte granskats av en människa. Den kan innehålla fel, och vissa instruktioner, kommandon, nedladdningar, produkttillgänglighet eller annat innehåll kan variera beroende på språk eller region. Vid eventuella motsägelser eller avvikelser är det den ursprungliga engelska versionen av playbook som gäller och har företräde.
<!-- auto-translated-disclaimer:end -->

# Plattformskonfiguration

Detta dokument beskriver den förväntade plattformskonfigurationen för att köra denna playbook.

## Obligatoriska appar/ramverk

| Komponent       | Förväntad konfiguration               | Anteckningar                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python med `venv`-stöd         | Används för att skapa och aktivera `kernel-env`                                     |
| ROCm Python SDK | ROCm 7.13-paketfamiljen             | Installeras genom playbookens beroendeflöde                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Krävs för `torch.cuda`, HIP-runtime, JIT-kompilering och `CUDAExtension` |
| GPU-drivrutin      | AMD GPU-drivrutin med ROCm/HIP-stöd | Krävs innan PyTorch kan identifiera AMD GPU:n                               |

> Obs: Om du kör på AMD Ryzen™ AI Halo Developer Platform är AMD ROCm™-programvara och PyTorch förinstallerade.

## Förutsättningar för Linux

Följande systempaket krävs:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` krävs för att skapa `kernel-env`.
* `build-essential`, `gcc` och `g++` krävs för genomgångarna med C++-tillägg.
* `amd-smi` används för kontroll av GPU-synlighet/-användning på Linux.

Exemplen med C++-tillägg bygger inbyggda `.so`-moduler från `.cu`-filer med hjälp av PyTorchs `CUDAExtension`-metod.

## Förutsättningar för Windows

Windows-körningsmiljöer kräver:

* Python tillgängligt via `python`
* Installera senaste version: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) eller [nyare](https://visualstudio.microsoft.com/vs/community/) med arbetsbelastningen **Desktop development with C++**

Visual Studios C++-miljö måste tillhandahålla:
* `vcvars64.bat`
* `cl.exe`
* Sökvägar till Windows SDK:s include- och biblioteksfiler

Exemplen med C++-tillägg bygger inbyggda `.pyd`-moduler från `.cu`-filer med hjälp av PyTorchs `CUDAExtension`-metod.