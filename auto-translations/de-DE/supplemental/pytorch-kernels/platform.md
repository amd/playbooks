<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Plattformkonfiguration

Dieses Dokument beschreibt die erwartete Plattformkonfiguration für die Ausführung dieses Playbooks.

## Erforderliche Apps / Frameworks

| Component       | Expected Configuration               | Notes                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python with `venv` support         | Used to create and activate `kernel-env`                                     |
| ROCm Python SDK | ROCm 7.13 package family             | Installed through the playbook dependency flow                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Required for `torch.cuda`, HIP runtime, JIT compilation, and `CUDAExtension` |
| GPU Driver      | AMD GPU driver with ROCm/HIP support | Required before PyTorch can detect the AMD GPU                               |

> Hinweis: Wenn Sie auf der AMD Ryzen™ AI Halo Developer Platform arbeiten, sind AMD ROCm™-Software und PyTorch vorinstalliert.

## Linux-Voraussetzungen

Die folgenden Systempakete sind erforderlich:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` wird benötigt, um `kernel-env` zu erstellen.
* `build-essential`, `gcc` und `g++` sind für die C++-Erweiterungs-Walkthroughs erforderlich.
* `amd-smi` wird für Linux-GPU-Sichtbarkeits-/Auslastungsprüfungen verwendet.

Die C++-Erweiterungsbeispiele erstellen native `.so`-Module aus `.cu`-Dateien über den `CUDAExtension`-Pfad von PyTorch.

## Windows-Voraussetzungen

Windows-Runner erfordern:

* Python verfügbar über `python`
* Neueste Version installieren: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) oder [neuer](https://visualstudio.microsoft.com/vs/community/) mit der Workload **Desktopentwicklung mit C++**

Die C++-Umgebung von Visual Studio muss Folgendes bereitstellen:
* `vcvars64.bat`
* `cl.exe`
* Windows SDK-Include- und Bibliothekspfade

Die C++-Erweiterungsbeispiele erstellen native `.pyd`-Module aus `.cu`-Dateien über den `CUDAExtension`-Pfad von PyTorch.