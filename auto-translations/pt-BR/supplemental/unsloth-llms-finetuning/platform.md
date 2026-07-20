# Configuração da plataforma

Este documento descreve as configurações de plataforma esperadas para executar este playbook.

## Pré-requisitos

O PyTorch com suporte a ROCm já vem pré-instalado na AMD Ryzen™ AI Halo Developer Platform. Para todos os outros dispositivos, os usuários devem instalar manualmente o PyTorch com suporte a ROCm. Consulte a seção relevante para o seu sistema operacional:


### Windows

| Componente     | Versão         | Observações                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Pré-instalado na AMD Ryzen AI Halo Developer Platform; deve ser instalado manualmente em todos os outros dispositivos |


### Linux

| Componente     | Versão         | Observações                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Pré-instalado na AMD Ryzen AI Halo Developer Platform; deve ser instalado manualmente em todos os outros dispositivos |


## Modelos necessários

Os seguintes modelos foram testados e otimizados para sua plataforma:

| Modelo | Parâmetros | Tamanho | Local de download |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Baixar do HF

Os modelos serão baixados automaticamente para o diretório de cache do Hugging Face: `~/.cache/huggingface/hub/`

Garanta pelo menos **20 GB de espaço livre** para armazenamento dos modelos.

## Requisitos de rede

A configuração inicial requer acesso à internet para baixar os modelos do Hugging Face. Após o download, o playbook pode ser executado offline.

- Os downloads de modelos pela primeira vez podem levar de **5 a 10 minutos**, dependendo do tamanho do modelo e da velocidade da conexão
- Os modelos ficam armazenados em cache localmente e não precisam ser baixados novamente