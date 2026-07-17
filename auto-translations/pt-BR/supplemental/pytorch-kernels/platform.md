<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configuração da Plataforma

Este documento descreve a configuração esperada da plataforma para executar este playbook.

## Aplicativos / Frameworks Necessários

| Componente      | Configuração Esperada                | Observações                                                                  |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python com suporte a `venv`        | Usado para criar e ativar `kernel-env`                                       |
| ROCm Python SDK | Família de pacotes ROCm 7.13         | Instalado através do fluxo de dependências do playbook                       |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Necessário para `torch.cuda`, runtime HIP, compilação JIT e `CUDAExtension`  |
| Driver GPU      | Driver AMD GPU com suporte ROCm/HIP  | Necessário antes que o PyTorch possa detectar a AMD GPU                      |

> Observação: Se você estiver executando na AMD Ryzen™ AI Halo Developer Platform, o AMD ROCm™ software e o PyTorch já vêm pré-instalados.

## Pré-requisitos para Linux

Os seguintes pacotes de sistema são necessários:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` é necessário para criar `kernel-env`.
* `build-essential`, `gcc` e `g++` são necessários para os tutoriais de extensão C++.
* `amd-smi` é usado para verificações de visibilidade/utilização de GPU no Linux.

Os exemplos de extensão C++ compilam módulos `.so` nativos a partir de arquivos `.cu` usando o caminho `CUDAExtension` do PyTorch.

## Pré-requisitos para Windows

Os executores Windows requerem:

* Python disponível através de `python`
* Instale a versão mais recente: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) ou [mais recente](https://visualstudio.microsoft.com/vs/community/) com a carga de trabalho **Desenvolvimento para desktop com C++**

O ambiente C++ do Visual Studio deve fornecer:
* `vcvars64.bat`
* `cl.exe`
* Caminhos de inclusão e biblioteca do Windows SDK

Os exemplos de extensão C++ compilam módulos `.pyd` nativos a partir de arquivos `.cu` usando o caminho `CUDAExtension` do PyTorch.