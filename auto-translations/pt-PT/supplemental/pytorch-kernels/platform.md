<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente a partir do inglês e não foi revista por um humano. Pode conter erros, e determinadas instruções, comandos, transferências, disponibilidade de produtos ou outro conteúdo podem variar consoante o idioma ou a região. Em caso de qualquer inconsistência ou discrepância, prevalece a versão original em inglês do playbook.
<!-- auto-translated-disclaimer:end -->

# Configuração da Plataforma

Este documento descreve a configuração de plataforma esperada para executar este playbook.

## Aplicações / Frameworks Necessários

| Componente       | Configuração Esperada               | Notas                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python com suporte para `venv`         | Utilizado para criar e ativar `kernel-env`                                     |
| ROCm Python SDK | Família de pacotes ROCm 7.13             | Instalado através do fluxo de dependências do playbook                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Necessário para `torch.cuda`, runtime HIP, compilação JIT e `CUDAExtension` |
| Controlador GPU      | Controlador de GPU AMD com suporte para ROCm/HIP | Necessário antes que o PyTorch possa detetar a GPU AMD                               |

> Nota: Se estiver a executar na AMD Ryzen™ AI Halo Developer Platform, o software AMD ROCm™ e o PyTorch já vêm pré-instalados.

## Pré-requisitos para Linux

São necessários os seguintes pacotes de sistema:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` é necessário para criar `kernel-env`.
* `build-essential`, `gcc` e `g++` são necessários para os tutoriais de extensão C++.
* `amd-smi` é utilizado para verificações de visibilidade/utilização da GPU no Linux.

Os exemplos de extensão C++ constroem módulos `.so` nativos a partir de ficheiros `.cu` utilizando o percurso `CUDAExtension` do PyTorch.

## Pré-requisitos para Windows

Os executores Windows requerem:

* Python disponível através de `python`
* Instalar a versão mais recente: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) ou [mais recente](https://visualstudio.microsoft.com/vs/community/) com a carga de trabalho **Desenvolvimento para desktop com C++**

O ambiente C++ do Visual Studio deve fornecer:
* `vcvars64.bat`
* `cl.exe`
* Caminhos de inclusão e biblioteca do Windows SDK

Os exemplos de extensão C++ constroem módulos `.pyd` nativos a partir de ficheiros `.cu` utilizando o percurso `CUDAExtension` do PyTorch.