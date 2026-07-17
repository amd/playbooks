<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configuração da Plataforma

Este documento descreve as configurações de plataforma esperadas para executar este playbook.

## Aplicativos/Frameworks Necessários

### Windows/Linux

GAIA deve ser pré-instalado seguindo as instruções fornecidas no [Guia de Instalação do GAIA](../../dependencies/gaia.md).

Lemonade Server deve ser pré-instalado seguindo as instruções fornecidas no [Guia de Instalação do Lemonade](../../dependencies/lemonade.md).

## Modelos Necessários

### Windows/Linux

O Hardware Advisor Agent utiliza **Qwen3-Coder-30B** para raciocínio do agente. Este modelo é baixado automaticamente durante `gaia init`. Não são necessários downloads manuais de modelos.