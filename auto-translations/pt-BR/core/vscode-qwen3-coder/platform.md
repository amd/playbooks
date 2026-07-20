<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configuração da Plataforma

Este documento descreve as configurações de plataforma esperadas para a execução deste playbook.

## Windows

### Instalação do LM Studio

O LM Studio deve estar pré-instalado:

| Componente | Versão | Local |
|-----------|---------|----------|
| **LM Studio (Models + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Download do Modelo

Os seguintes modelos já devem estar presentes no diretório de modelos do LM Studio (`C:\Users\...\.lmstudio\models`):

| Tipo de Modelo | Quantização | Tamanho | Local |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### Instalação do LM Studio

Consulte lmstudio.md (dentro da pasta dependencies) para mais detalhes.

### Download do Modelo

Igual ao Windows.