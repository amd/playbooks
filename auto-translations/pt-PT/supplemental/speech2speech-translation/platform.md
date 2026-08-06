<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente a partir do inglês e não foi revista por um humano. Pode conter erros, e determinadas instruções, comandos, transferências, disponibilidade de produtos ou outro conteúdo podem variar consoante o idioma ou a região. Em caso de qualquer inconsistência ou discrepância, prevalece a versão original em inglês do playbook.
<!-- auto-translated-disclaimer:end -->

# Configuração da Plataforma

Este documento descreve as configurações de plataforma esperadas para executar este playbook.

## Pré-requisitos

O PyTorch com suporte a ROCm vem pré-instalado na AMD Ryzen™ AI Halo Developer Platform. Para todos os outros dispositivos, os utilizadores devem instalar manualmente o PyTorch com suporte a ROCm. Consulte a secção relevante para o seu sistema operativo:

### Windows

| Componente     | Versão         | Notas                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 ou mais recente    | Pré-instalado na AMD Ryzen AI Halo Developer Platform; deve ser instalado manualmente em todos os outros dispositivos |

### Linux

| Componente     | Versão         | Notas                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 ou mais recente    | Pré-instalado na AMD Ryzen AI Halo Developer Platform; deve ser instalado manualmente em todos os outros dispositivos |

## Modelos Necessários

Os seguintes modelos foram testados e otimizados para a sua plataforma:

| Modelo | Parâmetros | Tamanho | Local de Download |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2.3B | ~10GB | Pré-instalado na AMD Ryzen AI Halo Developer Platform; deve ser instalado manualmente em todos os outros dispositivos |

Os modelos serão automaticamente transferidos para o diretório de cache do Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Certifique-se de que existe pelo menos **20 GB de espaço livre** para o armazenamento de modelos.

## Requisitos de Rede

A configuração inicial requer acesso à internet para transferir modelos do Hugging Face. Após a transferência, o playbook pode ser executado offline.

- As primeiras transferências de modelos podem demorar **5 a 10 minutos**, dependendo do tamanho do modelo e da velocidade da ligação
- Os modelos são guardados em cache localmente e não precisam de ser transferidos novamente