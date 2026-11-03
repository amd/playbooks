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
ambiente de trabalho real. Em vez de copiar sugestões de uma janela de chat, você
aponta o agente para uma pasta de projeto e o deixa fazer o trabalho: implementar
um recurso, corrigir um bug, escrever testes ou explicar uma base de código.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) é a interface de
navegador recomendada para executar o OpenHands. Um único comando `agent-canvas`
inicia o servidor do agente, o backend de automação e o frontend web juntos, para
que você possa conduzir uma conversa com o agente pelo seu navegador.

Para manter tudo no seu sistema AMD, o agente conversa com um modelo local
servido pelo Lemonade Server. O Lemonade expõe esse modelo por meio de uma API
compatível com OpenAI, para que o Agent Canvas possa configurá-lo como qualquer
outro endpoint no estilo OpenAI, enquanto o modelo, seu código e o contexto da
conversa permanecem na sua máquina.

Neste guia, você vai iniciar um modelo local, abrir o Agent Canvas, apontá-lo
para esse modelo e executar sua primeira tarefa de codificação em uma pasta de
projeto real.

## O Que Você Vai Aprender

- Como iniciar o Lemonade Server e confirmar que um modelo local responde a
  solicitações de chat
- Como instalar e iniciar o Agent Canvas a partir do pacote npm
- Como configurar o Agent Canvas para usar um modelo local do Lemonade como LLM
- Como iniciar uma conversa do OpenHands e observar o agente editando arquivos e
  executando comandos em um ambiente de trabalho
- Como revisar o que o agente alterou e orientá-lo com mensagens de acompanhamento

## Conceitos Principais

| Conceito | O que é | Onde se encaixa neste guia |
| --- | --- | --- |
| Lemonade Server | Uma plataforma local de serviço de LLM criada para hardware AMD que expõe uma API compatível com OpenAI. Seus dados nunca saem da sua máquina. | Executa o modelo que alimenta o agente. |
| OpenHands | Um agente de software de IA que lê e edita arquivos, executa comandos de shell e navega na web dentro de um ambiente de trabalho. | O agente que você conduz a partir do chat. |
| Agent Canvas | A interface de navegador e o backend que executam conversas do OpenHands e exibem chamadas de ferramentas e alterações de arquivos. | Inicia a stack e hospeda sua conversa. |
| Ambiente de Trabalho | A pasta de projeto que o agente tem permissão para ler e modificar. | O alvo das edições e comandos do agente. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Fluxos de trabalho de agentes de codificação se beneficiam de um modelo e
> janela de contexto maiores. Use pelo menos 32 GB de memória do sistema e
> prefira 64 GB ou mais para modelos GGUF maiores.
<!-- @device:end -->

## Definindo a Configuração de Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software

<!-- @require:software-update -->
<!-- @device:end -->

## Pré-requisitos


<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

Você precisa de:

- Lemonade Server instalado e capaz de servir o modelo abaixo.

