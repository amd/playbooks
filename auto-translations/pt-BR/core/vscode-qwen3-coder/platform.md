<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configuração da Plataforma

Este documento descreve as configurações de plataforma esperadas para executar este playbook.

## Windows

### Instalação do LM Studio

O LM Studio deve estar pré-instalado:

| Componente | Versão | Localização |
|-----------|---------|----------|
| **LM Studio (Modelos + Misc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Programa)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Download de Modelos

Os seguintes modelos já devem estar presentes no diretório de modelos do LM Studio (`C:\Users\...\.lmstudio\models`):

| Tipo de Modelo | Quantização | Tamanho | Localização |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18,2 GB | `models\lmstudio-community` |

---

## Linux

### Instalação do LM Studio

Consulte lmstudio.md (dentro da pasta de dependências) para mais detalhes.

### Download de Modelos

Mesmo que no Windows.