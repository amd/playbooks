<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfiguracija platforme

Ovaj dokument opisuje očekivanu konfiguraciju platforme za pokretanje ovog priručnika.

## Potrebne aplikacije / okviri

| Komponenta      | Očekivana konfiguracija              | Napomene                                                                     |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python sa podrškom za `venv`       | Koristi se za kreiranje i aktivaciju `kernel-env`                            |
| ROCm Python SDK | ROCm 7.13 familija paketa            | Instalira se kroz tok zavisnosti priručnika                                  |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Potrebno za `torch.cuda`, HIP runtime, JIT kompilaciju i `CUDAExtension`    |
| GPU Driver      | AMD GPU drajver sa podrškom za ROCm/HIP | Potrebno pre nego što PyTorch može da detektuje AMD GPU                  |

> Napomena: Ako koristite AMD Ryzen™ AI Halo Developer Platform, AMD ROCm™ softver i PyTorch su unapred instalirani.

## Linux preduslovi

Sledeći sistemski paketi su potrebni:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` je potreban za kreiranje `kernel-env`.
* `build-essential`, `gcc` i `g++` su potrebni za primere sa C++ ekstenzijama.
* `amd-smi` se koristi za proveru vidljivosti/iskorišćenosti GPU-a na Linuxu.

Primeri C++ ekstenzija grade native `.so` module iz `.cu` fajlova koristeći PyTorch-ov `CUDAExtension` put.

## Windows preduslovi

Windows pokretači zahtevaju:

* Python dostupan kroz `python`
* Instalirajte najnoviji: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) ili [noviji](https://visualstudio.microsoft.com/vs/community/) sa radnim opterećenjem **Desktop development with C++**

C++ okruženje Visual Studio-a mora da obezbedi:
* `vcvars64.bat`
* `cl.exe`
* Windows SDK putanje za uključivanje i biblioteke

Primeri C++ ekstenzija grade native `.pyd` module iz `.cu` fajlova koristeći PyTorch-ov `CUDAExtension` put.