<!-- @os:linux -->
- Node.js 22.12 ou posterior e `npm` (usados pela CLI `agent-canvas`).
- `uv`, o gerenciador de pacotes Python que o Agent Canvas usa para gerenciar
  o ambiente do servidor do agente. Se o seu sistema ainda não o tiver,
  instale-o a partir do
  [guia de instalação do uv](https://docs.astral.sh/uv/getting-started/installation/)
  antes de iniciar o Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop para Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  instalado e em execução. No Windows, a stack do Agent Canvas é executada a
  partir da imagem Docker publicada, que já inclui Node.js, `uv` e o pacote
  `@openhands/agent-canvas`, então você não precisa instalá-los na máquina
  host.
<!-- @os:end -->

- Uma pasta de projeto para trabalhar. Pode ser qualquer repositório git local
  ou diretório de código no qual você deseja que o agente trabalhe.

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
<!-- @test:id=prereq-clis-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

lemonade --version
node -v
npm -v

# uv is a required prerequisite (agent-canvas uses it to build its Python env).
# Install it only if the runner doesn't already have it.
# TODO: remove this self-provisioning once the runners ship uv by default.
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"
uv --version

echo "OK: lemonade, node, npm, and uv are all available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=prereq-clis-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# On Windows the Agent Canvas stack runs from the published Docker image, so the
# only host prerequisites are Lemonade and a running Docker engine. Node.js, uv,
# and agent-canvas are bundled inside the container.
lemonade --version
docker version --format "{{.Server.Version}}"

Write-Host "OK: lemonade and docker are available"
```
<!-- @test:end -->
<!-- @os:end -->

## 1. Iniciar o Lemonade Server

Inicie o modelo pela CLI do Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Escolha um modelo compatível com seu hardware.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) é um modelo de codificação forte, mas precisa de um grande volume de memória. Se seu dispositivo tem memória ou VRAM de GPU limitada, escolha um modelo GGUF menor da biblioteca de modelos do Lemonade e use esse ID de modelo em todo este guia.

> **Observação:** O primeiro `lemonade run` baixa o modelo caso ele ainda não esteja presente, o que pode levar um tempo dependendo do tamanho do modelo e da sua conexão.

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

<!-- @os:linux -->
<!-- @test:id=lemonade-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

export MODELS_JSON="$models_json"

python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
model_id = "${lemonade_model}"

entry = None
for item in data.get("data", []):
    if item.get("id") == model_id:
        entry = item
        break

if entry is None:
    print(f"Model {model_id} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print(f"Model {model_id} is present but not downloaded in Lemonade. Please download it before running CI.")
    sys.exit(1)

print(f"OK: {model_id} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Lemonade chat/completions returned a response"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$modelsJson = $null
for ($i = 0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}

if (-not $modelsJson) {throw "Lemonade server not ready on http://127.0.0.1:13305"}
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model = "${lemonade_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openhands-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) {throw "Empty response from Lemonade chat/completions"}
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->
## 3. Instalar e Iniciar o Agent Canvas

<!-- @os:linux -->
Instale o pacote publicado do Agent Canvas globalmente:

```bash
npm install -g @openhands/agent-canvas
```

<!-- @test:id=agent-canvas-version-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# agent-canvas is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than installing it here.
if ! command -v agent-canvas >/dev/null 2>&1; then
  echo "agent-canvas is not on PATH; the runner must provision it before CI runs"
  exit 1
fi

# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help

echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

Em seguida, inicie a stack completa em um terminal:

```bash
agent-canvas
```

Por padrão, o Agent Canvas é iniciado em `http://localhost:8000`. Abra essa URL em
seu navegador. A porta não é especial — se a 8000 já estiver em uso, passe qualquer
porta livre com `--port` (ou `-p`) ao iniciar o Agent Canvas:

```bash
agent-canvas --port 3000
```

Em seguida, abra `http://localhost:3000`. O backend local padrão deve aparecer
como saudável na tela inicial.

O comando `agent-canvas` inicia o servidor de agente, o backend de automação e
o frontend web juntos. Você só precisa desse único comando para executar o OpenHands
localmente.

<!-- @test:id=agent-canvas-server-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

log="/tmp/agent-canvas-ci.log"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000
# ingress root: the ingress serves the static frontend and returns 200 for /
# even when the agent-server is down.
ok=false
for i in $(seq 1 300); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18000/server_info || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  if ! kill -0 "$p" 2>/dev/null; then
    echo "agent-canvas process exited before it finished starting"
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "agent-server not ready on http://127.0.0.1:18000/server_info"
  echo "---- agent-canvas log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
No Windows, execute a imagem de container publicada do Agent Canvas com o Docker Desktop.
A imagem inclui o Agent Server, o backend de automação e o frontend web, então
você não precisa instalar o Node.js, o `uv` ou a CLI na máquina host.

Primeiro, crie as pastas de configuração e de workspace que o container monta:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Baixe a imagem publicada (ela é pública, portanto nenhum login é necessário):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Em seguida, inicie a stack:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Abra `http://localhost:8000/canvas` em seu navegador. Se a porta 8000 já estiver em
uso, mapeie uma porta diferente no host, por exemplo `-p 8080:8000`, e abra
`http://localhost:8080/canvas` no lugar.

> **Observação:** o primeiro lançamento inicializa o Agent Server dentro do container,
> então pode levar um ou dois minutos até o backend reportar-se saudável.

O ponto de montagem `.openhands` mantém seu perfil de LLM e as configurações entre
reinicializações do container. O restante deste guia configura tudo pela
interface do Agent Canvas no seu navegador.

<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "openhands-agent-canvas-ci"
$hostPort = 18080

# The image is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than pulling it here.
$imgId = docker images -q $image
if (-not $imgId) {
  throw "Image $image is not present; the runner must provision it before CI runs"
}
Write-Host "OK: $image is present"

if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }

