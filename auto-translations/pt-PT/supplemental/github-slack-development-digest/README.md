<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente a partir do inglês e não foi revista por um humano. Pode conter erros, e determinadas instruções, comandos, transferências, disponibilidade de produtos ou outro conteúdo podem variar consoante o idioma ou a região. Em caso de qualquer inconsistência ou discrepância, prevalece a versão original em inglês do playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Visão Geral

Os programadores gastam muito tempo em pequenos ciclos recorrentes: rever pull requests etiquetados, responder a comentários no GitHub, triar novos issues, transformar tópicos do Slack em notas de standup ou acompanhamentos de incidentes, e acompanhar sinais de lançamento ou investigação. Cada ciclo é familiar, mas ainda assim requer discernimento: reunir o contexto certo, decidir o que importa, e publicar uma atualização clara onde a equipa já trabalha.

As [automações OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) transformam esses ciclos em conversas de agente agendadas ou acionadas por eventos: execuções em que um agente de software de IA pode ler contexto, chamar ferramentas e produzir uma atualização. Os modelos de automação partilhados no catálogo de extensões OpenHands seguem este padrão para revisão de pull requests do GitHub, monitorização de repositórios, triagem de issues do Linear, retrospetivas de incidentes, resumos diários do Slack e resumos de investigação: uma automação é ativada, utiliza integrações configuradas como o GitHub ou o Slack para obter contexto, raciocina sobre esse contexto com um modelo de linguagem alargado (LLM) e escreve de volta um resultado.

