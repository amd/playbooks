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

### Windows

| Componente | Versão | Notas |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Pré-instalado e disponível no PATH na AMD Ryzen™ AI Halo Developer Platform; deve ser instalado manualmente em todos os outros dispositivos |
| **Lemonade Server** | mais recente | Em execução em `http://localhost:13305/api/v1` |

### Linux

| Componente | Versão | Notas |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Pré-instalado e disponível no PATH na AMD Ryzen™ AI Halo Developer Platform; deve ser instalado manualmente em todos os outros dispositivos |
| **Lemonade Server** | mais recente | Em execução em `http://localhost:13305/api/v1` |


## Lemonade LLM

O servidor Lemonade deve estar em execução com o modelo adequado ao dispositivo carregado (consulte o README para o comando `lemonade run` do seu dispositivo):

| Dispositivo | Endpoint | Modelo |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |