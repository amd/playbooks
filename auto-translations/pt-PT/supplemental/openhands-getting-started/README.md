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

## Descrição Geral

[OpenHands](https://github.com/All-Hands-AI/OpenHands) é um agente de software de IA
que pode escrever código, executar comandos, navegar na Web e editar ficheiros num
espaço de trabalho real. Em vez de copiar sugestões de uma janela de chat, indica-se
ao agente uma pasta de projeto e deixa-se que ele faça o trabalho: implementar uma
funcionalidade, corrigir um erro, escrever testes ou explicar uma base de código.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) é a interface de utilizador
no browser recomendada para executar o OpenHands. Um único comando `agent-canvas`
inicia o servidor do agente, o back-end de automatização e a interface Web em
conjunto, permitindo conduzir uma conversa com o agente a partir do browser.

Para manter tudo no seu sistema AMD, o agente comunica com um modelo local servido
pelo Lemonade Server. O Lemonade expõe esse modelo através de uma API compatível
com OpenAI, pelo que o Agent Canvas pode configurá-lo como qualquer outro endpoint
no estilo OpenAI, enquanto o modelo, o seu código e o contexto da conversa
permanecem todos na sua máquina.

Neste guia prático, vai iniciar um modelo local, lançar o Agent Canvas, apontá-lo
para esse modelo e executar a sua primeira tarefa de codificação numa pasta de
projeto real.

## O Que Vai Aprender

- Como iniciar o Lemonade Server e confirmar que um modelo local responde a
  pedidos de chat
- Como instalar e lançar o Agent Canvas a partir do pacote npm
- Como configurar o Agent Canvas para utilizar um modelo Lemonade local como LLM
- Como iniciar uma conversa OpenHands e observar o agente a editar ficheiros e a
  executar comandos num espaço de trabalho
- Como rever o que o agente alterou e orientá-lo com mensagens de seguimento

## Conceitos Fundamentais

| Conceito | O que é | Onde se encaixa neste guia prático |
| --- | --- | --- |
| Lemonade Server | Uma plataforma local de disponibilização de LLM criada para hardware AMD que expõe uma API compatível com OpenAI. Os seus dados nunca saem da sua máquina. | Executa o modelo que alimenta o agente. |
| OpenHands | Um agente de software de IA que lê e edita ficheiros, executa comandos de shell e navega na Web dentro de um espaço de trabalho. | O agente que se conduz a partir do chat. |
| Agent Canvas | A interface de utilizador no browser e o back-end que executa conversas OpenHands e mostra chamadas de ferramentas e alterações de ficheiros. | Lança a stack e aloja a sua conversa. |
| Espaço de trabalho | A pasta de projeto que o agente tem permissão para ler e modificar. | O alvo das edições e comandos do agente. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Os fluxos de trabalho de agentes de codificação beneficiam de um modelo maior e
> de uma janela de contexto maior. Utilize pelo menos 32 GB de memória do
> sistema e dê preferência a 64 GB ou mais para modelos GGUF maiores.
<!-- @device:end -->

## Definir a Configuração de Memória

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

Precisa de:

- Lemonade Server instalado e capaz de disponibilizar o modelo abaixo.

<!-- @os:linux -->
- Node.js 22.12 ou posterior e `npm` (utilizados pela CLI do `agent-canvas`).
- `uv`, o gestor de pacotes Python que o Agent Canvas utiliza para gerir o
  ambiente do servidor do agente. Se o seu sistema ainda não o tiver, instale-o
  a partir do
  [guia de instalação do uv](https://docs.astral.sh/uv/getting-started/installation/)
  antes de lançar o Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  instalado e em execução. No Windows, a stack do Agent Canvas é executada a
  partir da imagem Docker publicada, que inclui o Node.js, o `uv` e o pacote
  `@openhands/agent-canvas`, pelo que não é necessário instalá-los na máquina
  anfitriã.
<!-- @os:end -->

- Uma pasta de projeto para trabalhar. Pode ser qualquer repositório git local
  ou diretório de código no qual pretenda que o agente trabalhe.

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

Inicie o modelo a partir da CLI do Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Escolha um modelo adequado ao seu hardware.** O `Qwen3.6-35B-A3B-GGUF` (~20 GB) é um modelo de codificação sólido, mas precisa de um conjunto de memória grande. Se o seu dispositivo tiver memória ou VRAM da GPU limitada, escolha antes um modelo GGUF mais pequeno da biblioteca de modelos do Lemonade e utilize esse ID de modelo ao longo deste guia prático.

> **Nota:** O primeiro `lemonade run` descarrega o modelo caso ainda não esteja presente, o que pode demorar algum tempo consoante o tamanho do modelo e a sua ligação.

O Lemonade expõe uma API compatível com OpenAI em:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Verificar o Modelo Local

Confirme que o Lemonade consegue disponibilizar o modelo selecionado:

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
Instale globalmente o pacote publicado do Agent Canvas:

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

De seguida, inicie a stack completa a partir de um terminal:

```bash
agent-canvas
```

Por predefinição, o Agent Canvas inicia em `http://localhost:8000`. Abra esse
URL no seu navegador. A porta não tem nada de especial — se a 8000 já estiver
em utilização, indique qualquer porta livre com `--port` (ou `-p`) ao iniciar
o Agent Canvas:

```bash
agent-canvas --port 3000
```

Depois abra `http://localhost:3000` em vez disso. O backend local predefinido
deverá aparecer como saudável no ecrã inicial.

O comando `agent-canvas` inicia em conjunto o servidor do agente, o backend de
automação e o frontend web. Só precisa deste único comando para executar o
OpenHands localmente.

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
No Windows, execute a imagem de contentor publicada do Agent Canvas com o
Docker Desktop. A imagem inclui o Agent Server, o backend de automação e o
frontend web, pelo que não é necessário instalar Node.js, `uv`, nem a CLI no
anfitrião.

Primeiro, crie as pastas de configuração e de workspace que o contentor monta:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Faça o pull da imagem publicada (é pública, pelo que não é necessário iniciar
sessão):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

De seguida, inicie a stack:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Abra `http://localhost:8000/canvas` no seu navegador. Se a porta 8000 já
estiver em utilização, mapeie uma porta de anfitrião diferente, por exemplo
`-p 8080:8000`, e abra `http://localhost:8080/canvas` em vez disso.

> **Nota:** O primeiro arranque inicializa o Agent Server dentro do
> contentor, pelo que pode demorar um ou dois minutos até o backend reportar
> estado saudável.

O ponto de montagem `.openhands` mantém o seu perfil de LLM e as definições
entre reinícios do contentor. O restante deste manual configura tudo através
da interface do Agent Canvas no seu navegador.

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

No primeiro arranque, o Agent Canvas abre um fluxo de integração. Nesse fluxo:

1. Mantenha **OpenHands** selecionado como agente e clique em **Next**.
2. Em **Set up your LLM**, selecione **Advanced**.
3. Mantenha **Authentication** definido como **API key**.
4. Defina **Custom Model** como `openai/Qwen3.6-35B-A3B-GGUF`.
5. Defina **Base URL** como `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > No Windows, a stack é executada num contentor, que não consegue aceder
   > ao anfitrião em `127.0.0.1`. Utilize antes
   > `http://host.docker.internal:13305/api/v1` para que o agente em
   > contentor consiga aceder ao Lemonade em execução no anfitrião Windows.
   <!-- @os:end -->
6. Em **API Key**, introduza qualquer valor de marcador de posição não vazio,
   como `lemonade-local`. O Lemonade não exige uma chave real, mas o cliente
   OpenHands precisa de um valor para enviar.
7. Clique em **Next**.

As definições Advanced concluídas devem ter este aspeto. O campo da chave de
API é ocultado pela interface.

![Definições avançadas de LLM do Agent Canvas na primeira utilização, com o modelo Lemonade e o URL base local](assets/01-llm-advanced-settings.png)

O Agent Canvas guarda estes valores como um perfil de LLM. Se a sua versão
lhe pedir para atribuir um nome a esse perfil, use um nome sem espaços, como
`lemonade-local`. Se mudar de modelo mais tarde, abra **Settings > LLM** e
atualize os mesmos campos Advanced. Pode alternar entre perfis guardados a
partir da caixa de introdução do chat com o comando `/model`.

## 5. Abrir um Workspace

O agente só pode ler e modificar ficheiros dentro de um workspace escolhido
por si. Antes de iniciar uma tarefa, aponte o Agent Canvas para a sua pasta de
projeto:

1. No ecrã inicial, escolha **Open Workspace**.
2. Selecione a pasta que contém o seu projeto (por exemplo, um repositório
   git no qual quer que o agente trabalhe).
3. Inicie uma nova conversa nesse workspace.

Tudo o que o agente faz — ler ficheiros, executar comandos, editar código —
está delimitado a esse workspace.

![Ecrã inicial do Agent Canvas após a integração](assets/02-agent-canvas-home.png)

## 6. Executar a Sua Primeira Tarefa de Programação

Com o workspace aberto e o LLM local selecionado, escreva uma tarefa concreta
no chat. Uma boa primeira tarefa é pequena e verificável, por exemplo:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Observe a linha temporal da conversa. O OpenHands irá:

- Ler o workspace para compreender a estrutura.
- Criar o ficheiro `hello.py` com a função pedida e o bloco de teste.
- Opcionalmente, executar `python3 hello.py` para verificar o resultado.
- Reportar o que fez e qualquer resultado de comandos no chat.

Deverá ver o novo ficheiro a aparecer no workspace, e a mensagem final do
agente deverá descrever a alteração que fez. Este é o momento de recompensa:
o agente escreveu e executou código real na sua pasta de projeto.

## 7. Rever e Orientar o Agente

Depois de o agente concluir um passo, reveja o seu trabalho antes de aceitar
o passo seguinte:

- **Alterações de ficheiros**: utilize o navegador de ficheiros do workspace
  ou a vista de diferenças do agente para ver exatamente o que foi
  adicionado, alterado ou eliminado.
- **Resultado de comandos**: expanda qualquer comando executado pelo agente
  para ver o stdout, o stderr e o código de saída.
- **Acompanhamento**: se o resultado não for o que pretendia, responda na
  mesma conversa com uma correção. O agente mantém o contexto anterior e itera
  sobre os mesmos ficheiros.

Por exemplo, se o teste não imprimir a saudação esperada, responda:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

O agente voltará a ler o ficheiro, executará o comando, diagnosticará o
problema e voltará a editar o ficheiro — tudo na mesma conversa.
## Resolução de problemas

<!-- @os:linux -->
- **`agent-canvas` não está no PATH:** reinstale com
  `npm install -g @openhands/agent-canvas` e confirme se o diretório binário global do npm
  está no PATH antes de `agent-canvas` poder ser iniciado a partir de um novo
  terminal.
- **`npm install -g` falha com um erro de permissões:** configure um diretório
  global do npm pertencente ao utilizador, depois reabra o terminal e instale o Agent Canvas novamente.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` está em falta:** instale-o a partir de
  [the uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).
  O Agent Canvas usa o `uv` para gerir o ambiente Python do servidor do agente.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` ou `docker run` falha ao ligar:** certifique-se de que o Docker Desktop
  está em execução (o ícone da baleia está na bandeja do sistema) e que o motor terminou
  de iniciar. `docker version` deve imprimir tanto a secção Client como a Server.
- **O contentor inicia mas o backend nunca fica saudável:** o primeiro
  arranque inicializa o Agent Server dentro do contentor; dê-lhe um ou dois minutos,
  depois verifique `docker logs <container>` para erros.
- **O contentor não consegue alcançar o Lemonade:** o contentor alcança o anfitrião através de
  `host.docker.internal`. Confirme que o Lemonade está a servir no anfitrião Windows com
  `lemonade status`, e utilize `http://host.docker.internal:13305/api/v1` como o
  URL Base ao configurar o LLM.
<!-- @os:end -->

- **A UI carrega mas o backend aparece como não saudável:** aguarde um ou dois minutos para que
  o agent server termine de iniciar, depois atualize a página. Se continuar não saudável, reinicie
  a stack e verifique os registos para erros.
- **Os pedidos de chat do Lemonade falham com um erro de ligação:** confirme que
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` é bem-sucedido e que
  o Lemonade continua a servir o modelo com `lemonade status`.
- **O agente apresenta um erro de comprimento de contexto ou limite de tokens:** inicie uma
  conversa nova para que o agente não transporte um histórico demasiado grande. Se
  continuar a acontecer, reinicie o Lemonade com um `ctx_size` maior do que o predefinido
  65536 (por exemplo `ctx_size=131072`), consoante a memória disponível.
- **O agente produz edições de baixa qualidade ou incompletas:** mude para um modelo
  maior no Lemonade, ou dê ao agente uma tarefa mais pequena e concreta e deixe-o
  terminar antes de pedir a próxima alteração.

## Próximos passos

- Experimente uma tarefa maior no mesmo espaço de trabalho, como adicionar um ficheiro de teste unitário ou
  corrigir um erro conhecido, e reveja as diferenças (diff) do agente antes de manter a alteração.
- Ligue um servidor MCP como o GitHub ou o Slack em **Customize** para que o
  agente possa ler issues ou publicar atualizações enquanto trabalha.
- Guarde vários perfis de LLM (um modelo pequeno e rápido e um modelo grande e mais potente) e
  alterne entre eles com `/model` a meio da conversa.
- Avance para [OpenHands automations](https://docs.openhands.dev/openhands/usage/automations/overview) para
  transformar ciclos de desenvolvimento recorrentes em execuções de agente agendadas ou acionadas por eventos.

## Recursos

- [OpenHands documentation](https://docs.openhands.dev/)
- [Agent Canvas overview](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvas setup](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM profiles and model configuration](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Lemonade Server documentation](https://lemonade-server.ai/docs)

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