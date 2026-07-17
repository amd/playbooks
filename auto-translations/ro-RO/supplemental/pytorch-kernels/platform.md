<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configurarea Platformei

Acest document descrie configurarea așteptată a platformei pentru rularea acestui playbook.

## Aplicații / Framework-uri Necesare

| Componentă      | Configurare Așteptată                | Note                                                                         |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python cu suport `venv`            | Utilizat pentru a crea și activa `kernel-env`                                |
| ROCm Python SDK | Familia de pachete ROCm 7.13         | Instalat prin fluxul de dependențe al playbook-ului                          |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Necesar pentru `torch.cuda`, runtime HIP, compilare JIT și `CUDAExtension`  |
| Driver GPU      | Driver AMD GPU cu suport ROCm/HIP    | Necesar înainte ca PyTorch să poată detecta GPU-ul AMD                       |

> Notă: Dacă rulați pe AMD Ryzen™ AI Halo Developer Platform, AMD ROCm™ software și PyTorch sunt preinstalate.

## Cerințe Preliminare Linux

Următoarele pachete de sistem sunt necesare:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` este necesar pentru a crea `kernel-env`.
* `build-essential`, `gcc` și `g++` sunt necesare pentru parcurgerea exemplelor cu extensii C++.
* `amd-smi` este utilizat pentru verificarea vizibilității/utilizării GPU-ului pe Linux.

Exemplele cu extensii C++ compilează module native `.so` din fișiere `.cu` folosind calea `CUDAExtension` a PyTorch.

## Cerințe Preliminare Windows

Rularea pe Windows necesită:

* Python disponibil prin comanda `python`
* Instalați cea mai recentă versiune: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) sau [mai nou](https://visualstudio.microsoft.com/vs/community/) cu volumul de lucru **Dezvoltare desktop cu C++**

Mediul C++ din Visual Studio trebuie să furnizeze:
* `vcvars64.bat`
* `cl.exe`
* Căile de includere și bibliotecă ale Windows SDK

Exemplele cu extensii C++ compilează module native `.pyd` din fișiere `.cu` folosind calea `CUDAExtension` a PyTorch.