try {
  docker run -d --name $name -p "${hostPort}:8000" $image | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "docker run failed for $image" }

  # Probe the agent-server backend health through the container proxy
  # (/server_info -> agent-server on 18000 inside the container), not just the
  # /canvas static UI, which can return 200 while the backend is still down.
  $ok = $false
  for ($i = 0; $i -lt 300; $i++) {
    $canvas = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/canvas").StatusCode } catch { 0 }
    $info   = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/server_info").StatusCode } catch { 0 }
    if ($canvas -eq 200 -and $info -eq 200) { $ok = $true; break }
    $state = docker inspect -f "{{.State.Status}}" $name 2>$null
    if ($state -ne "running") { throw "Container $name exited before it finished starting" }
    Start-Sleep -Seconds 2
  }

  if (-not $ok) {
    docker logs --tail 40 $name
    throw "agent-canvas backend not healthy on http://localhost:${hostPort}/server_info"
  }
  Write-Host "OK: agent-canvas Docker stack is healthy (/canvas and /server_info return 200)"
}
finally {
  if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }
}
```
<!-- @test:end -->
<!-- @os:end -->

## 4. Configurar o LLM Local

Na primeira inicialização, o Agent Canvas abre um fluxo de integração. Nesse fluxo:

1. Mantenha **OpenHands** selecionado como o agente e clique em **Next**.
2. Em **Set up your LLM**, selecione **Advanced**.
3. Mantenha **Authentication** definido como **API key**.
4. Defina **Custom Model** como `openai/Qwen3.6-35B-A3B-GGUF`.
5. Defina **Base URL** como `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > No Windows, a stack é executada em um container, que não consegue alcançar o host em
   > `127.0.0.1`. Use `http://host.docker.internal:13305/api/v1` em vez disso, para que
   > o agente em container consiga alcançar o Lemonade em execução no host Windows.
   <!-- @os:end -->
6. Em **API Key**, insira qualquer valor de espaço reservado não vazio, como `lemonade-local`.
   O Lemonade não exige uma chave real, mas o cliente do OpenHands precisa de um valor
   para enviar.
7. Clique em **Next**.

As configurações Advanced concluídas devem ficar assim. O campo de chave de API é
mascarado pela interface.

![Configurações Advanced de LLM do Agent Canvas no primeiro uso, com o modelo Lemonade e a URL base local](assets/01-llm-advanced-settings.png)

O Agent Canvas salva esses valores como um perfil de LLM. Se sua versão pedir para
nomear esse perfil, use um nome sem espaços, como `lemonade-local`. Se você alterar
os modelos posteriormente, abra **Settings > LLM** e atualize os mesmos campos Advanced. Você
pode alternar entre perfis salvos a partir do campo de chat com o comando `/model`.

## 5. Abrir um Workspace

O agente só pode ler e modificar arquivos dentro de um workspace que você escolher. Antes
de iniciar uma tarefa, aponte o Agent Canvas para a pasta do seu projeto:

1. Na tela inicial, escolha **Open Workspace**.
2. Selecione a pasta que contém seu projeto (por exemplo, um repositório git
   no qual você deseja que o agente trabalhe).
3. Inicie uma nova conversa nesse workspace.

Tudo o que o agente faz—ler arquivos, executar comandos, editar código—fica
restrito a esse workspace.

![Tela inicial do Agent Canvas após a integração](assets/02-agent-canvas-home.png)

## 6. Execute Sua Primeira Tarefa de Codificação

Com o workspace aberto e o LLM local selecionado, digite uma tarefa concreta no
chat. Uma boa primeira tarefa é pequena e verificável, por exemplo:

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

Você deve ver o novo arquivo aparecer no workspace, e a mensagem final do agente
deve descrever a alteração que ele fez. Este é o momento de recompensa: o
agente escreveu e executou código real na pasta do seu projeto.

## 7. Revise e Oriente o Agente

Depois que o agente terminar uma etapa, revise o trabalho antes de aceitar a próxima:

- **Alterações de arquivo**: use o navegador de arquivos do workspace ou a visualização de diff do agente para
  ver exatamente o que foi adicionado, alterado ou excluído.
