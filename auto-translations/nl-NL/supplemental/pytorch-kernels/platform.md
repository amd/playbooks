<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platformconfiguratie

Dit document beschrijft de verwachte platformconfiguratie voor het uitvoeren van dit playbook.

## Vereiste apps / frameworks

| Component       | Verwachte configuratie               | Opmerkingen                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python met `venv`-ondersteuning         | Gebruikt om `kernel-env` aan te maken en te activeren                                     |
| ROCm Python SDK | ROCm 7.13-pakketfamilie             | Geïnstalleerd via de afhankelijkheidsstroom van het playbook                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Vereist voor `torch.cuda`, HIP-runtime, JIT-compilatie en `CUDAExtension` |
| GPU-stuurprogramma      | AMD GPU-stuurprogramma met ROCm/HIP-ondersteuning | Vereist voordat PyTorch de AMD GPU kan detecteren                               |

> Opmerking: Als u werkt op het AMD Ryzen™ AI Halo Developer Platform, zijn AMD ROCm™-software en PyTorch vooraf geïnstalleerd.

## Linux-vereisten

De volgende systeempakketten zijn vereist:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` is vereist om `kernel-env` aan te maken.
* `build-essential`, `gcc` en `g++` zijn vereist voor de C++-extensie-walkthroughs.
* `amd-smi` wordt gebruikt voor GPU-zichtbaarheids-/gebruikscontroles op Linux.

De C++-extensievoorbeelden bouwen native `.so`-modules van `.cu`-bestanden via het `CUDAExtension`-pad van PyTorch.

## Windows-vereisten

Windows-runners vereisen:

* Python beschikbaar via `python`
* Installeer de nieuwste versie: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) of [nieuwer](https://visualstudio.microsoft.com/vs/community/) met de workload **Bureaubladontwikkeling met C++**

De C++-omgeving van Visual Studio moet het volgende bieden:
* `vcvars64.bat`
* `cl.exe`
* Windows SDK-include- en bibliotheekpaden

De C++-extensievoorbeelden bouwen native `.pyd`-modules van `.cu`-bestanden via het `CUDAExtension`-pad van PyTorch.