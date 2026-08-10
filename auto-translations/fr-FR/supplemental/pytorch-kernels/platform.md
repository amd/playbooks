<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduction automatique.** Cette page a été traduite automatiquement depuis l'anglais et n'a pas été relue par un traducteur humain. Elle peut contenir des erreurs, et certaines instructions, commandes, téléchargements, disponibilités de produits ou autres contenus peuvent varier selon la langue ou la région. En cas d'incohérence ou de divergence, la version originale en anglais du playbook fait foi et prévaut.
<!-- auto-translated-disclaimer:end -->

# Configuration de la plateforme

Ce document décrit la configuration de plateforme attendue pour l'exécution de ce playbook.

## Applications / Frameworks requis

| Composant       | Configuration attendue               | Remarques                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python avec prise en charge de `venv`         | Utilisé pour créer et activer `kernel-env`                                     |
| ROCm Python SDK | Famille de packages ROCm 7.13             | Installé via le flux de dépendances du playbook                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Requis pour `torch.cuda`, l'environnement d'exécution HIP, la compilation JIT et `CUDAExtension` |
| Pilote GPU      | Pilote GPU AMD avec prise en charge ROCm/HIP | Requis avant que PyTorch puisse détecter le GPU AMD                               |

> Remarque : Si vous utilisez la plateforme AMD Ryzen™ AI Halo Developer Platform, le logiciel AMD ROCm™ et PyTorch sont préinstallés.

## Prérequis Linux

Les packages système suivants sont requis :

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` est requis pour créer `kernel-env`.
* `build-essential`, `gcc`, et `g++` sont requis pour les tutoriels d'extension C++.
* `amd-smi` est utilisé pour les vérifications de visibilité/utilisation GPU sous Linux.

Les exemples d'extension C++ compilent des modules natifs `.so` à partir de fichiers `.cu` en utilisant le chemin `CUDAExtension` de PyTorch.

## Prérequis Windows

Les exécuteurs Windows nécessitent :

* Python disponible via `python`
* Installer la dernière version : [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) ou [version plus récente](https://visualstudio.microsoft.com/vs/community/) avec la charge de travail **Développement Desktop en C++**

L'environnement C++ de Visual Studio doit fournir :
* `vcvars64.bat`
* `cl.exe`
* Les chemins d'inclusion et de bibliothèques du Windows SDK

Les exemples d'extension C++ compilent des modules natifs `.pyd` à partir de fichiers `.cu` en utilisant le chemin `CUDAExtension` de PyTorch.