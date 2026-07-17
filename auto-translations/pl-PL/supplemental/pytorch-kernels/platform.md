<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfiguracja platformy

Ten dokument opisuje oczekiwaną konfigurację platformy do uruchamiania tego playbooka.

## Wymagane aplikacje / frameworki

| Komponent       | Oczekiwana konfiguracja              | Uwagi                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python z obsługą `venv`            | Używany do tworzenia i aktywowania `kernel-env`                              |
| ROCm Python SDK | Rodzina pakietów ROCm 7.13           | Instalowana przez przepływ zależności playbooka                              |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Wymagany dla `torch.cuda`, środowiska uruchomieniowego HIP, kompilacji JIT i `CUDAExtension` |
| Sterownik GPU   | Sterownik AMD GPU z obsługą ROCm/HIP | Wymagany, zanim PyTorch będzie mógł wykryć AMD GPU                           |

> Uwaga: Jeśli korzystasz z AMD Ryzen™ AI Halo Developer Platform, oprogramowanie AMD ROCm™ i PyTorch są preinstalowane.

## Wymagania wstępne dla systemu Linux

Wymagane są następujące pakiety systemowe:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` jest wymagany do tworzenia `kernel-env`.
* `build-essential`, `gcc` i `g++` są wymagane do przewodników po rozszerzeniach C++.
* `amd-smi` jest używany do sprawdzania widoczności/wykorzystania GPU w systemie Linux.

Przykłady rozszerzeń C++ budują natywne moduły `.so` z plików `.cu` przy użyciu ścieżki `CUDAExtension` PyTorch.

## Wymagania wstępne dla systemu Windows

Środowiska uruchomieniowe Windows wymagają:

* Pythona dostępnego przez `python`
* Zainstalowania najnowszej wersji: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) lub [nowszego](https://visualstudio.microsoft.com/vs/community/) z obciążeniem **Programowanie aplikacji klasycznych w języku C++**

Środowisko C++ Visual Studio musi zapewniać:
* `vcvars64.bat`
* `cl.exe`
* Ścieżki do plików nagłówkowych i bibliotek Windows SDK

Przykłady rozszerzeń C++ budują natywne moduły `.pyd` z plików `.cu` przy użyciu ścieżki `CUDAExtension` PyTorch.