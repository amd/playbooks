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

[OpenHands](https://github.com/All-Hands-AI/OpenHands) é um agente de software de IA
que pode escrever código, executar comandos, navegar na web e editar arquivos em um
workspace real. Em vez de copiar sugestões de uma janela de chat, você aponta o
agente para uma pasta de projeto e deixa que ele faça o trabalho: implementar um
recurso, corrigir um bug, escrever testes ou explicar uma base de código.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) é a interface de
navegador recomendada para executar o OpenHands. Um único comando `agent-canvas`
inicia o servidor do agente, o backend de automação e o frontend web juntos, para
que você possa conduzir uma conversa com o agente pelo navegador.

Para manter tudo no seu sistema AMD, o agente conversa com um modelo local servido
pelo Lemonade Server. O Lemonade expõe esse modelo por meio de uma API compatível
com OpenAI, então o Agent Canvas pode configurá-lo como qualquer outro endpoint no
estilo OpenAI, enquanto o modelo, seu código e o contexto da conversa permanecem
na sua máquina.

Neste playbook, você iniciará um modelo local, abrirá o Agent Canvas, apontará-o
para esse modelo e executará sua primeira tarefa de codificação em uma pasta de
projeto real.

## O que você vai aprender

- Como iniciar o Lemonade Server e confirmar que um modelo local responde a
  solicitações de chat
- Como instalar e iniciar o Agent Canvas a partir do pacote npm
- Como configurar o Agent Canvas para usar um modelo local do Lemonade como LLM
- Como iniciar uma conversa no OpenHands e observar o agente editando arquivos e
  executando comandos em um workspace
- Como revisar o que o agente alterou e orientá-lo com mensagens de acompanhamento

## Conceitos Fundamentais

| Conceito | O que é | Onde se encaixa neste playbook |
| --- | --- | --- |
| Lemonade Server | Uma plataforma local de serviço de LLM criada para hardware AMD que expõe uma API compatível com OpenAI. Seus dados nunca saem da sua máquina. | Executa o modelo que alimenta o agente. |
| OpenHands | Um agente de software de IA que lê e edita arquivos, executa comandos de shell e navega na web dentro de um workspace. | O agente que você conduz pelo chat. |
| Agent Canvas | A interface de navegador e o backend que executam conversas do OpenHands e mostram chamadas de ferramentas e alterações de arquivos. | Inicia a stack e hospeda sua conversa. |
| Workspace | A pasta de projeto que o agente tem permissão para ler e modificar. | O alvo das edições e comandos do agente. |

<!-- @device:stx,krk -->
> [!NOTE]
> Fluxos de trabalho com agentes de codificação se beneficiam de um modelo maior
> e de uma janela de contexto maior. Use pelo menos 32 GB de memória do sistema
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

