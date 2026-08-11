<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente do inglês e não foi revisada por um ser humano. Ela pode conter erros, e determinadas instruções, comandos, downloads, disponibilidade de produtos ou outros conteúdos podem variar de acordo com o idioma ou a região. Em caso de qualquer inconsistência ou divergência, a versão original em inglês do playbook prevalecerá.
<!-- auto-translated-disclaimer:end -->

# Configuração da Plataforma

Este documento descreve as configurações de plataforma esperadas para executar este playbook.

## Aplicativos/Frameworks Necessários

### Windows/Linux

- O **Lemonade Server** deve ser instalado seguindo o
  [guia de instalação do Lemonade](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 ou posterior** e `npm`, usados pela CLI do `agent-canvas`.
- **uv**, o gerenciador de pacotes Python que o Agent Canvas usa para gerenciar
  o ambiente do servidor de agentes. Instale-o a partir do
  [guia de instalação do uv](https://docs.astral.sh/uv/getting-started/installation/).

## Modelos Necessários

### Windows/Linux

O modelo a seguir deve estar disponível no Lemonade Server antes de iniciar o
playbook.

| Tipo de Modelo | ID do Modelo | Observações |
| --- | --- | --- |
| Modelo de chat GGUF | `Qwen3.6-35B-A3B-GGUF` | Servido pelo Lemonade Server em `http://127.0.0.1:13305/api/v1`. Use um modelo GGUF menor em dispositivos com menos de 32 GB de memória. |

Inicie o modelo com:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```
