<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

# Platformconfiguratie

Dit document beschrijft de verwachte platformconfiguratie voor het uitvoeren van deze playbook.

## Vereiste apps/frameworks

| Component       | Verwachte configuratie               | Opmerkingen                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python met `venv`-ondersteuning         | Wordt gebruikt om `kernel-env` aan te maken en te activeren                                     |
| ROCm Python SDK | ROCm 7.13-pakketfamilie             | Geïnstalleerd via de dependency-flow van de playbook                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Vereist voor `torch.cuda`, HIP-runtime, JIT-compilatie en `CUDAExtension` |
| GPU-driver      | AMD GPU-driver met ROCm/HIP-ondersteuning | Vereist voordat PyTorch de AMD GPU kan detecteren                               |

> Opmerking: Als u het AMD Ryzen™ AI Halo Developer Platform gebruikt, zijn AMD ROCm™-software en PyTorch al vooraf geïnstalleerd.

## Linux-vereisten

De volgende systeempakketten zijn vereist:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` is vereist om `kernel-env` aan te maken.
* `build-essential`, `gcc` en `g++` zijn vereist voor de C++-extensiehandleidingen.
* `amd-smi` wordt gebruikt voor GPU-zichtbaarheids-/gebruikscontroles onder Linux.

De C++-extensievoorbeelden bouwen native `.so`-modules vanuit `.cu`-bestanden via het `CUDAExtension`-pad van PyTorch.

## Windows-vereisten

Windows-runners vereisen:

* Python beschikbaar via `python`
* Installeer de nieuwste versie: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) of [nieuwer](https://visualstudio.microsoft.com/vs/community/) met de workload **Desktop development with C++**

De Visual Studio C++-omgeving moet het volgende bieden:
* `vcvars64.bat`
* `cl.exe`
* Windows SDK include- en library-paden

De C++-extensievoorbeelden bouwen native `.pyd`-modules vanuit `.cu`-bestanden via het `CUDAExtension`-pad van PyTorch.