- Lemonade Server instalado e capaz de servir o modelo abaixo.
- Node.js 22.12 ou posterior e `npm` (usados pelo CLI do `agent-canvas`).
- `uv`, o gerenciador de pacotes Python usado pelo Agent Canvas para gerenciar o
  ambiente do servidor do agente. Se seu sistema ainda não o tiver, instale-o a
  partir do [guia de instalação do uv](https://docs.astral.sh/uv/getting-started/installation/)
  antes de iniciar o Agent Canvas.
- Uma pasta de projeto para trabalhar. Pode ser qualquer repositório git local ou
  diretório de código no qual você queira que o agente trabalhe.

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. Iniciar o Lemonade Server

Inicie o modelo pelo CLI do Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

O Lemonade expõe uma API compatível com OpenAI em:

```text
http://127.0.0.1:13305/api/v1
```



## 2. Verificar o Modelo Local

Confirme que o Lemonade consegue servir o modelo selecionado:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Em seguida, envie uma pequena solicitação de chat:

```bash
curl -sS "http://127.0.0.1:13305/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.6-35B-A3B-GGUF",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

Se isso retornar um array `choices`, o Lemonade está pronto para o Agent Canvas.

## 3. Instalar e Iniciar o Agent Canvas

Instale o pacote publicado do Agent Canvas globalmente:

```bash
npm install -g @openhands/agent-canvas
```

Em seguida, inicie a stack completa a partir de um terminal:

```bash
agent-canvas
```

Por padrão, o Agent Canvas inicia em `http://localhost:8000`. Abra essa URL no
seu navegador. Se a porta 8000 já estiver em uso, passe `--port` (ou `-p`) ao
iniciar o Agent Canvas:

```bash
agent-canvas --port 3000
```

O mesmo comando funciona no PowerShell no Windows. Em seguida, abra
`http://localhost:3000` em vez disso. O backend local padrão deve aparecer como
saudável na tela inicial.

O comando `agent-canvas` inicia o servidor do agente, o backend de automação e
o frontend web juntos. Você só precisa deste único comando para executar o
OpenHands localmente.

## 4. Configurar o LLM Local

No primeiro uso, o Agent Canvas abre um fluxo de integração (onboarding). Nesse
fluxo:

1. Mantenha **OpenHands** selecionado como o agente e clique em **Next**.
2. Em **Set up your LLM**, selecione **Advanced**.
3. Mantenha **Authentication** definido como **API key**.
4. Defina **Custom Model** como `openai/Qwen3.6-35B-A3B-GGUF`.
5. Defina **Base URL** como `http://127.0.0.1:13305/api/v1`.
6. Em **API Key**, insira qualquer valor de espaço reservado não vazio, como
   `lemonade-local`. O Lemonade não exige uma chave real, mas o cliente
   OpenHands precisa de um valor para enviar.
7. Clique em **Next**.

As configurações Advanced concluídas devem se parecer com isto. O campo de
chave de API é mascarado pela interface.

![Configurações Advanced de LLM do Agent Canvas no primeiro uso com o modelo Lemonade e a URL base local](assets/01-llm-advanced-settings.png)

O Agent Canvas salva esses valores como um perfil de LLM. Se sua versão pedir
que você nomeie esse perfil, use um nome sem espaços, como `lemonade-local`.
Se você mudar de modelo mais tarde, abra **Settings > LLM** e atualize os
mesmos campos Advanced. Você pode alternar entre perfis salvos a partir do
campo de chat com o comando `/model`.

## 5. Abrir um Workspace

O agente só pode ler e modificar arquivos dentro de um workspace escolhido por
você. Antes de iniciar uma tarefa, aponte o Agent Canvas para a pasta do seu
projeto:

1. Na tela inicial, escolha **Open Workspace**.
2. Selecione a pasta que contém seu projeto (por exemplo, um repositório git no
   qual você queira que o agente trabalhe).
3. Inicie uma nova conversa nesse workspace.

Tudo o que o agente faz — ler arquivos, executar comandos, editar código — fica
restrito a esse workspace.

![Tela inicial do Agent Canvas após a integração](assets/02-agent-canvas-home.png)
## 6. Execute sua primeira tarefa de codificação

Com o workspace aberto e o LLM local selecionado, digite uma tarefa concreta
no chat. Uma boa primeira tarefa é pequena e verificável, por exemplo:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Observe a linha do tempo da conversa. O OpenHands irá:

- Ler o workspace para entender a estrutura.
- Criar `hello.py` com a função solicitada e o bloco de teste.
- Opcionalmente, executar `python3 hello.py` para verificar a saída.
- Relatar o que fez e qualquer saída de comando no chat.

Você deve ver o novo arquivo aparecer no workspace, e a mensagem final do
agente deve descrever a alteração que ele fez. Este é o momento de recompensa:
o agente escreveu e executou código real na pasta do seu projeto.

## 7. Revise e oriente o agente

Depois que o agente concluir uma etapa, revise seu trabalho antes de aceitar a
próxima:

- **Alterações de arquivo**: use o navegador de arquivos do workspace ou a
  visualização de diff do agente para ver exatamente o que foi adicionado,
  alterado ou excluído.
- **Saída de comando**: expanda qualquer comando que o agente executou para
  ver stdout, stderr e o código de saída.
- **Acompanhamentos**: se o resultado não for o que você queria, responda na
  mesma conversa com uma correção. O agente mantém o contexto anterior e
  itera nos mesmos arquivos.

Por exemplo, se o teste não imprimiu a saudação esperada, responda:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

O agente vai reler o arquivo, executar o comando, diagnosticar o problema e
editar o arquivo novamente—tudo na mesma conversa.

## Solução de problemas

- **`agent-canvas` não está no PATH:** reinstale com
  `npm install -g @openhands/agent-canvas` e confirme que o diretório binário
  global do npm está no seu PATH. No Windows, execute `npm config get prefix`;
  o diretório retornado, geralmente `%APPDATA%\npm` ou
  `%USERPROFILE%\.npm-global`, deve estar no PATH do usuário antes que o
  `agent-canvas` possa ser iniciado a partir de um novo terminal.
- **`npm install -g` falha com um erro de permissão:** configure um diretório
  global do npm de propriedade do usuário, depois reabra o terminal e instale
  o Agent Canvas novamente.

  <!-- @os:linux -->
  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
  <!-- @os:end -->

  <!-- @os:windows -->
  ```powershell
  New-Item -ItemType Directory -Force "$env:USERPROFILE\.npm-global"
  npm config set prefix "$env:USERPROFILE\.npm-global"
  $env:Path = "$env:USERPROFILE\.npm-global;$env:Path"
  npm install -g @openhands/agent-canvas
  ```

  Para tornar a alteração do PATH do Windows permanente, adicione
  `%USERPROFILE%\.npm-global` ao PATH do seu usuário em **Configurações >
  Sistema > Sobre > Configurações avançadas do sistema > Variáveis de
  ambiente**, e abra um novo terminal.
  <!-- @os:end -->
- **A interface carrega, mas o backend mostra estado não saudável:** aguarde
  alguns segundos para que o servidor do agente termine de iniciar e, em
  seguida, atualize a página. Se continuar não saudável, reinicie o
  `agent-canvas` e verifique a saída do terminal em busca de erros.
- **As solicitações de chat do Lemonade falham com erro de conexão:**
  confirme que `curl -fsS "http://127.0.0.1:13305/api/v1/health"` é
  bem-sucedido e que o Lemonade ainda está servindo o modelo com
  `lemonade status`.
- **O agente apresenta erro com mensagem de limite de contexto ou de
  tokens:** reinicie o Lemonade com um `ctx_size` maior (por exemplo,
  `ctx_size=65536`), e inicie uma nova conversa para que o agente não carregue
  um histórico muito grande.
- **O agente produz edições de baixa qualidade ou incompletas:** mude para um
  modelo maior no Lemonade, ou dê ao agente uma tarefa menor e mais concreta e
  deixe-o terminar antes de pedir a próxima alteração.
- **`uv` está faltando:** instale-o a partir do
  [guia de instalação do uv](https://docs.astral.sh/uv/getting-started/installation/).
  O Agent Canvas usa o `uv` para gerenciar o ambiente Python do servidor do
  agente.

## Próximos passos

- Tente uma tarefa maior no mesmo workspace, como adicionar um arquivo de
  teste unitário ou corrigir um bug conhecido, e revise o diff do agente antes
  de manter a alteração.
- Conecte um servidor MCP, como GitHub ou Slack, em **Customize** para que o
  agente possa ler issues ou publicar atualizações enquanto trabalha.
- Salve vários perfis de LLM (um modelo pequeno e rápido e um modelo grande e
  mais poderoso) e alterne entre eles com `/model` no meio da conversa.
- Avance para [automações do OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) para
  transformar loops de desenvolvimento recorrentes em execuções de agente
  programadas ou acionadas por eventos.

## Recursos

- [Documentação do OpenHands](https://docs.openhands.dev/)
- [Visão geral do Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Configuração do Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [Perfis de LLM e configuração de modelo](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Documentação do Lemonade Server](https://lemonade-server.ai/docs)