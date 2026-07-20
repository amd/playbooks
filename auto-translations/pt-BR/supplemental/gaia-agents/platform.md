<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configuração da Plataforma

Este documento descreve as configurações de plataforma esperadas para executar este playbook.

## Aplicativos/Frameworks Necessários

### Windows/Linux

O GAIA deve estar pré-instalado seguindo as instruções fornecidas no [Guia de Instalação do GAIA](../../dependencies/gaia.md).

O Lemonade Server deve estar pré-instalado seguindo as instruções fornecidas no [Guia de Instalação do Lemonade](../../dependencies/lemonade.md).

## Modelos Necessários

### Windows/Linux

O Hardware Advisor Agent usa o **Qwen3-Coder-30B** para o raciocínio do agente. Esse modelo é baixado automaticamente durante o `gaia init`. Não é necessário baixar modelos manualmente.