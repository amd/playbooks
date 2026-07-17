<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platformkonfiguration

Dette dokument beskriver den forventede platformkonfiguration til at køre dette playbook.

## Påkrævede apps / frameworks

| Komponent       | Forventet konfiguration              | Noter                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python med `venv`-understøttelse   | Bruges til at oprette og aktivere `kernel-env`                               |
| ROCm Python SDK | ROCm 7.13-pakkefamilie               | Installeres via playbook-afhængighedsflowet                                  |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Påkrævet for `torch.cuda`, HIP-runtime, JIT-kompilering og `CUDAExtension`  |
| GPU Driver      | AMD GPU-driver med ROCm/HIP-understøttelse | Påkrævet, før PyTorch kan registrere AMD GPU'en                        |

> Bemærk: Hvis du kører på AMD Ryzen™ AI Halo Developer Platform, er AMD ROCm™-software og PyTorch forudinstalleret.

## Linux-forudsætninger

Følgende systempakker er påkrævede:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` er påkrævet for at oprette `kernel-env`.
* `build-essential`, `gcc` og `g++` er påkrævet til C++-udvidelsesgennemgangene.
* `amd-smi` bruges til Linux GPU-synligheds-/udnyttelsestjek.

C++-udvidelseseksemplerne bygger native `.so`-moduler fra `.cu`-filer ved hjælp af PyTorchs `CUDAExtension`-sti.

## Windows-forudsætninger

Windows-kørere kræver:

* Python tilgængeligt via `python`
* Installer seneste: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) eller [nyere](https://visualstudio.microsoft.com/vs/community/) med arbejdsbelastningen **Desktop development with C++**

Visual Studio C++-miljøet skal levere:
* `vcvars64.bat`
* `cl.exe`
* Windows SDK-include- og biblioteksstier

C++-udvidelseseksemplerne bygger native `.pyd`-moduler fra `.cu`-filer ved hjælp af PyTorchs `CUDAExtension`-sti.