<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

# Platformkonfiguration

Dette dokument beskriver den forventede platformkonfiguration for at køre denne playbook.

## Krævede apps/frameworks

| Komponent       | Forventet konfiguration               | Bemærkninger                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python med `venv`-understøttelse         | Bruges til at oprette og aktivere `kernel-env`                                     |
| ROCm Python SDK | ROCm 7.13-pakkefamilie             | Installeres gennem playbookens afhængighedsflow                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Påkrævet for `torch.cuda`, HIP-runtime, JIT-kompilering og `CUDAExtension` |
| GPU-driver      | AMD GPU-driver med ROCm/HIP-understøttelse | Påkrævet, før PyTorch kan registrere AMD GPU'en                               |

> Bemærk: Hvis du kører på AMD Ryzen™ AI Halo Developer Platform, er AMD ROCm™-softwaren og PyTorch forudinstalleret.

## Forudsætninger for Linux

Følgende systempakker er påkrævet:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` er påkrævet for at oprette `kernel-env`.
* `build-essential`, `gcc` og `g++` er påkrævet til C++-udvidelsesgennemgangene.
* `amd-smi` bruges til synlighed/udnyttelsestjek af GPU'en på Linux.

C++-udvidelseseksemplerne bygger native `.so`-moduler fra `.cu`-filer ved hjælp af PyTorchs `CUDAExtension`-sti.

## Forudsætninger for Windows

Windows-runnere kræver:

* Python tilgængelig via `python`
* Installer nyeste: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) eller [nyere](https://visualstudio.microsoft.com/vs/community/) med workloaden **Desktop development with C++**

Visual Studio C++-miljøet skal levere:
* `vcvars64.bat`
* `cl.exe`
* Windows SDK-include- og biblioteksstier

C++-udvidelseseksemplerne bygger native `.pyd`-moduler fra `.cu`-filer ved hjælp af PyTorchs `CUDAExtension`-sti.