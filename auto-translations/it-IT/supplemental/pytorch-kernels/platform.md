<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configurazione della Piattaforma

Questo documento descrive la configurazione della piattaforma prevista per l'esecuzione di questo playbook.

## App / Framework Richiesti

| Componente      | Configurazione Prevista              | Note                                                                         |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python con supporto `venv`         | Utilizzato per creare e attivare `kernel-env`                                |
| ROCm Python SDK | Famiglia di pacchetti ROCm 7.13      | Installato tramite il flusso delle dipendenze del playbook                   |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Richiesto per `torch.cuda`, runtime HIP, compilazione JIT e `CUDAExtension` |
| Driver GPU      | Driver AMD GPU con supporto ROCm/HIP | Richiesto prima che PyTorch possa rilevare la AMD GPU                        |

> Nota: Se si utilizza AMD Ryzen™ AI Halo Developer Platform, AMD ROCm™ software e PyTorch sono preinstallati.

## Prerequisiti Linux

I seguenti pacchetti di sistema sono richiesti:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` è richiesto per creare `kernel-env`.
* `build-essential`, `gcc` e `g++` sono richiesti per le procedure dettagliate sulle estensioni C++.
* `amd-smi` viene utilizzato per i controlli di visibilità/utilizzo della GPU su Linux.

Gli esempi di estensioni C++ compilano moduli nativi `.so` da file `.cu` utilizzando il percorso `CUDAExtension` di PyTorch.

## Prerequisiti Windows

I runner Windows richiedono:

* Python disponibile tramite `python`
* Installare l'ultima versione: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) o [versione più recente](https://visualstudio.microsoft.com/vs/community/) con il carico di lavoro **Sviluppo desktop con C++**

L'ambiente C++ di Visual Studio deve fornire:
* `vcvars64.bat`
* `cl.exe`
* Percorsi di inclusione e libreria di Windows SDK

Gli esempi di estensioni C++ compilano moduli nativi `.pyd` da file `.cu` utilizzando il percorso `CUDAExtension` di PyTorch.