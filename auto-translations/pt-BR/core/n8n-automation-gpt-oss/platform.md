<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

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


## LLM do Lemonade

O servidor Lemonade deve estar em execução com o modelo apropriado para o dispositivo carregado (consulte o README para o comando `lemonade run` do seu dispositivo):

| Dispositivo | Endpoint | Modelo |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |