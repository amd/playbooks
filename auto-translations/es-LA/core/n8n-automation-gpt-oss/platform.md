<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducción automática.** Esta página fue traducida automáticamente del inglés y no ha sido revisada por un humano. Puede contener errores, y ciertas instrucciones, comandos, descargas, disponibilidad de productos u otro contenido pueden variar según el idioma o la región. En caso de cualquier incoherencia o discrepancia, la versión original en inglés del playbook prevalecerá y será la que rija.
<!-- auto-translated-disclaimer:end -->

# Configuración de la plataforma

Este documento describe las configuraciones de plataforma esperadas para ejecutar este playbook.

## Requisitos previos

### Windows

| Componente | Versión | Notas |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Preinstalado y disponible en PATH en la AMD Ryzen™ AI Halo Developer Platform; debe instalarse manualmente en todos los demás dispositivos |
| **Lemonade Server** | latest | Ejecutándose en `http://localhost:13305/api/v1` |

### Linux

| Componente | Versión | Notas |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Preinstalado y disponible en PATH en la AMD Ryzen™ AI Halo Developer Platform; debe instalarse manualmente en todos los demás dispositivos |
| **Lemonade Server** | latest | Ejecutándose en `http://localhost:13305/api/v1` |


## Lemonade LLM

El servidor Lemonade debe estar ejecutándose con el modelo adecuado para el dispositivo cargado (consulte el README para conocer el comando `lemonade run` correspondiente a su dispositivo):

| Dispositivo | Endpoint | Modelo |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |