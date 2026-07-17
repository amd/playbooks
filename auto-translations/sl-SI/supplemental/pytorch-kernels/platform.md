<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfiguracija platforme

Ta dokument opisuje pričakovano konfiguracijo platforme za izvajanje tega priročnika.

## Zahtevane aplikacije / ogrodja

| Komponenta      | Pričakovana konfiguracija            | Opombe                                                                       |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python s podporo za `venv`         | Uporablja se za ustvarjanje in aktivacijo `kernel-env`                       |
| ROCm Python SDK | Družina paketov ROCm 7.13            | Nameščeno prek toka odvisnosti priročnika                                    |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Potrebno za `torch.cuda`, izvajalno okolje HIP, prevajanje JIT in `CUDAExtension` |
| Gonilnik GPU    | Gonilnik AMD GPU s podporo ROCm/HIP  | Potrebno, preden PyTorch lahko zazna AMD GPU                                 |

> Opomba: Če izvajate na razvijalski platformi AMD Ryzen™ AI Halo, sta AMD ROCm™ programska oprema in PyTorch že vnaprej nameščena.

## Predpogoji za Linux

Zahtevani so naslednji sistemski paketi:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` je potreben za ustvarjanje `kernel-env`.
* `build-essential`, `gcc` in `g++` so potrebni za vaje z razširitvami C++.
* `amd-smi` se uporablja za preverjanje vidljivosti/izkoriščenosti GPU v Linuxu.

Primeri razširitev C++ gradijo izvorne module `.so` iz datotek `.cu` z uporabo poti `CUDAExtension` v PyTorch.

## Predpogoji za Windows

Izvajalci v sistemu Windows zahtevajo:

* Python, dostopen prek `python`
* Namestite najnovejše: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) ali [novejšo različico](https://visualstudio.microsoft.com/vs/community/) z delovnim obremenilom **Namizni razvoj s C++**

Okolje C++ v Visual Studio mora zagotavljati:
* `vcvars64.bat`
* `cl.exe`
* Poti do vključenih datotek in knjižnic Windows SDK

Primeri razširitev C++ gradijo izvorne module `.pyd` iz datotek `.cu` z uporabo poti `CUDAExtension` v PyTorch.