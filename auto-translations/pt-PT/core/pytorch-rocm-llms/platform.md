<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente a partir do inglês e não foi revista por um humano. Pode conter erros, e determinadas instruções, comandos, transferências, disponibilidade de produtos ou outro conteúdo podem variar consoante o idioma ou a região. Em caso de qualquer inconsistência ou discrepância, prevalece a versão original em inglês do playbook.
<!-- auto-translated-disclaimer:end -->

# Configuração da Plataforma

Este documento descreve as configurações de plataforma esperadas para executar este manual de instruções.

## Pré-requisitos

O PyTorch com suporte para ROCm já vem pré-instalado na AMD Ryzen™ AI Halo Developer Platform. Para todos os outros dispositivos, os utilizadores devem instalar manualmente o PyTorch com suporte para ROCm. Consulte a secção relevante para o seu sistema operativo:

### Windows

| Componente     | Versão         | Notas                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 ou mais recente    | Pré-instalado na AMD Ryzen AI Halo Developer Platform; deve ser instalado manualmente em todos os outros dispositivos |

### Linux

| Componente     | Versão         | Notas                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 ou mais recente    | Pré-instalado na AMD Ryzen AI Halo Developer Platform; deve ser instalado manualmente em todos os outros dispositivos |

## Modelos Necessários

Os seguintes modelos foram testados e otimizados para a sua plataforma:

| Modelo | Parâmetros | Tamanho | Localização de Transferência |
|-------|------------|------|-------------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | Pré-instalado na AMD Ryzen AI Halo Developer Platform; deve ser instalado manualmente em todos os outros dispositivos |

Os modelos serão transferidos automaticamente para o diretório de cache do Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Garanta pelo menos **50 GB de espaço livre** para o armazenamento dos modelos.

## Requisitos de Rede

A configuração inicial requer acesso à internet para transferir os modelos a partir do Hugging Face. Após a transferência, o manual de instruções pode ser executado offline.

- As transferências iniciais dos modelos podem demorar **5 a 10 minutos**, dependendo do tamanho do modelo e da velocidade da ligação
- Os modelos ficam guardados em cache localmente e não precisam de ser transferidos novamente