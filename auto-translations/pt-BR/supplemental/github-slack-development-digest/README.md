<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente do inglês e não foi revisada por um ser humano. Ela pode conter erros, e determinadas instruções, comandos, downloads, disponibilidade de produtos ou outros conteúdos podem variar de acordo com o idioma ou a região. Em caso de qualquer inconsistência ou divergência, a versão original em inglês do playbook prevalecerá.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Visão Geral

Desenvolvedores gastam muito tempo em pequenos ciclos recorrentes: revisar
pull requests etiquetados, responder comentários no GitHub, triar novas issues,
transformar threads do Slack em notas de standup ou acompanhamentos de incidentes,
e acompanhar sinais de lançamento ou pesquisa. Cada ciclo é familiar, mas ainda
requer julgamento: reunir o contexto certo, decidir o que importa e publicar uma
atualização clara onde a equipe já trabalha.

As [automações do OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview)
transformam esses ciclos em conversas de agente agendadas ou acionadas por eventos:
execuções em que um agente de software de IA pode ler contexto, chamar ferramentas
e produzir uma atualização. Os modelos de automação compartilhados no catálogo de
extensões do OpenHands seguem esse padrão para revisão de pull requests do GitHub,
monitoramento de repositórios, triagem de issues do Linear, retrospectivas de
incidentes, resumos diários do Slack e resumos de pesquisa: uma automação é
acionada, usa integrações configuradas como GitHub ou Slack para buscar contexto,
raciocina sobre esse contexto com um modelo de linguagem grande (LLM) e escreve
um resultado de volta.

