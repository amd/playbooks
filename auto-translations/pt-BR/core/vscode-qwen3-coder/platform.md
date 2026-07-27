<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente do inglês e não foi revisada por um humano. Ela pode conter erros, e algumas etapas, comandos, downloads ou a disponibilidade do produto podem variar de acordo com seu idioma ou região. Caso algo pareça incorreto, considere o playbook original em inglês como a fonte oficial.
<!-- auto-translated-disclaimer:end -->

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