<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

# Configurarea platformei

Acest document descrie configurația de platformă preconizată pentru rularea acestui playbook.

## Aplicații/framework-uri necesare

| Componentă       | Configurație preconizată               | Note                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python cu suport pentru `venv`         | Utilizat pentru a crea și activa `kernel-env`                                     |
| ROCm Python SDK | Familia de pachete ROCm 7.13             | Instalat prin fluxul de dependențe al playbook-ului                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Necesar pentru `torch.cuda`, runtime-ul HIP, compilarea JIT și `CUDAExtension` |
| Driver GPU      | Driver AMD GPU cu suport ROCm/HIP | Necesar înainte ca PyTorch să poată detecta GPU-ul AMD                               |

> Notă: Dacă rulați pe AMD Ryzen™ AI Halo Developer Platform, software-ul AMD ROCm™ și PyTorch sunt preinstalate.

## Cerințe preliminare pentru Linux

Sunt necesare următoarele pachete de sistem:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` este necesar pentru a crea `kernel-env`.
* `build-essential`, `gcc` și `g++` sunt necesare pentru ghidurile pas cu pas privind extensiile C++.
* `amd-smi` este utilizat pentru verificările de vizibilitate/utilizare a GPU-ului pe Linux.

Exemplele de extensii C++ construiesc module native `.so` din fișiere `.cu` folosind calea `CUDAExtension` a PyTorch.

## Cerințe preliminare pentru Windows

Executoarele Windows necesită:

* Python disponibil prin `python`
* Instalați cea mai recentă versiune: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) sau [o versiune mai nouă](https://visualstudio.microsoft.com/vs/community/) cu sarcina de lucru **Desktop development with C++**

Mediul Visual Studio C++ trebuie să ofere:
* `vcvars64.bat`
* `cl.exe`
* Căile pentru include-uri și biblioteci ale Windows SDK

Exemplele de extensii C++ construiesc module native `.pyd` din fișiere `.cu` folosind calea `CUDAExtension` a PyTorch.