<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduzione automatica.** Questa pagina è stata tradotta automaticamente dall'inglese e non è stata revisionata da una persona. Potrebbe contenere errori e alcune istruzioni, comandi, download, disponibilità dei prodotti o altri contenuti potrebbero variare in base alla lingua o alla regione. In caso di incongruenza o discrepanza, prevale la versione originale in lingua inglese del playbook.
<!-- auto-translated-disclaimer:end -->

# Configurazione della piattaforma

Questo documento descrive la configurazione della piattaforma prevista per l'esecuzione di questo playbook.

## App/framework richiesti

| Componente       | Configurazione prevista               | Note                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python con supporto `venv`         | Usato per creare e attivare `kernel-env`                                     |
| ROCm Python SDK | Famiglia di pacchetti ROCm 7.13             | Installato tramite il flusso di dipendenze del playbook                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Richiesto per `torch.cuda`, runtime HIP, compilazione JIT e `CUDAExtension` |
| Driver GPU      | Driver GPU AMD con supporto ROCm/HIP | Richiesto prima che PyTorch possa rilevare la GPU AMD                               |

> Nota: se stai utilizzando AMD Ryzen™ AI Halo Developer Platform, il software AMD ROCm™ e PyTorch sono preinstallati.

## Prerequisiti Linux

Sono richiesti i seguenti pacchetti di sistema:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` è richiesto per creare `kernel-env`.
* `build-essential`, `gcc` e `g++` sono richiesti per le guide dettagliate sulle estensioni C++.
* `amd-smi` viene utilizzato per i controlli di visibilità/utilizzo della GPU su Linux.

Gli esempi di estensione C++ compilano moduli nativi `.so` da file `.cu` utilizzando il percorso `CUDAExtension` di PyTorch.

## Prerequisiti Windows

I runner Windows richiedono:

* Python disponibile tramite `python`
* Installare l'ultima versione di: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) o [versioni più recenti](https://visualstudio.microsoft.com/vs/community/) con il carico di lavoro **Sviluppo di applicazioni desktop con C++**

L'ambiente C++ di Visual Studio deve fornire:
* `vcvars64.bat`
* `cl.exe`
* Percorsi di inclusione e librerie del Windows SDK

Gli esempi di estensione C++ compilano moduli nativi `.pyd` da file `.cu` utilizzando il percorso `CUDAExtension` di PyTorch.