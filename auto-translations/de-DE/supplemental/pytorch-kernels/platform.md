<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maschinelle Übersetzung.** Diese Seite wurde automatisch aus dem Englischen übersetzt und nicht von einem Menschen überprüft. Sie kann Fehler enthalten, und bestimmte Anweisungen, Befehle, Downloads, Produktverfügbarkeiten oder andere Inhalte können je nach Sprache oder Region abweichen. Im Falle von Unstimmigkeiten oder Widersprüchen ist die englische Originalversion des playbook maßgeblich und hat Vorrang.
<!-- auto-translated-disclaimer:end -->

# Plattformkonfiguration

Dieses Dokument beschreibt die erwartete Plattformkonfiguration für die Ausführung dieses Playbooks.

## Erforderliche Apps / Frameworks

| Komponente       | Erwartete Konfiguration               | Hinweise                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python mit `venv`-Unterstützung         | Wird zum Erstellen und Aktivieren von `kernel-env` verwendet                                     |
| ROCm Python SDK | ROCm 7.13 Paketfamilie             | Wird über den Abhängigkeitsablauf des Playbooks installiert                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Erforderlich für `torch.cuda`, HIP-Runtime, JIT-Kompilierung und `CUDAExtension` |
| GPU-Treiber      | AMD GPU-Treiber mit ROCm-/HIP-Unterstützung | Erforderlich, bevor PyTorch die AMD GPU erkennen kann                               |

> Hinweis: Wenn Sie auf der AMD Ryzen™ AI Halo Developer Platform arbeiten, sind AMD ROCm™ Software und PyTorch bereits vorinstalliert.

## Linux-Voraussetzungen

Die folgenden Systempakete werden benötigt:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` wird benötigt, um `kernel-env` zu erstellen.
* `build-essential`, `gcc` und `g++` sind für die C++-Erweiterungs-Walkthroughs erforderlich.
* `amd-smi` wird für Linux-GPU-Sichtbarkeits-/Auslastungsprüfungen verwendet.

Die C++-Erweiterungsbeispiele erstellen native `.so`-Module aus `.cu`-Dateien mithilfe des `CUDAExtension`-Pfads von PyTorch.

## Windows-Voraussetzungen

Windows-Runner benötigen:

* Python, verfügbar über `python`
* Installieren Sie die neueste Version: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) oder [neuer](https://visualstudio.microsoft.com/vs/community/) mit der Workload **Desktopentwicklung mit C++**

Die Visual Studio C++-Umgebung muss Folgendes bereitstellen:
* `vcvars64.bat`
* `cl.exe`
* Include- und Bibliothekspfade des Windows SDK

Die C++-Erweiterungsbeispiele erstellen native `.pyd`-Module aus `.cu`-Dateien mithilfe des `CUDAExtension`-Pfads von PyTorch.