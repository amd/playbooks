<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tłumaczenie maszynowe.** Ta strona została automatycznie przetłumaczona z języka angielskiego i nie została zweryfikowana przez człowieka. Może zawierać błędy, a niektóre instrukcje, polecenia, pliki do pobrania, dostępność produktów lub inne treści mogą różnić się w zależności od języka lub regionu. W przypadku jakichkolwiek niezgodności lub rozbieżności rozstrzygająca jest oryginalna angielska wersja playbook.
<!-- auto-translated-disclaimer:end -->

# Konfiguracja platformy

Ten dokument opisuje oczekiwaną konfigurację platformy do uruchomienia tego playbooka.

## Wymagane aplikacje / frameworki

| Komponent       | Oczekiwana konfiguracja               | Uwagi                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python z obsługą `venv`         | Używany do tworzenia i aktywowania `kernel-env`                                     |
| ROCm Python SDK | Rodzina pakietów ROCm 7.13             | Instalowany w ramach przepływu zależności playbooka                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Wymagany dla `torch.cuda`, środowiska uruchomieniowego HIP, kompilacji JIT oraz `CUDAExtension` |
| Sterownik GPU      | Sterownik AMD GPU z obsługą ROCm/HIP | Wymagany, zanim PyTorch będzie w stanie wykryć GPU AMD                                 |

> Uwaga: Jeśli korzystasz z platformy AMD Ryzen™ AI Halo Developer Platform, oprogramowanie AMD ROCm™ oraz PyTorch są preinstalowane.

## Wymagania wstępne dla systemu Linux

Wymagane są następujące pakiety systemowe:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` jest wymagany do utworzenia `kernel-env`.
* `build-essential`, `gcc` oraz `g++` są wymagane do przewodników dotyczących rozszerzeń C++.
* `amd-smi` jest używane do sprawdzania widoczności/wykorzystania GPU w systemie Linux.

Przykłady rozszerzeń C++ budują natywne moduły `.so` z plików `.cu`, korzystając ze ścieżki `CUDAExtension` w PyTorch.

## Wymagania wstępne dla systemu Windows

Runnery systemu Windows wymagają:

* Pythona dostępnego poprzez `python`
* Zainstalowania najnowszej wersji: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) lub [nowszego](https://visualstudio.microsoft.com/vs/community/) z obciążeniem roboczym **Programowanie aplikacji klasycznych w C++**

Środowisko Visual Studio C++ musi zapewniać:
* `vcvars64.bat`
* `cl.exe`
* Ścieżki plików nagłówkowych i bibliotek Windows SDK

Przykłady rozszerzeń C++ budują natywne moduły `.pyd` z plików `.cu`, korzystając ze ścieżki `CUDAExtension` w PyTorch.