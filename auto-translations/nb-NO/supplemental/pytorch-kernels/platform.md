<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Plattformkonfigurasjon

Dette dokumentet beskriver den forventede plattformkonfigurasjonen for å kjøre denne spilleboken.

## Nødvendige apper / rammeverk

| Komponent       | Forventet konfigurasjon              | Merknader                                                                    |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python med `venv`-støtte           | Brukes til å opprette og aktivere `kernel-env`                               |
| ROCm Python SDK | ROCm 7.13-pakkefamilien              | Installert gjennom spillebokens avhengighetsflyt                             |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Nødvendig for `torch.cuda`, HIP-kjøretid, JIT-kompilering og `CUDAExtension` |
| GPU-driver      | AMD GPU-driver med ROCm/HIP-støtte   | Nødvendig før PyTorch kan oppdage AMD GPU                                    |

> Merk: Hvis du kjører på AMD Ryzen™ AI Halo Developer Platform, er AMD ROCm™-programvare og PyTorch forhåndsinstallert.

## Linux-forutsetninger

Følgende systempakker er nødvendige:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` er nødvendig for å opprette `kernel-env`.
* `build-essential`, `gcc` og `g++` er nødvendige for gjennomgangene av C++-utvidelser.
* `amd-smi` brukes for kontroll av GPU-synlighet/-utnyttelse på Linux.

C++-utvidelseseksemplene bygger native `.so`-moduler fra `.cu`-filer ved hjelp av PyTorchs `CUDAExtension`-sti.

## Windows-forutsetninger

Windows-kjørere krever:

* Python tilgjengelig via `python`
* Installer nyeste: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) eller [nyere](https://visualstudio.microsoft.com/vs/community/) med arbeidsmengden **Skrivebordutvikling med C++**

Visual Studio C++-miljøet må tilby:
* `vcvars64.bat`
* `cl.exe`
* Windows SDK-inkluderings- og bibliotekstier

C++-utvidelseseksemplene bygger native `.pyd`-moduler fra `.cu`-filer ved hjelp av PyTorchs `CUDAExtension`-sti.