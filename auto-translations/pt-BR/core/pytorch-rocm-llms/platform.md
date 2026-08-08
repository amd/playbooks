<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente do inglês e não foi revisada por um ser humano. Ela pode conter erros, e determinadas instruções, comandos, downloads, disponibilidade de produtos ou outros conteúdos podem variar de acordo com o idioma ou a região. Em caso de qualquer inconsistência ou divergência, a versão original em inglês do playbook prevalecerá.
<!-- auto-translated-disclaimer:end -->

# Configuração de Plataforma

Este documento descreve as configurações de plataforma esperadas para executar este playbook.

## Pré-requisitos

O PyTorch com suporte a ROCm vem pré-instalado na AMD Ryzen™ AI Halo Developer Platform. Para todos os outros dispositivos, os usuários devem instalar manualmente o PyTorch com suporte a ROCm. Consulte a seção relevante para seu sistema operacional:

### Windows

| Componente     | Versão         | Observações                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 ou mais recente    | Pré-instalado na AMD Ryzen AI Halo Developer Platform; deve ser instalado manualmente em todos os outros dispositivos |

### Linux

| Componente     | Versão         | Observações                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 ou mais recente    | Pré-instalado na AMD Ryzen AI Halo Developer Platform; deve ser instalado manualmente em todos os outros dispositivos |

## Modelos Necessários

Os seguintes modelos foram testados e otimizados para sua plataforma:

| Modelo | Parâmetros | Tamanho | Local de Download |
|-------|------------|------|-------------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | Pré-instalado na AMD Ryzen AI Halo Developer Platform; deve ser instalado manualmente em todos os outros dispositivos |

Os modelos serão baixados automaticamente para o diretório de cache do Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Certifique-se de ter pelo menos **50 GB de espaço livre** para armazenamento dos modelos.

## Requisitos de Rede

A configuração inicial requer acesso à internet para baixar os modelos do Hugging Face. Após o download, o playbook pode ser executado offline.

- O download inicial dos modelos pode levar de **5 a 10 minutos**, dependendo do tamanho do modelo e da velocidade da conexão
- Os modelos são armazenados em cache localmente e não precisam ser baixados novamente