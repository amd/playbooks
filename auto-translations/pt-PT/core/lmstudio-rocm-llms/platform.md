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

## Windows

### Instalação do LM Studio

O LM Studio deve estar pré-instalado:

| Componente | Versão | Localização |
|-----------|---------|----------|
| **LM Studio (Modelos + Misc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Programa)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Descarregamento do Modelo

Os seguintes modelos já devem estar presentes no diretório de modelos do LM Studio (`C:\Users\...\.lmstudio\models`):

| Dispositivo | Tipo de Modelo | Quantização | Tamanho (GB) | Localização |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### Instalação do LM Studio

Consulte [lmstudio.md](../../dependencies/lmstudio.md) para mais detalhes.

### Descarregamento do Modelo

Igual ao Windows.