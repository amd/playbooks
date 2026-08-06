<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

# Konfiguracija platforme

Ovaj dokument opisuje očekivanu konfiguraciju platforme za izvršavanje ovog priručnika (playbook).

## Obavezne aplikacije/okviri

| Komponenta       | Očekivana konfiguracija               | Napomene                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python sa `venv` podrškom         | Koristi se za kreiranje i aktiviranje `kernel-env`                                     |
| ROCm Python SDK | ROCm 7.13 porodica paketa             | Instalira se kroz tok zavisnosti priručnika                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Neophodno za `torch.cuda`, HIP runtime, JIT kompilaciju i `CUDAExtension` |
| GPU drajver      | AMD GPU drajver sa ROCm/HIP podrškom | Neophodno pre nego što PyTorch može da detektuje AMD GPU                               |

> Napomena: Ako radite na AMD Ryzen™ AI Halo Developer Platform, AMD ROCm™ softver i PyTorch su unapred instalirani.

## Preduslovi za Linux

Potrebni su sledeći sistemski paketi:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` je potreban za kreiranje `kernel-env`.
* `build-essential`, `gcc` i `g++` su potrebni za vodiče kroz C++ ekstenzije.
* `amd-smi` se koristi za proveru vidljivosti/iskorišćenosti GPU-a na Linuxu.

Primeri C++ ekstenzija grade native `.so` module iz `.cu` fajlova koristeći PyTorch-ov `CUDAExtension` put.

## Preduslovi za Windows

Windows izvršioci zahtevaju:

* Python dostupan preko `python`
* Instalirajte najnoviju verziju: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) ili [noviji](https://visualstudio.microsoft.com/vs/community/) sa radnim opterećenjem **Desktop development with C++**

Visual Studio C++ okruženje mora da obezbedi:
* `vcvars64.bat`
* `cl.exe`
* Windows SDK include i library putanje

Primeri C++ ekstenzija grade native `.pyd` module iz `.cu` fajlova koristeći PyTorch-ov `CUDAExtension` put.