<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente a partir do inglês e não foi revista por um humano. Pode conter erros, e determinadas instruções, comandos, transferências, disponibilidade de produtos ou outro conteúdo podem variar consoante o idioma ou a região. Em caso de qualquer inconsistência ou discrepância, prevalece a versão original em inglês do playbook.
<!-- auto-translated-disclaimer:end -->

# Configuração da Plataforma — Lemonade Local AI

Este documento descreve o software pré-instalado, os caminhos dos modelos e os pré-requisitos específicos da plataforma assumidos por este manual.

## Software Pré-Instalado

| Software | Versão | Finalidade |
|----------|---------|---------|
| Lemonade Server | Versão mais recente | Servidor LLM local com API compatível com OpenAI |
| Python | 3.10–3.13 | Necessário para o exemplo do cliente Python da OpenAI |

## Armazenamento de Modelos por Predefinição

Os modelos transferidos através do Lemonade são armazenados de acordo com a especificação do Hugging Face Hub:

| Plataforma | Caminho Predefinido |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Para alterar o local de armazenamento, defina a variável de ambiente `HF_HOME`.

## Requisitos de Hardware

| Destino de Hardware | Requisitos |
|----------------|-------------|
| **CPU** | Qualquer processador x86-64 moderno (AMD ou Intel) |
| **GPU (Vulkan)** | Qualquer GPU com suporte para o driver Vulkan |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000 series ou Radeon PRO W7000 series; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | Processador AMD Ryzen AI 300 series, Windows 11 |

## Requisitos de Rede

- É necessária ligação à Internet para a transferência inicial do modelo (1–25 GB, dependendo do modelo)
- Não é necessária ligação à Internet após a transferência dos modelos