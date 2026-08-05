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

[OpenHands](https://github.com/All-Hands-AI/OpenHands) é um agente de software de IA que pode escrever código, executar comandos, navegar na web e editar ficheiros num espaço de trabalho real. Em vez de copiar sugestões de uma janela de chat, o utilizador aponta o agente para uma pasta de projeto e deixa-o fazer o trabalho: implementar uma funcionalidade, corrigir um erro, escrever testes ou explicar uma base de código.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) é a interface de browser recomendada para executar o OpenHands. Um único comando `agent-canvas` inicia em conjunto o servidor do agente, o backend de automação e o frontend web, permitindo conduzir uma conversa com o agente a partir do browser.

Para manter tudo no seu sistema AMD, o agente comunica com um modelo local servido pelo Lemonade Server. O Lemonade expõe esse modelo através de uma API compatível com OpenAI, pelo que o Agent Canvas pode configurá-lo como qualquer outro endpoint no estilo OpenAI, enquanto o modelo, o seu código e o contexto da conversa permanecem na sua máquina.

Neste manual, vai iniciar um modelo local, iniciar o Agent Canvas, apontá-lo para esse modelo e executar a sua primeira tarefa de programação numa pasta de projeto real.

## O Que Vai Aprender

- Como iniciar o Lemonade Server e confirmar que um modelo local responde a pedidos de chat
- Como instalar e iniciar o Agent Canvas a partir do pacote npm
- Como configurar o Agent Canvas para utilizar um modelo Lemonade local como LLM
- Como iniciar uma conversa no OpenHands e observar o agente a editar ficheiros e a executar comandos num espaço de trabalho
- Como rever o que o agente alterou e orientá-lo com mensagens de acompanhamento

## Conceitos Fundamentais

| Conceito | O que é | Onde se enquadra neste manual |
| --- | --- | --- |
| Lemonade Server | Uma plataforma local de serviço de LLM criada para hardware AMD que expõe uma API compatível com OpenAI. Os seus dados nunca saem da sua máquina. | Executa o modelo que alimenta o agente. |
| OpenHands | Um agente de software de IA que lê e edita ficheiros, executa comandos de shell e navega na web dentro de um espaço de trabalho. | O agente que o utilizador conduz a partir do chat. |
| Agent Canvas | A interface de browser e o backend que executa as conversas do OpenHands e mostra chamadas de ferramentas e alterações de ficheiros. | Inicia a stack e aloja a sua conversa. |
| Workspace | A pasta de projeto que o agente tem permissão para ler e modificar. | O alvo das edições e comandos do agente. |

<!-- @device:stx,krk -->
> [!NOTE]
> Os fluxos de trabalho de agentes de programação beneficiam de um modelo maior e de uma janela de contexto mais ampla. Utilize pelo menos 32 GB de memória do sistema e prefira 64 GB ou mais para modelos GGUF maiores.
<!-- @device:end -->

## Pré-requisitos

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

É necessário:

- Lemonade Server instalado e capaz de servir o modelo abaixo.
- Node.js 22.12 ou posterior e `npm` (utilizado pela CLI do `agent-canvas`).
- `uv`, o gestor de pacotes Python que o Agent Canvas utiliza para gerir o ambiente do servidor do agente. Se o seu sistema ainda não o tiver, instale-o a partir do [guia de instalação do uv](https://docs.astral.sh/uv/getting-started/installation/) antes de iniciar o Agent Canvas.
- Uma pasta de projeto para trabalhar. Pode ser qualquer repositório git local ou diretório de código no qual pretenda que o agente trabalhe.

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. Iniciar o Lemonade Server

Inicie o modelo a partir da CLI do Lemonade:

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

Em seguida, envie um pequeno pedido de chat:

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

Se isto devolver um array `choices`, o Lemonade está pronto para o Agent Canvas.

## 3. Instalar e Iniciar o Agent Canvas

Instale o pacote publicado do Agent Canvas globalmente:

```bash
npm install -g @openhands/agent-canvas
```

Em seguida, inicie a stack completa a partir de um terminal:

```bash
agent-canvas
```

Por predefinição, o Agent Canvas inicia em `http://localhost:8000`. Abra esse URL no seu browser. Se a porta 8000 já estiver em uso, passe `--port` (ou `-p`) ao iniciar o Agent Canvas:

```bash
agent-canvas --port 3000
```

O mesmo comando funciona no PowerShell no Windows. Depois, abra `http://localhost:3000` em vez disso. O backend local predefinido deverá aparecer como saudável no ecrã principal.

O comando `agent-canvas` inicia em conjunto o servidor do agente, o backend de automação e o frontend web. Só precisa deste único comando para executar o OpenHands localmente.

## 4. Configurar o LLM Local

No primeiro arranque, o Agent Canvas abre um fluxo de integração. Nesse fluxo:

1. Mantenha **OpenHands** selecionado como agente e clique em **Next**.
2. Em **Set up your LLM**, selecione **Advanced**.
3. Mantenha **Authentication** definido como **API key**.
4. Defina **Custom Model** como `openai/Qwen3.6-35B-A3B-GGUF`.
5. Defina **Base URL** como `http://127.0.0.1:13305/api/v1`.
6. Em **API Key**, introduza qualquer valor de substituição não vazio, como `lemonade-local`. O Lemonade não requer uma chave real, mas o cliente OpenHands precisa de um valor para enviar.
7. Clique em **Next**.

As definições Advanced concluídas devem ter este aspeto. O campo da chave da API está oculto pela interface.

![Definições Advanced do LLM no primeiro uso do Agent Canvas com o modelo Lemonade e o URL base local](assets/01-llm-advanced-settings.png)

O Agent Canvas guarda estes valores como um perfil de LLM. Se a sua versão pedir para nomear esse perfil, utilize um nome sem espaços, como `lemonade-local`. Se alterar os modelos mais tarde, abra **Settings > LLM** e atualize os mesmos campos Advanced. Pode alternar entre perfis guardados a partir da entrada de chat com o comando `/model`.

## 5. Abrir um Workspace

O agente só pode ler e modificar ficheiros dentro de um workspace escolhido por si. Antes de iniciar uma tarefa, aponte o Agent Canvas para a sua pasta de projeto:

1. No ecrã principal, escolha **Open Workspace**.
2. Selecione a pasta que contém o seu projeto (por exemplo, um repositório git no qual pretenda que o agente trabalhe).
3. Inicie uma nova conversa nesse workspace.

Tudo o que o agente faz — ler ficheiros, executar comandos, editar código — está limitado a esse workspace.

![Ecrã principal do Agent Canvas após a integração](assets/02-agent-canvas-home.png)
## 6. Execute a Primeira Tarefa de Codificação

Com o espaço de trabalho aberto e o LLM local selecionado, escreva uma tarefa concreta no chat. Uma boa primeira tarefa é pequena e verificável, por exemplo:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Observe a linha temporal da conversa. O OpenHands irá:

- Ler o espaço de trabalho para compreender a estrutura.
- Criar `hello.py` com a função pedida e o bloco de teste.
- Opcionalmente, executar `python3 hello.py` para verificar o resultado.
- Reportar no chat o que fez e qualquer resultado de comandos.

Deverá ver o novo ficheiro a surgir no espaço de trabalho, e a mensagem final do agente deverá descrever a alteração que fez. Este é o momento de recompensa: o agente escreveu e executou código real na sua pasta de projeto.

## 7. Reveja e Oriente o Agente

Depois de o agente terminar um passo, reveja o trabalho antes de aceitar o passo seguinte:

- **Alterações a ficheiros**: utilize o navegador de ficheiros do espaço de trabalho ou a vista de diferenças do agente para ver exatamente o que foi adicionado, alterado ou eliminado.
- **Resultado de comandos**: expanda qualquer comando executado pelo agente para ver o stdout, stderr e o código de saída.
- **Acompanhamentos**: se o resultado não for o pretendido, responda na mesma conversa com uma correção. O agente mantém o contexto anterior e itera sobre os mesmos ficheiros.

Por exemplo, se o teste não imprimiu a saudação esperada, responda:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

O agente irá reler o ficheiro, executar o comando, diagnosticar o problema e editar o ficheiro novamente — tudo na mesma conversa.

## Resolução de Problemas

- **`agent-canvas` não está no PATH:** reinstale com
  `npm install -g @openhands/agent-canvas` e confirme que o diretório binário global do npm está no seu PATH. No Windows, execute `npm config get prefix`; o
  diretório devolvido, normalmente `%APPDATA%\npm` ou `%USERPROFILE%\.npm-global`,
  tem de estar no PATH do utilizador antes de o `agent-canvas` poder ser iniciado a partir de um novo terminal.
- **`npm install -g` falha com um erro de permissões:** configure um diretório global npm pertencente ao utilizador, depois reabra o terminal e instale o Agent Canvas novamente.

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

  Para tornar permanente a alteração do PATH no Windows, adicione `%USERPROFILE%\.npm-global` ao
  PATH do seu utilizador em **Definições > Sistema > Acerca > Definições avançadas do sistema >
  Variáveis de Ambiente**, e abra um novo terminal.
  <!-- @os:end -->
- **A interface carrega mas o backend aparece como não saudável:** aguarde alguns segundos até o servidor do agente terminar de iniciar, depois atualize a página. Se permanecer não saudável, reinicie
  o `agent-canvas` e verifique o resultado do terminal em busca de erros.
- **Os pedidos de chat do Lemonade falham com um erro de ligação:** confirme que
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` é bem-sucedido e que
  o Lemonade continua a servir o modelo com `lemonade status`.
- **O agente apresenta um erro de comprimento de contexto ou limite de tokens:** reinicie
  o Lemonade com um `ctx_size` maior (por exemplo `ctx_size=65536`), e inicie uma
  conversa nova para que o agente não transporte um histórico demasiado grande.
- **O agente produz edições de baixa qualidade ou incompletas:** mude para um
  modelo maior no Lemonade, ou dê ao agente uma tarefa mais pequena e concreta, deixando-o
  terminar antes de pedir a alteração seguinte.
- **Falta o `uv`:** instale-o a partir de
  [the uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).
  O Agent Canvas utiliza o `uv` para gerir o ambiente Python do servidor do agente.

## Passos Seguintes

- Experimente uma tarefa maior no mesmo espaço de trabalho, como adicionar um ficheiro de teste unitário ou
  corrigir um bug conhecido, e reveja as diferenças do agente antes de manter a alteração.
- Ligue um servidor MCP como o GitHub ou o Slack em **Customize** para que
  o agente possa ler issues ou publicar atualizações enquanto trabalha.
- Guarde vários perfis de LLM (um modelo pequeno e rápido e um modelo grande e mais potente) e
  alterne entre eles com `/model` a meio da conversa.
- Avance para [OpenHands automations](https://docs.openhands.dev/openhands/usage/automations/overview) para
  transformar ciclos de desenvolvimento recorrentes em execuções de agentes agendadas ou acionadas por eventos.

## Recursos

- [Documentação do OpenHands](https://docs.openhands.dev/)
- [Visão geral do Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Configuração do Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [Perfis de LLM e configuração de modelos](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Documentação do Lemonade Server](https://lemonade-server.ai/docs)