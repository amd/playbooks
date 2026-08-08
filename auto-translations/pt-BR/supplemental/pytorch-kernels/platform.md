<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente do inglês e não foi revisada por um ser humano. Ela pode conter erros, e determinadas instruções, comandos, downloads, disponibilidade de produtos ou outros conteúdos podem variar de acordo com o idioma ou a região. Em caso de qualquer inconsistência ou divergência, a versão original em inglês do playbook prevalecerá.
<!-- auto-translated-disclaimer:end -->

# Configuração da Plataforma

Este documento descreve a configuração de plataforma esperada para executar este playbook.

## Aplicativos / Frameworks Necessários

| Componente       | Configuração Esperada               | Notas                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python com suporte a `venv`         | Usado para criar e ativar `kernel-env`                                     |
| ROCm Python SDK | Família de pacotes ROCm 7.13             | Instalado através do fluxo de dependências do playbook                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Necessário para `torch.cuda`, runtime HIP, compilação JIT e `CUDAExtension` |
| Driver de GPU      | Driver de GPU AMD com suporte a ROCm/HIP | Necessário antes que o PyTorch possa detectar a GPU AMD                               |

> Observação: Se você estiver executando na AMD Ryzen™ AI Halo Developer Platform, o software AMD ROCm™ e o PyTorch já vêm pré-instalados.

## Pré-requisitos do Linux

Os seguintes pacotes do sistema são necessários:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` é necessário para criar o `kernel-env`.
* `build-essential`, `gcc` e `g++` são necessários para os tutoriais de extensão em C++.
* `amd-smi` é usado para verificações de visibilidade/utilização de GPU no Linux.

Os exemplos de extensão em C++ compilam módulos `.so` nativos a partir de arquivos `.cu` usando o caminho `CUDAExtension` do PyTorch.

## Pré-requisitos do Windows

Os executores do Windows requerem:

* Python disponível através de `python`
* Instale a versão mais recente: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) ou [mais recente](https://visualstudio.microsoft.com/vs/community/) com a carga de trabalho **Desktop development with C++**

O ambiente C++ do Visual Studio deve fornecer:
* `vcvars64.bat`
* `cl.exe`
* Caminhos de inclusão e biblioteca do Windows SDK

Os exemplos de extensão em C++ compilam módulos `.pyd` nativos a partir de arquivos `.cu` usando o caminho `CUDAExtension` do PyTorch.