<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente a partir do inglês e não foi revista por um humano. Pode conter erros, e determinadas instruções, comandos, transferências, disponibilidade de produtos ou outro conteúdo podem variar consoante o idioma ou a região. Em caso de qualquer inconsistência ou discrepância, prevalece a versão original em inglês do playbook.
<!-- auto-translated-disclaimer:end -->

# Configuração da Plataforma

Este documento descreve as configurações de plataforma esperadas para executar este manual de instruções.

## Windows

### Instalação do LM Studio

O LM Studio deve estar pré-instalado:

| Componente | Versão | Localização |
|-----------|---------|----------|
| **LM Studio (Modelos + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Programa)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Transferência do Modelo

Os seguintes modelos já deverão estar presentes na diretoria de modelos do LM Studio (`C:\Users\...\.lmstudio\models`):

| Tipo de Modelo | Quantização | Tamanho | Localização |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### Instalação do LM Studio

Consulte lmstudio.md (dentro da pasta dependencies) para mais detalhes.

### Transferência do Modelo

Igual ao Windows.