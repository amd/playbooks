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

## Aplicações/Frameworks Necessários

### Windows/Linux

- O **Lemonade Server** deve ser instalado seguindo o
  [guia de instalação do Lemonade](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 ou posterior** e `npm`, utilizados pela CLI `agent-canvas` e pelos servidores
  MCP lançados com `npx`.
- **uv**, o gestor de pacotes Python que o Agent Canvas utiliza para gerir o ambiente do
  servidor do agente. Instale-o a partir do
  [guia de instalação do uv](https://docs.astral.sh/uv/getting-started/installation/).

## Modelos Necessários

### Windows/Linux

O seguinte modelo deve estar disponível no Lemonade Server antes de iniciar o
playbook.

| Tipo de Modelo | ID do Modelo | Notas |
| --- | --- | --- |
| Modelo de chat GGUF | `Qwen3.6-35B-A3B-GGUF` | Servido pelo Lemonade Server em `http://127.0.0.1:13305/api/v1`. Utilize um modelo GGUF mais pequeno em dispositivos com menos de 32 GB de memória. |

Inicie o modelo com:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

## Credenciais Externas

Este playbook requer:

- Um token do GitHub com acesso de leitura ao repositório a ser resumido.
- Um token de bot do Slack com acesso de escrita `chat:write` e de leitura de canais.
- Um ID de equipa do Slack e o ID do canal do Slack de destino.