- **Saída de comando**: expanda qualquer comando executado pelo agente para ver a saída padrão (stdout), a saída de erro (stderr)
  e o código de saída.
- **Acompanhamentos**: se o resultado não for o que você queria, responda na mesma
  conversa com uma correção. O agente mantém o contexto anterior e
  itera sobre os mesmos arquivos.

Por exemplo, se o teste não imprimiu a saudação esperada, responda:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

O agente irá reler o arquivo, executar o comando, diagnosticar o problema e editar
o arquivo novamente—tudo na mesma conversa.
## Solução de problemas

<!-- @os:linux -->
- **`agent-canvas` não está no PATH:** reinstale com
  `npm install -g @openhands/agent-canvas` e confirme que o diretório binário
  global do npm está no seu PATH antes que o `agent-canvas` possa ser iniciado
  a partir de um novo terminal.
- **`npm install -g` falha com erro de permissão:** configure um diretório
  global do npm de propriedade do usuário, depois reabra o terminal e instale
  o Agent Canvas novamente.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` está ausente:** instale-o a partir do
  [guia de instalação do uv](https://docs.astral.sh/uv/getting-started/installation/).
  O Agent Canvas usa o `uv` para gerenciar o ambiente Python do servidor de agente.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` ou `docker run` falha ao conectar:** certifique-se de que o
  Docker Desktop está em execução (o ícone da baleia está na bandeja do
  sistema) e que o mecanismo terminou de iniciar. `docker version` deve
  exibir tanto uma seção Client quanto uma seção Server.
- **O contêiner inicia, mas o backend nunca fica íntegro:** a primeira
  inicialização inicializa o Agent Server dentro do contêiner; aguarde um ou
  dois minutos e, em seguida, verifique `docker logs <container>` em busca de erros.
- **O contêiner não consegue alcançar o Lemonade:** o contêiner alcança o host
  por meio de `host.docker.internal`. Confirme se o Lemonade está servindo no
  host Windows com `lemonade status` e use `http://host.docker.internal:13305/api/v1`
  como a Base URL ao configurar o LLM.
<!-- @os:end -->

- **A UI carrega, mas o backend aparece como não íntegro:** aguarde um ou dois
  minutos para que o servidor de agente termine de iniciar e, em seguida,
  atualize a página. Se continuar não íntegro, reinicie a pilha e verifique
  os logs em busca de erros.
- **As solicitações de chat do Lemonade falham com erro de conexão:** confirme
  que `curl -fsS "http://127.0.0.1:13305/api/v1/health"` tem sucesso e que o
  Lemonade ainda está servindo o modelo com `lemonade status`.
- **O agente apresenta erro de limite de contexto ou de tokens:** inicie uma
  conversa nova para que o agente não carregue um histórico excessivamente
  grande. Se isso continuar acontecendo, reinicie o Lemonade com um
  `ctx_size` maior do que o padrão de 65536 (por exemplo, `ctx_size=131072`),
  se a memória permitir.
- **O agente produz edições de baixa qualidade ou incompletas:** mude para um
  modelo maior no Lemonade, ou dê ao agente uma tarefa menor e mais concreta e
  deixe-o terminar antes de solicitar a próxima alteração.

## Próximos passos

- Experimente uma tarefa maior no mesmo workspace, como adicionar um arquivo de
  teste unitário ou corrigir um bug conhecido, e revise o diff do agente antes
  de manter a alteração.
- Conecte um servidor MCP, como GitHub ou Slack, em **Customize** para que o
  agente possa ler issues ou publicar atualizações enquanto trabalha.
- Salve vários perfis de LLM (um modelo pequeno e rápido e um modelo grande e
  mais robusto) e alterne entre eles com `/model` no meio da conversa.
- Avance para [automações do OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview)
  para transformar ciclos recorrentes de desenvolvimento em execuções de
  agente agendadas ou acionadas por eventos.

## Recursos

- [Documentação do OpenHands](https://docs.openhands.dev/)
- [Visão geral do Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Configuração do Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [Perfis de LLM e configuração de modelo](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Documentação do Lemonade Server](https://lemonade-server.ai/docs)

<!-- @os:linux -->
<!-- @test:id=lemonade-unload-linux timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-unload-windows timeout=60 hidden=True -->
```powershell
# CI cleanup: unload the model so the GPU pool is free
lemonade unload
exit 0
```
<!-- @test:end -->
<!-- @os:end -->