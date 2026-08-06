<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

# Konfiguracija platforme

Ta dokument opisuje pričakovano konfiguracijo platforme za zagon tega priročnika (playbook).

## Zahtevane aplikacije / ogrodja

| Komponenta       | Pričakovana konfiguracija               | Opombe                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python s podporo za `venv`         | Uporabljen za ustvarjanje in aktiviranje `kernel-env`                                     |
| ROCm Python SDK | Družina paketov ROCm 7.13             | Nameščen prek poteka odvisnosti priročnika               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Zahtevan za `torch.cuda`, izvajalno okolje HIP, JIT prevajanje in `CUDAExtension` |
| Gonilnik GPU      | Gonilnik AMD GPU s podporo za ROCm/HIP | Zahtevan, preden lahko PyTorch zazna GPU AMD                               |

> Opomba: Če delate na razvojni platformi AMD Ryzen™ AI Halo, sta programska oprema AMD ROCm™ in PyTorch že vnaprej nameščena.

## Predpogoji za Linux

Zahtevani so naslednji sistemski paketi:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` je zahtevan za ustvarjanje `kernel-env`.
* `build-essential`, `gcc` in `g++` so zahtevani za vodiče o razširitvah C++.
* `amd-smi` se uporablja za preverjanje vidljivosti/izkoriščenosti GPU v Linuxu.

Primeri razširitev C++ zgradijo izvorne module `.so` iz datotek `.cu` z uporabo poti `CUDAExtension` v PyTorch.

## Predpogoji za Windows

Izvajalna okolja Windows zahtevajo:

* Python, dostopen prek `python`
* Namestite najnovejšo različico: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) ali [novejši](https://visualstudio.microsoft.com/vs/community/) z delovno obremenitvijo **Desktop development with C++**

Okolje Visual Studio C++ mora zagotavljati:
* `vcvars64.bat`
* `cl.exe`
* Poti za vključitve in knjižnice Windows SDK

Primeri razširitev C++ zgradijo izvorne module `.pyd` iz datotek `.cu` z uporabo poti `CUDAExtension` v PyTorch.