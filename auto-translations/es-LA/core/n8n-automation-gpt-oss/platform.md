<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configuración de la Plataforma

Este documento describe las configuraciones de plataforma esperadas para ejecutar este playbook.

## Requisitos previos

### Windows

| Componente | Versión | Notas |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Preinstalado y disponible en PATH en la AMD Ryzen™ AI Halo Developer Platform; debe instalarse manualmente en todos los demás dispositivos |
| **Lemonade Server** | latest | En ejecución en `http://localhost:13305/api/v1` |

### Linux

| Componente | Versión | Notas |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Preinstalado y disponible en PATH en la AMD Ryzen™ AI Halo Developer Platform; debe instalarse manualmente en todos los demás dispositivos |
| **Lemonade Server** | latest | En ejecución en `http://localhost:13305/api/v1` |


## LLM de Lemonade

El servidor Lemonade debe estar en ejecución con el modelo apropiado para el dispositivo cargado (consulte el README para el comando `lemonade run` correspondiente a su dispositivo):

| Dispositivo | Endpoint | Modelo |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |