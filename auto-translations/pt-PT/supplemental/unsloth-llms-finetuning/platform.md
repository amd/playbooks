<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente a partir do inglês e não foi revista por um humano. Pode conter erros, e determinadas instruções, comandos, transferências, disponibilidade de produtos ou outro conteúdo podem variar consoante o idioma ou a região. Em caso de qualquer inconsistência ou discrepância, prevalece a versão original em inglês do playbook.
<!-- auto-translated-disclaimer:end -->

# Configuração da Plataforma

Este documento descreve as configurações de plataforma esperadas para a execução deste playbook.

## Pré-requisitos

O PyTorch com suporte ROCm vem pré-instalado na AMD Ryzen™ AI Halo Developer Platform. Para todos os outros dispositivos, os utilizadores devem instalar manualmente o PyTorch com suporte ROCm. Consulte a secção relevante para o seu sistema operativo:


### Windows

| Componente     | Versão         | Notas                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Pré-instalado na AMD Ryzen AI Halo Developer Platform; deve ser instalado manualmente em todos os outros dispositivos |


### Linux

| Componente     | Versão         | Notas                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Pré-instalado na AMD Ryzen AI Halo Developer Platform; deve ser instalado manualmente em todos os outros dispositivos |


## Modelos Necessários

Os seguintes modelos foram testados e otimizados para a sua plataforma:

| Modelo | Parâmetros | Tamanho | Localização de Download |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Descarregar do HF

Os modelos serão descarregados automaticamente para o diretório de cache do Hugging Face: `~/.cache/huggingface/hub/`

Certifique-se de que dispõe de, pelo menos, **20 GB de espaço livre** para armazenamento de modelos.

## Requisitos de Rede

A configuração inicial requer acesso à internet para descarregar modelos do Hugging Face. Após o download, o playbook pode ser executado offline.

- Os primeiros downloads de modelos podem demorar **5 a 10 minutos**, dependendo do tamanho do modelo e da velocidade da ligação
- Os modelos ficam guardados em cache localmente e não precisam de ser descarregados novamente