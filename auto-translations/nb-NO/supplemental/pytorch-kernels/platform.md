<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden ble automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte instruksjoner, kommandoer, nedlastinger, produkttilgjengelighet eller annet innhold kan variere etter språk eller region. Ved eventuelle uoverensstemmelser eller avvik er den opprinnelige engelske versjonen av playbook-en gjeldende.
<!-- auto-translated-disclaimer:end -->

# Plattformkonfigurasjon

Dette dokumentet beskriver forventet plattformkonfigurasjon for å kjøre denne playbooken.

## Nødvendige apper/rammeverk

| Komponent       | Forventet konfigurasjon               | Merknader                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python med `venv`-støtte         | Brukes til å opprette og aktivere `kernel-env`                                     |
| ROCm Python SDK | ROCm 7.13-pakkefamilie             | Installeres gjennom playbookens avhengighetsflyt                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Kreves for `torch.cuda`, HIP-kjøretidsmiljøet, JIT-kompilering og `CUDAExtension` |
| GPU-driver      | AMD GPU-driver med ROCm/HIP-støtte | Kreves før PyTorch kan oppdage AMD GPU-en                               |

> Merk: Hvis du kjører på AMD Ryzen™ AI Halo Developer Platform, er AMD ROCm™-programvare og PyTorch forhåndsinstallert.

## Forutsetninger for Linux

Følgende systempakker kreves:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` kreves for å opprette `kernel-env`.
* `build-essential`, `gcc` og `g++` kreves for gjennomgangene med C++-utvidelser.
* `amd-smi` brukes til å sjekke GPU-synlighet/-utnyttelse på Linux.

Eksemplene med C++-utvidelser bygger native `.so`-moduler fra `.cu`-filer ved hjelp av PyTorchs `CUDAExtension`-løp.

## Forutsetninger for Windows

Windows-kjøremiljøer krever:

* Python tilgjengelig via `python`
* Installer nyeste versjon: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) eller [nyere](https://visualstudio.microsoft.com/vs/community/) med arbeidsbelastningen **Desktop development with C++**

Visual Studio C++-miljøet må tilby:
* `vcvars64.bat`
* `cl.exe`
* Inkluderings- og bibliotekbaner for Windows SDK

Eksemplene med C++-utvidelser bygger native `.pyd`-moduler fra `.cu`-filer ved hjelp av PyTorchs `CUDAExtension`-løp.