O [Agent Canvas](https://github.com/OpenHands/agent-canvas) é o plano de controle
local para criar e testar essas automações. Neste playbook, ele executa um
OpenHands Agent Server, o processo de backend que executa conversas de agente,
e conecta o agente a serviços externos como GitHub e Slack.

Para manter o fluxo de trabalho no seu sistema AMD, o agente se comunica com um
modelo local servido pelo Lemonade Server. O Lemonade expõe esse modelo por
meio de uma API compatível com OpenAI, de forma que o Agent Canvas possa
configurá-lo como um endpoint remoto no estilo OpenAI, enquanto o modelo, o
prompt e o contexto do fluxo de trabalho permanecem locais.

Neste playbook, você criará uma automação concreta: um resumo agendado de
desenvolvimento do GitHub para o Slack. Ele usa o GitHub para inspecionar a
atividade recente do repositório, o Slack para publicar o resumo, chamadas à
API do Agent Canvas para configurar e testar a automação, e o Lemonade para
executar o LLM localmente.

![Diagrama de arquitetura mostrando GitHub MCP, automação OpenHands, Lemonade Server e Slack MCP](assets/00-architecture-overview.png)

## O Que Você Vai Aprender

- Como iniciar o Lemonade Server e verificar se um modelo local responde a
  solicitações de chat
- Como iniciar o Agent Canvas e apontar seu Agent Server para um LLM local
- Como instalar servidores GitHub e Slack Model Context Protocol (MCP) por
  meio da API do Agent Server
- Como criar e disparar uma automação agendada do OpenHands que publica um
  resumo de desenvolvimento no Slack
- Como solucionar as falhas mais comuns de modelo local e automação

## Conceitos Fundamentais

| Conceito | O que é | Onde se encaixa neste playbook |
| --- | --- | --- |
| Lemonade Server | Uma plataforma de serviço de LLM local criada para hardware AMD que expõe uma API compatível com OpenAI. Seus dados nunca saem da sua máquina. | Executa o modelo que alimenta o agente. |
| OpenHands Agent Server | O processo de backend que executa conversas de agente do OpenHands. | Hospeda o agente, seu perfil de LLM e seus servidores MCP. |
| Agent Canvas | O plano de controle local para o OpenHands que executa o Agent Server e uma interface para inspecionar execuções de agente. | Inicia os backends e fornece a API que você chama. |
| Servidor MCP | Um servidor Model Context Protocol que fornece a um agente ferramentas para um serviço externo, como GitHub ou Slack. | Permite que o agente leia o GitHub e escreva no Slack. |
| Automação OpenHands | Uma conversa de agente agendada ou acionada por evento que busca contexto, raciocina sobre ele e escreve um resultado em algum lugar. | O resumo de GitHub para Slack que você cria aqui. |

<!-- @device:stx,krk -->
> [!NOTE]
> Fluxos de trabalho de agentes de codificação se beneficiam de um modelo e
> uma janela de contexto maiores. Use pelo menos 32 GB de memória do sistema
> e prefira 64 GB ou mais para modelos GGUF maiores.
<!-- @device:end -->

## Pré-requisitos

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Você precisa de:

- Lemonade Server instalado seguindo o guia padrão de
  [instalação do Lemonade](https://lemonade-server.ai/docs/guide/install/).
- Node.js 22.12 ou posterior e `npm`, usados para instalar a CLI publicada do
  Agent Canvas e executar servidores MCP com `npx`.
- Um pacote `@openhands/agent-canvas` publicado recentemente, com
  configurações de agente orientadas por esquema, `LLMSummarizingCondenserSettings.max_tokens`,
  e suporte a `custom_tokenizer` de LLM.
- O pacote Python `transformers` disponível no ambiente do Agent Server.
  Ele é necessário para a contagem de tokens de modelos de chat quando
  `custom_tokenizer` está definido.
- Um token do GitHub com acesso de leitura ao repositório que você deseja
  resumir.
- Um token de bot do Slack (`xoxb-...`) com `chat:write` e acesso de leitura
  a canais.
- Um ID de equipe do Slack (`T...`).
- Um ID de canal do Slack (`C...`) onde o resumo deve ser publicado.

Convide o aplicativo do Slack para o canal de destino antes de testar a
automação.

## Variáveis Usadas Neste Playbook

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

Os valores a seguir são inseridos na interface do Agent Canvas em etapas
posteriores. Defina-os aqui para que você possa copiá-los depois:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

Use um valor explícito `owner/repo` para `GITHUB_REPO_FILTER`. Curingas amplos
de organização podem retornar contexto de MCP demais para modelos locais.

## 1. Inicie o Lemonade Server

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

Opcional: se o Agent Canvas ou o executor de automação não estiverem na mesma
máquina, publique o endpoint do Lemonade por meio de um túnel seguro e use a
URL HTTPS como a URL base do LLM:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Verifique o Modelo Local

Confirme que o Lemonade consegue servir o modelo selecionado:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Em seguida, envie uma pequena solicitação de chat:

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

Se isso retornar um array `choices`, o Lemonade está pronto para o Agent Canvas.
## 3. Iniciar o Agent Canvas

Instale o pacote publicado do Agent Canvas e inicie a stack completa:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Se a instalação global via npm falhar com um erro de permissão, consulte o
item de solução de problemas de permissões do npm abaixo.

Por padrão, o Agent Canvas é iniciado em `http://localhost:8000`. Abra essa
URL no seu navegador. O backend local padrão deve aparecer como saudável na
tela inicial.

O comando `agent-canvas` inicia o servidor de agente, o backend de automação
e o frontend web juntos. Você só precisa desse comando para executar o
OpenHands localmente. O restante deste guia configura tudo pela interface do
Agent Canvas no seu navegador.

## 4. Configurar o LLM local na interface

No primeiro uso, o Agent Canvas abre um fluxo de integração. Nesse fluxo:

1. Mantenha **OpenHands** selecionado como o agente e clique em **Next**.
2. Em **Set up your LLM**, selecione **Advanced**.
3. Mantenha **Authentication** definido como **API key**.
4. Defina **Custom Model** com o valor de `OPENHANDS_LLM_MODEL`,
   `openai/Qwen3.6-35B-A3B-GGUF`.
5. Defina **Base URL** como `http://127.0.0.1:13305/api/v1`.
6. Em **API Key**, digite qualquer valor de preenchimento não vazio, como
   `lemonade-local`. O Lemonade não exige uma chave real, mas o cliente do
   OpenHands precisa de um valor para enviar.

Os campos de conexão devem ficar assim. O campo de chave de API é mascarado
pela interface.

![Configurações avançadas de LLM do Agent Canvas no primeiro uso, com o modelo Lemonade e a URL base local](assets/01-llm-advanced-settings.png)

Em seguida, selecione **All** e defina os campos extras de modelo local:

1. Role até **Custom Tokenizer** e defina como `Qwen/Qwen3.6-35B-A3B`.
2. Role até **LiteLLM Extra Body** e defina como
   `{"enable_thinking": true}`.
3. Clique em **Next**.

![Aba All de LLM do Agent Canvas no primeiro uso, com o tokenizador personalizado do Qwen](assets/02-llm-all-tokenizer-settings.png)

![Aba All de LLM do Agent Canvas no primeiro uso, com o corpo extra do LiteLLM configurado](assets/03-llm-all-extra-body-settings.png)

As configurações de LLM devem mostrar:

| Campo | Valor |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

O prefixo `openai/` informa ao LiteLLM para usar a formatação de solicitação
compatível com OpenAI ao acessar o endpoint do Lemonade. O tokenizador
personalizado é o tokenizador original do Hugging Face para o modelo GGUF;
ele permite que o OpenHands conte os mesmos tokens de modelo de chat que o
servidor de modelo local vê. O formulário atual de LLM de primeiro uso não
exibe configurações de condensador. Se a sua versão do Agent Canvas exibir
configurações de condensador posteriormente em **Settings > LLM**, use
`llm_summarizing` e defina o número máximo de tokens abaixo da janela de
contexto do Lemonade, como `56000`.

## 5. Instalar os servidores MCP do GitHub e do Slack

Na interface do Agent Canvas, abra **Customize** (ou **Settings > MCP**) para
adicionar os servidores MCP que fornecem ao agente ferramentas para GitHub e
Slack. Os valores de token são enviados apenas ao seu Agent Server local e
são persistidos como configurações criptografadas.

### Servidor MCP do GitHub

Adicione um novo servidor MCP com estas configurações:

| Campo | Valor |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = seu token do GitHub |

Use um token do GitHub com acesso de leitura ao repositório que você deseja
resumir.

### Servidor MCP do Slack

Adicione um segundo servidor MCP com estas configurações:

| Campo | Valor |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = o ID do seu canal de resumo |

Defina `SLACK_CHANNEL_IDS` como o ID do canal de resumo (o mesmo valor de
`SLACK_DIGEST_CHANNEL`) para que o agente não precise percorrer todos os
canais do Slack.

Depois de adicionar os dois servidores, use o botão **Test** em cada um para
confirmar que eles se conectam e anunciam ferramentas. O servidor do GitHub
deve listar ferramentas do GitHub, e o servidor do Slack deve listar
ferramentas do Slack.

![Página de MCP do Agent Canvas com os servidores GitHub e Slack instalados](assets/04-mcp-servers-installed.png)

## 6. Criar a automação de resumo

Na interface do Agent Canvas, abra a página **Automations** e crie uma nova
automação:

1. Escolha **Create automation** e selecione o tipo **Prompt preset**.
2. Defina o **Name** como `GitHub Development Digest to Slack`.
3. Defina o **Prompt** com o texto a seguir, substituindo os espaços
   reservados de repositório e canal pelos seus valores:

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

4. Defina o **Trigger** como **Cron** com a programação `0 9 * * 1-5` (9h
   nos dias úteis) e defina o **Timezone** com o seu fuso horário, por
   exemplo `America/New_York`.
5. Defina o **Timeout** como `900` segundos.
6. Salve a automação.

A página de detalhes da automação mostra a nova automação com seu gatilho
cron e o ponto de entrada de prompt preset gerado.

![Página de detalhes da automação do Agent Canvas após a criação](assets/05-automation-created.png)
## 7. Teste a Automação

Na página de detalhes da automação na UI do Agent Canvas:

1. Clique em **Run now** (ou **Dispatch**) para executar a automação uma vez imediatamente.
2. Observe a lista de execuções na mesma página. A execução mais recente deve mudar para
   `COMPLETED`.
3. Abra seu canal do Slack de destino. Ele deve conter o resumo gerado.

Você não precisa esperar o cron schedule disparar—**Run now** aciona uma
execução sob demanda para que você possa confirmar que o prompt, as conexões MCP e a publicação no Slack
funcionam antes de depender do agendamento.

![Execução da automação do Agent Canvas concluída com sucesso](assets/06-automation-run-completed.png)

![Canal do Slack mostrando o resumo gerado pelo OpenHands](assets/07-slackbot-message.png)

## Solução de Problemas

- **O Lemonade está inativo:** reinicie-o com o
  comando `lemonade run "${LEMONADE_MODEL}"` na etapa 1 e execute novamente a verificação de
  integridade.
- **`npm install -g` falha com um erro de permissão:** no Linux ou WSL,
  configure um diretório global do npm de propriedade do usuário, adicione-o ao arquivo de inicialização do seu shell,
  e depois instale o Agent Canvas novamente:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  Se você usar `zsh`, adicione a mesma linha `export PATH=...` ao `~/.zshrc` em vez
  de `~/.bashrc`.
- **O Agent Canvas rejeita as configurações do LLM após definir `custom_tokenizer`:**
  instale `transformers` no ambiente Python do Agent Server, reinicie o Agent
  Canvas se necessário e tente salvar as configurações do LLM novamente. O OpenHands requer
  o Transformers para carregar o modelo de chat do tokenizador quando `custom_tokenizer` está
  definido.
- **O Agent Canvas não consegue acessar o Lemonade:** verifique
  `curl -fsS "${LEMONADE_BASE_URL}/health"` e confirme se a URL base inserida no
  formulário de LLM de primeiro uso ou em **Settings > LLM** corresponde ao endpoint local
  em execução ou ao túnel HTTPS.
- **As configurações do LLM não foram salvas:** certifique-se de ter clicado em **Next** após
  inserir os valores. Reabra **Settings > LLM** para confirmar que os valores
  persistiram.
- **O GitHub MCP não consegue ver repositórios privados:** confirme se o token do GitHub tem
  acesso de leitura ao repositório de destino e se o botão **Test** do MCP em
  **Customize** exibe as ferramentas do GitHub.
- **O Slack consegue ler canais, mas não consegue publicar:** convide o aplicativo do Slack para o
  canal de destino e confirme se o bot tem `chat:write`.
- **A automação lista muitos canais do Slack:** use um ID de canal do Slack e
  defina `SLACK_CHANNEL_IDS` no servidor MCP do Slack em **Customize**.
- **A execução da automação falha ou excede o contexto:** confirme se o Lemonade foi iniciado
  com `ctx_size=65536`, confirme se o LLM do OpenHands tem `custom_tokenizer` definido,
  e use um repositório explícito com os conjuntos de resultados do GitHub limitados a 3 a 5
  itens. Se a sua compilação do Agent Canvas expuser configurações de condenser, defina o máximo de tokens do condenser
  abaixo da janela de contexto do Lemonade.

## Próximos Passos

- Adicione um resumo semanal apenas de releases.
- Adicione uma automação acionada por eventos do GitHub para alertas mais rápidos de PR ou push.
- Direcione o mesmo resumo para o Notion, Linear ou outra ferramenta baseada em MCP.

## Recursos

- [Playbooks de IA da AMD](https://developer.amd.com/playbooks/)
- [Documentação do Lemonade Server](https://lemonade-server.ai/docs)
- [Repositório de extensões do OpenHands](https://github.com/OpenHands/extensions)
- [Servidores do Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Pacote Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)