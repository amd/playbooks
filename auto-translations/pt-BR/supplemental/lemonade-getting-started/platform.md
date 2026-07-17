<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configuração de Plataforma — Lemonade Local AI

Este documento descreve o software pré-instalado, os caminhos de modelos e os pré-requisitos específicos de plataforma assumidos por este playbook.

## Software Pré-Instalado

| Software | Versão | Finalidade |
|----------|---------|---------|
| Lemonade Server | Versão mais recente | Servidor LLM local com API compatível com OpenAI |
| Python | 3.10–3.13 | Necessário para o exemplo de cliente OpenAI em Python |

## Armazenamento Padrão de Modelos

Os modelos baixados pelo Lemonade são armazenados usando a especificação do Hugging Face Hub:

| Plataforma | Caminho Padrão |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

Para alterar o local de armazenamento, defina a variável de ambiente `HF_HOME`.

## Requisitos de Hardware

| Alvo de Hardware | Requisitos |
|----------------|-------------|
| **CPU** | Qualquer processador x86-64 moderno (AMD ou Intel) |
| **GPU (Vulkan)** | Qualquer GPU com suporte a driver Vulkan |
| **GPU (ROCm)** | AMD Radeon RX série 7000/9000 ou Radeon PRO W7000 series; AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | Processador AMD Ryzen AI série 300, Windows 11 |

## Requisitos de Rede

- Conexão com a internet necessária para o download inicial do modelo (1–25 GB dependendo do modelo)
- Sem necessidade de internet após o download dos modelos