O [Agent Canvas](https://github.com/OpenHands/agent-canvas) é o plano de controlo local para construir e testar essas automações. Neste manual, executa um OpenHands Agent Server, o processo de backend que executa conversas de agente, e liga o agente a serviços externos como o GitHub e o Slack.

Para manter o fluxo de trabalho no seu sistema AMD, o agente comunica com um modelo local servido pelo Lemonade Server. O Lemonade expõe esse modelo através de uma API compatível com OpenAI, pelo que o Agent Canvas o pode configurar como um endpoint remoto do tipo OpenAI, enquanto o modelo, o prompt e o contexto do fluxo de trabalho permanecem locais.

Neste manual, irá construir uma automação concreta: um resumo agendado de desenvolvimento do GitHub para o Slack. Utiliza o GitHub para inspecionar a atividade recente do repositório, o Slack para publicar o resumo, chamadas à API do Agent Canvas para configurar e testar a automação, e o Lemonade para executar o LLM localmente.

![Diagrama de arquitetura mostrando o GitHub MCP, a automação OpenHands, o Lemonade Server e o Slack MCP](assets/00-architecture-overview.png)

## O Que Irá Aprender

- Como iniciar o Lemonade Server e verificar se um modelo local responde a pedidos de chat
- Como iniciar o Agent Canvas e apontar o seu Agent Server para um LLM local
- Como instalar servidores GitHub e Slack Model Context Protocol (MCP) através da API do Agent Server
- Como criar e despoletar uma automação OpenHands agendada que publica um resumo de desenvolvimento no Slack
- Como resolver as falhas mais comuns de modelo local e de automação

## Conceitos Fundamentais

| Conceito | O que é | Onde se encaixa neste manual |
| --- | --- | --- |
| Lemonade Server | Uma plataforma local de serving de LLM criada para hardware AMD que expõe uma API compatível com OpenAI. Os seus dados nunca saem da sua máquina. | Executa o modelo que alimenta o agente. |
| OpenHands Agent Server | O processo de backend que executa conversas de agente OpenHands. | Aloja o agente, o seu perfil de LLM e os seus servidores MCP. |
| Agent Canvas | O plano de controlo local para o OpenHands que executa o Agent Server e uma interface para inspecionar execuções de agente. | Inicia os backends e fornece a API que invoca. |
| Servidor MCP | Um servidor Model Context Protocol que fornece a um agente ferramentas para um serviço externo como o GitHub ou o Slack. | Permite ao agente ler o GitHub e escrever no Slack. |
| Automação OpenHands | Uma conversa de agente agendada ou acionada por eventos que obtém contexto, raciocina sobre ele e escreve um resultado algures. | O resumo do GitHub para o Slack que constrói aqui. |

<!-- @device:stx,krk -->
> [!NOTE]
> Os fluxos de trabalho de agentes de codificação beneficiam de um modelo maior e de uma janela de contexto maior. Utilize pelo menos 32 GB de memória de sistema, e prefira 64 GB ou mais para modelos GGUF maiores.
<!-- @device:end -->

## Pré-requisitos

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Precisa de:

- Lemonade Server instalado seguindo o guia de instalação padrão do [Lemonade](https://lemonade-server.ai/docs/guide/install/).
- Node.js 22.12 ou posterior e `npm`, utilizados para instalar a CLI publicada do Agent Canvas e executar servidores MCP com `npx`.
- Um pacote `@openhands/agent-canvas` publicado recente, com definições de agente orientadas por schema, `LLMSummarizingCondenserSettings.max_tokens`, e suporte para `custom_tokenizer` do LLM.
- O pacote Python `transformers` disponível no ambiente do Agent Server. É necessário para a contagem de tokens de modelos de chat quando `custom_tokenizer` está definido.
- Um token do GitHub com acesso de leitura ao repositório que pretende resumir.
- Um token de bot do Slack (`xoxb-...`) com `chat:write` e acesso de leitura a canais.
- Um ID de equipa do Slack (`T...`).
- Um ID de canal do Slack (`C...`) onde o resumo deve ser publicado.

Convide a aplicação Slack para o canal de destino antes de testar a automação.

## Variáveis Utilizadas Neste Manual

<!-- @device:halo,halo_box,stx,krk -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
export OPENHANDS_LLM_MODEL="openai/${LEMONADE_MODEL}"
export QWEN_CUSTOM_TOKENIZER="Qwen/Qwen3.6-35B-A3B"
export CONDENSER_MAX_TOKENS="56000"
```

Os seguintes valores são introduzidos na interface do Agent Canvas em passos posteriores. Defina-os aqui para que os possa copiar mais tarde:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

Utilize um valor explícito `owner/repo` para `GITHUB_REPO_FILTER`. Wildcards alargados de organização podem devolver demasiado contexto MCP para modelos locais.

## 1. Iniciar o Lemonade Server

Inicie o modelo a partir da CLI do Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

O Lemonade expõe uma API compatível com OpenAI em:

```text
http://127.0.0.1:13305/api/v1
```

Opcional: se o Agent Canvas ou o executor de automação não estiverem na mesma máquina, publique o endpoint do Lemonade através de um túnel seguro e utilize o URL HTTPS como o URL base do LLM:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Verificar o Modelo Local

Confirme que o Lemonade consegue servir o modelo selecionado:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Depois, envie um pequeno pedido de chat:

```bash
curl -sS "${LEMONADE_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"${LEMONADE_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

Se isto devolver um array `choices`, o Lemonade está pronto para o Agent Canvas.
## 3. Iniciar o Agent Canvas

Instale o pacote publicado do Agent Canvas e inicie a stack completa:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Se a instalação global do npm falhar com um erro de permissões, consulte a
entrada de resolução de problemas de permissões do npm abaixo.

Por predefinição, o Agent Canvas inicia em `http://localhost:8000`. Abra esse
URL no seu navegador. O backend local predefinido deverá aparecer como
saudável no ecrã principal.

O comando `agent-canvas` inicia o agent server, o backend de automação e o
frontend web em conjunto. Só precisa deste comando para executar o OpenHands
localmente. O resto deste guia configura tudo através da UI do Agent Canvas
no seu navegador.

## 4. Configurar o LLM Local na UI

No primeiro arranque, o Agent Canvas abre um fluxo de introdução. Nesse fluxo:

1. Mantenha **OpenHands** selecionado como o agente e clique em **Next**.
2. Em **Set up your LLM**, selecione **Advanced**.
3. Mantenha **Authentication** definido como **API key**.
4. Defina **Custom Model** para o valor de `OPENHANDS_LLM_MODEL`,
   `openai/Qwen3.6-35B-A3B-GGUF`.
5. Defina **Base URL** para `http://127.0.0.1:13305/api/v1`.
6. Em **API Key**, introduza um valor de substituição não vazio, como
   `lemonade-local`. O Lemonade não requer uma chave real, mas o cliente
   OpenHands precisa de um valor para enviar.

Os campos de ligação devem ter este aspeto. O campo de chave da API está
ocultado pela UI.

![Definições avançadas de LLM no primeiro arranque do Agent Canvas com o modelo Lemonade e o URL base local](assets/01-llm-advanced-settings.png)

Em seguida, selecione **All** e defina os campos adicionais do modelo local:

1. Percorra até **Custom Tokenizer** e defina-o para `Qwen/Qwen3.6-35B-A3B`.
2. Percorra até **LiteLLM Extra Body** e defina-o para
   `{"enable_thinking": true}`.
3. Clique em **Next**.

![Separador All de LLM no primeiro arranque do Agent Canvas com o tokenizador personalizado Qwen](assets/02-llm-all-tokenizer-settings.png)

![Separador All de LLM no primeiro arranque do Agent Canvas com o corpo extra do LiteLLM configurado](assets/03-llm-all-extra-body-settings.png)

As definições do LLM devem mostrar:

| Campo | Valor |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

O prefixo `openai/` indica ao LiteLLM para usar formatação de pedidos
compatível com OpenAI contra o endpoint Lemonade. O tokenizador personalizado
é o tokenizador original do Hugging Face para o modelo GGUF; permite ao
OpenHands contar os mesmos tokens de modelo de chat que o servidor local do
modelo vê. O formulário atual de LLM de primeiro arranque não mostra
definições de condensador. Se a sua compilação do Agent Canvas expuser mais
tarde definições de condensador em **Settings > LLM**, use `llm_summarizing` e
defina o máximo de tokens abaixo da janela de contexto do Lemonade, como
`56000`.

## 5. Instalar Servidores MCP de GitHub e Slack

Na UI do Agent Canvas, abra **Customize** (ou **Settings > MCP**) para
adicionar os servidores MCP que dão ao agente ferramentas para GitHub e Slack.
Os valores de token são enviados apenas para o seu Agent Server local e são
persistidos como definições encriptadas.

### Servidor MCP do GitHub

Adicione um novo servidor MCP com estas definições:

| Campo | Valor |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = o seu token do GitHub |

Use um token do GitHub com acesso de leitura ao repositório que pretende
resumir.

### Servidor MCP do Slack

Adicione um segundo servidor MCP com estas definições:

| Campo | Valor |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = o ID do seu canal de resumo |

Defina `SLACK_CHANNEL_IDS` para o ID do canal de resumo (o mesmo valor que
`SLACK_DIGEST_CHANNEL`) para que o agente não precise de percorrer todos os
canais do Slack.

Depois de adicionar ambos os servidores, use o botão **Test** em cada um para
confirmar que estabelece ligação e anuncia ferramentas. O servidor do GitHub
deve listar ferramentas do GitHub, e o servidor do Slack deve listar
ferramentas do Slack.

![Página MCP do Agent Canvas com os servidores GitHub e Slack instalados](assets/04-mcp-servers-installed.png)

## 6. Criar a Automação de Resumo (Digest)

Na UI do Agent Canvas, abra a página **Automations** e crie uma nova
automação:

1. Escolha **Create automation** e selecione o tipo **Prompt preset**.
2. Defina o **Name** para `GitHub Development Digest to Slack`.
3. Defina o **Prompt** para o seguinte texto, substituindo os valores de
   substituição do repositório e do canal pelos seus valores:

   ```text
   Use the GitHub MCP server for exactly one repository: your-org/your-repo.
   Inspect recent development activity since the previous weekday, including
   merged pull requests, newly opened or reopened pull requests, notable
   commits pushed to main or release branches, new issues, important issue
   updates, releases, risks, blockers, and review requests. Keep GitHub
   lookups small: inspect the latest 3 to 5 commits, pull requests, issues,
   and releases. Use the Slack MCP server to post directly to channel ID
   C0123456789. Keep the Slack message concise: title with date range, 3 to 7
   bullets, links back to GitHub, and a Needs attention section only if
   needed. End with: This digest was generated by an AI agent (OpenHands) on
   behalf of the user. Do not include secrets, raw tokens, private
   environment variables, or unrelated Slack messages.
   ```

4. Defina o **Trigger** para **Cron** com o horário `0 9 * * 1-5` (9h em dias
   úteis) e defina o **Timezone** para o seu fuso horário, por exemplo
   `America/New_York`.
5. Defina o **Timeout** para `900` segundos.
6. Guarde a automação.

A página de detalhes da automação mostra a nova automação com o seu trigger
cron e o ponto de entrada de prompt preset gerado.

![Página de detalhes da automação do Agent Canvas após a criação](assets/05-automation-created.png)
## 7. Testar a Automação

A partir da página de detalhes da automação na interface do Agent Canvas:

1. Clique em **Run now** (ou **Dispatch**) para executar a automação uma vez, imediatamente.
2. Observe a lista de execuções na mesma página. A execução mais recente deverá
   transitar para `COMPLETED`.
3. Abra o seu canal do Slack de destino. Deverá conter o resumo gerado.

Não precisa de esperar que o agendamento cron seja acionado—**Run now** aciona
uma execução a pedido para que possa confirmar que o prompt, as ligações MCP e
a publicação no Slack funcionam antes de depender do agendamento.

![Execução de automação do Agent Canvas concluída com sucesso](assets/06-automation-run-completed.png)

![Canal do Slack a mostrar o resumo do OpenHands gerado](assets/07-slackbot-message.png)

## Resolução de Problemas

- **O Lemonade está em baixo:** reinicie-o com o comando
  `lemonade run "${LEMONADE_MODEL}"` do passo 1 e, em seguida, execute
  novamente a verificação de funcionamento.
- **`npm install -g` falha com um erro de permissões:** no Linux ou WSL,
  configure um diretório global npm pertencente ao utilizador, adicione-o ao
  ficheiro de arranque da sua shell e, em seguida, instale novamente o Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  Se utilizar `zsh`, adicione a mesma linha `export PATH=...` ao `~/.zshrc`
  em vez de ao `~/.bashrc`.
- **O Agent Canvas rejeita as definições do LLM após definir `custom_tokenizer`:**
  instale `transformers` no ambiente Python do Agent Server, reinicie o Agent
  Canvas se necessário e volte a tentar guardar as definições do LLM. O OpenHands
  requer o Transformers para carregar o modelo de chat do tokenizador quando
  `custom_tokenizer` está definido.
- **O Agent Canvas não consegue alcançar o Lemonade:** verifique
  `curl -fsS "${LEMONADE_BASE_URL}/health"` e confirme que o URL base indicado
  no formulário de LLM da primeira utilização ou em **Settings > LLM**
  corresponde ao ponto final local em execução ou ao túnel HTTPS.
- **As definições do LLM não foram guardadas:** certifique-se de que clicou em
  **Next** depois de introduzir os valores. Reabra **Settings > LLM** para
  confirmar que os valores foram persistidos.
- **O GitHub MCP não consegue ver repositórios privados:** confirme que o token
  do GitHub tem acesso de leitura ao repositório de destino e que o botão
  **Test** do MCP em **Customize** anuncia as ferramentas do GitHub.
- **O Slack consegue ler canais mas não consegue publicar:** convide a
  aplicação Slack para o canal de destino e confirme que o bot tem `chat:write`.
- **A automação lista demasiados canais do Slack:** utilize um ID de canal do
  Slack e defina `SLACK_CHANNEL_IDS` no servidor MCP do Slack em **Customize**.
- **A execução da automação falha ou excede o contexto:** confirme que o
  Lemonade foi iniciado com `ctx_size=65536`, confirme que o LLM do OpenHands
  tem `custom_tokenizer` definido e utilize um repositório explícito com os
  conjuntos de resultados do GitHub limitados a 3 a 5 itens. Se a sua versão do
  Agent Canvas expuser definições de condensador, defina o máximo de tokens do
  condensador abaixo da janela de contexto do Lemonade.

## Próximos Passos

- Adicione um resumo semanal apenas de lançamentos.
- Adicione uma automação acionada por eventos do GitHub para alertas mais
  rápidos de PR ou push.
- Encaminhe o mesmo resumo para o Notion, o Linear ou outra ferramenta
  suportada por MCP.

## Recursos

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Documentação do Lemonade Server](https://lemonade-server.ai/docs)
- [Repositório de extensões do OpenHands](https://github.com/OpenHands/extensions)
- [Servidores do Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Pacote MCP do Slack](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)