<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente a partir do inglês e não foi revista por um humano. Pode conter erros, e alguns passos, comandos, transferências ou disponibilidade de produtos podem ser diferentes no seu idioma ou região. Se algo parecer incorreto, considere o playbook original em inglês como fonte fidedigna.
<!-- auto-translated-disclaimer:end -->

# Configuração da Plataforma

Este documento descreve as configurações de plataforma esperadas para executar este playbook.

## Aplicações/Frameworks Necessários

### Windows/Linux

O GAIA deve ser pré-instalado seguindo as instruções fornecidas no [Guia de Instalação do GAIA](../../dependencies/gaia.md).

O Lemonade Server deve ser pré-instalado seguindo as instruções fornecidas no [Guia de Instalação do Lemonade](../../dependencies/lemonade.md).

## Modelos Necessários

### Windows/Linux

O Hardware Advisor Agent utiliza o **Qwen3-Coder-30B** para o raciocínio do agente. Este modelo é transferido automaticamente durante `gaia init`. Não são necessárias transferências manuais de modelos.