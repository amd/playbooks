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
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Visão Geral

Os programadores despendem muito tempo em pequenos ciclos recorrentes: rever pull requests etiquetadas, responder a comentários no GitHub, triar novos issues, transformar threads do Slack em notas de standup ou acompanhamentos de incidentes, e acompanhar sinais de lançamentos ou de investigação.
Cada ciclo é familiar, mas continua a exigir discernimento: reunir o contexto certo, decidir o que importa e publicar uma atualização clara onde a equipa já trabalha.

As [automações do OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) transformam esses ciclos em conversas de agente acionadas por agendamento ou por eventos: execuções em que um agente de software de IA pode ler contexto, invocar ferramentas e produzir uma atualização.
Os modelos de automação partilhados no catálogo de extensões do OpenHands seguem este padrão para revisão de pull requests do GitHub, monitorização de repositórios, triagem de issues do Linear, retrospetivas de incidentes, resumos diários de standup no Slack e sínteses de investigação: uma automação é acionada, utiliza integrações configuradas como o GitHub ou o Slack para obter contexto, raciocina sobre esse contexto com um modelo de linguagem de grande dimensão (LLM) e escreve de volta um resultado.

O [Agent Canvas](https://github.com/OpenHands/agent-canvas) é o plano de controlo local para criar e testar essas automações.
Neste guia, executa um OpenHands Agent Server, o processo de backend que executa as conversas do agente, e liga o agente a serviços externos como o GitHub e o Slack.

Para manter o fluxo de trabalho no seu sistema AMD, o agente comunica com um modelo local servido pelo Lemonade Server.
O Lemonade expõe esse modelo através de uma API compatível com OpenAI, pelo que o Agent Canvas o pode configurar como se fosse um endpoint remoto no estilo OpenAI, enquanto o modelo, o prompt e o contexto do fluxo de trabalho permanecem locais.

Neste guia, vai criar uma automação concreta: um resumo diário de desenvolvimento do GitHub para o Slack, agendado.
Utiliza o GitHub para inspecionar a atividade recente do repositório, o Slack para publicar o resumo, chamadas à API do Agent Canvas para configurar e testar a automação, e o Lemonade para executar o LLM localmente.

![Diagrama de arquitetura a mostrar GitHub MCP, automação do OpenHands, Lemonade Server e Slack MCP](assets/00-architecture-overview.png)

## O Que Vai Aprender

- Como iniciar o Lemonade Server e verificar se um modelo local responde a pedidos de chat
- Como iniciar o Agent Canvas e apontar o respetivo Agent Server para um LLM local
- Como instalar servidores Model Context Protocol (MCP) do GitHub e do Slack através da API do Agent Server
- Como criar e despoletar uma automação agendada do OpenHands que publica um resumo de desenvolvimento no Slack
- Como resolver as falhas mais comuns de modelos locais e de automações

## Conceitos Fundamentais

| Conceito | O que é | Onde se encaixa neste guia |
| --- | --- | --- |
| Lemonade Server | Uma plataforma local de disponibilização de LLMs construída para hardware AMD, que expõe uma API compatível com OpenAI. Os seus dados nunca saem da sua máquina. | Executa o modelo que alimenta o agente. |
| OpenHands Agent Server | O processo de backend que executa as conversas de agente do OpenHands. | Aloja o agente, o seu perfil de LLM e os seus servidores MCP. |
| Agent Canvas | O plano de controlo local para o OpenHands que executa o Agent Server e uma interface para inspecionar execuções do agente. | Inicia os backends e disponibiliza a API que invoca. |
| Servidor MCP | Um servidor Model Context Protocol que fornece a um agente ferramentas para um serviço externo como o GitHub ou o Slack. | Permite que o agente leia o GitHub e escreva no Slack. |
| Automação do OpenHands | Uma conversa de agente acionada por agendamento ou por eventos que obtém contexto, raciocina sobre ele e escreve um resultado algures. | O resumo do GitHub para o Slack que cria aqui. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Os fluxos de trabalho de agentes de programação beneficiam de um modelo e de uma janela de contexto maiores.
> Utilize pelo menos 32 GB de memória do sistema e prefira 64 GB ou mais para modelos GGUF maiores.
<!-- @device:end -->

## Definir a Configuração de Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software

<!-- @require:software-update -->
<!-- @device:end -->

## Pré-requisitos

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

Precisa de:

- Lemonade Server instalado seguindo o [guia de instalação do Lemonade](https://lemonade-server.ai/docs/guide/install/) padrão.

<!-- @os:linux -->
- Node.js 22.12 ou posterior e `npm`, utilizados para instalar o CLI publicado do Agent Canvas e executar servidores MCP com `npx`.
- `uv`, o gestor de pacotes Python que o Agent Canvas utiliza para construir o ambiente do Agent Server. Se ainda não estiver instalado, instale-o a partir do [guia de instalação do uv](https://docs.astral.sh/uv/getting-started/installation/).
- Um pacote `@openhands/agent-canvas` publicado recente, com definições de agente orientadas por esquema, `LLMSummarizingCondenserSettings.max_tokens`, e suporte para `custom_tokenizer` do LLM.
- O pacote Python `transformers` disponível no ambiente do Agent Server. É necessário para a contagem de tokens de modelos de chat quando `custom_tokenizer` está definido.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/), instalado e em execução. No Windows, a stack do Agent Canvas é executada a partir da imagem Docker publicada, que inclui o Node.js, o `uv`, o `transformers` e o pacote `@openhands/agent-canvas`, pelo que não precisa de os instalar no anfitrião.
<!-- @os:end -->

- Um token do GitHub com acesso de leitura ao repositório que pretende resumir.
- Um token de bot do Slack (`xoxb-...`) com acesso `chat:write` e de leitura de canais.
- Um ID de equipa do Slack (`T...`).
- Um ID de canal do Slack (`C...`) onde o resumo deve ser publicado.

Convide a aplicação do Slack para o canal de destino antes de testar a automação.
## Variáveis Utilizadas neste Playbook

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:LEMONADE_BASE_URL = "http://127.0.0.1:13305/api/v1"
$env:LEMONADE_MODEL = "Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

Estas duas variáveis são utilizadas pelos comandos de verificação abaixo.
O modelo, o tokenizer e outras definições do LLM são introduzidos diretamente na interface do Agent Canvas em passos posteriores, pelo que os seus valores literais são apresentados diretamente em linha onde são necessários.

Os seguintes valores são introduzidos na interface do Agent Canvas em passos posteriores.
Defina-os aqui para que os possa copiar posteriormente:

<!-- @os:linux -->
```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:GITHUB_REPO_FILTER = "your-org/your-repo"
$env:SLACK_DIGEST_CHANNEL = "C0123456789"
$env:DIGEST_TIMEZONE = "America/New_York"
```
<!-- @os:end -->

Utilize um valor explícito `owner/repo` para `GITHUB_REPO_FILTER`.
Caracteres universais (wildcards) de organizações demasiado abrangentes podem devolver demasiado contexto MCP para modelos locais.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Iniciar o Lemonade Server

Inicie o modelo a partir da CLI do Lemonade:

<!-- @os:linux -->
```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "$env:LEMONADE_MODEL"
```
<!-- @os:end -->

> **Escolha um modelo adequado ao seu hardware.** O `Qwen3.6-35B-A3B-GGUF` (~20 GB) é um modelo robusto para este fluxo de trabalho, mas necessita de um grande conjunto de memória.
> Se o seu dispositivo tiver memória ou VRAM de GPU limitadas, escolha um modelo GGUF mais pequeno da biblioteca de modelos do Lemonade e utilize esse ID de modelo (e o respetivo tokenizer correspondente) ao longo deste playbook.

> **Nota:** O primeiro `lemonade run` transfere o modelo caso ainda não esteja presente, o que pode demorar algum tempo dependendo do tamanho do modelo e da sua ligação.

O Lemonade expõe uma API compatível com OpenAI em:

```text
http://127.0.0.1:13305/api/v1
```

Opcional: se o Agent Canvas ou o executor de automação não estiverem na mesma máquina, publique o endpoint do Lemonade através de um túnel seguro e utilize o URL HTTPS como URL base do LLM.
O [ngrok](https://ngrok.com/) expõe uma porta local à internet através de um URL HTTPS seguro; requer uma conta ngrok gratuita, e deve substituir `YOUR_NGROK_DOMAIN.ngrok-free.dev` pelo seu próprio domínio reservado:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Verificar o Modelo Local

Confirme que o Lemonade consegue servir o modelo selecionado:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Em seguida, envie um pequeno pedido de chat:

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
<!-- @os:end -->

<!-- @os:windows -->
```powershell
curl.exe -s "$env:LEMONADE_BASE_URL/models"
```

Em seguida, envie um pequeno pedido de chat:

```powershell
$body = @{
  model    = "$env:LEMONADE_MODEL"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5
curl.exe -sS "$env:LEMONADE_BASE_URL/chat/completions" -H "Content-Type: application/json" -d $body
```
<!-- @os:end -->

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
entry = None
for item in data.get("data", []):
    if item.get("id") == "${lemonade_model}":
        entry = item
        break

if entry is None:
    print("Model ${lemonade_model} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: ${lemonade_model} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 64
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi
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

if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model    = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "digest-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
<!-- @os:end -->

## 3. Iniciar o Agent Canvas

<!-- @os:linux -->
Instale o pacote publicado do Agent Canvas e inicie a stack completa:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Se a instalação global do npm falhar com um erro de permissões, consulte a entrada de resolução de problemas de permissões do npm abaixo.

Por predefinição, o Agent Canvas inicia em `http://localhost:8000`.
Abra esse URL no seu navegador.
A porta não é especial—se a porta 8000 já estiver em utilização, indique qualquer porta livre com `--port` (ou `-p`).
O backend local predefinido deverá aparecer como saudável no ecrã inicial.

> **Nota:** O primeiro arranque constrói o ambiente Python gerido por `uv` do Agent Server, pelo que pode demorar alguns minutos até o backend reportar estar saudável.

O comando `agent-canvas` inicia em conjunto o agent server, o backend de automação e o frontend web.
Só precisa deste único comando para executar o OpenHands localmente.
O resto deste playbook configura tudo através da interface do Agent Canvas no seu navegador.
<!-- @os:end -->

<!-- @os:windows -->
No Windows, execute a imagem do contentor do Agent Canvas publicada com o Docker Desktop.
A imagem inclui o Agent Server, o backend de automação e o frontend web, pelo que não é necessário instalar o Node.js, o `uv` ou a CLI na máquina anfitriã.

Primeiro, crie as pastas de configuração e de espaço de trabalho que o contentor monta:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Faça o pull da imagem publicada (cerca de 6 GB; é pública, pelo que não é necessário iniciar sessão):

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

Abra `http://localhost:8000/canvas` no seu navegador.
Se a porta 8000 já estiver em utilização, mapeie uma porta de anfitrião diferente, por exemplo `-p 8080:8000`, e abra `http://localhost:8080/canvas` em vez disso.

> **Nota:** O primeiro arranque constrói o ambiente do Agent Server dentro do contentor, pelo que pode demorar alguns minutos até o backend reportar estar saudável.

A montagem `.openhands` mantém o seu perfil de LLM, servidores MCP e automações persistentes entre reinícios do contentor.
O resto deste playbook configura tudo através da interface do Agent Canvas no seu navegador em `http://localhost:8000/canvas`.
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=uv-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-version timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help
echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-start timeout=1200 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
log="/tmp/agent-canvas-test.log"
p=""
cleanup() {
  set +e
  for port in 8000 18000 18001 3001; do
    pid="$(ss -ltnp 2>/dev/null | grep ":$port " | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2)"
    [ -n "$pid" ] && kill "$pid" 2>/dev/null
  done
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null
    sleep 2
    kill -9 "$p" 2>/dev/null
  fi
}
# Preserve the real exit code; cleanup must never flip a pass to a fail (or vice versa).
trap 'rc=$?; cleanup; exit $rc' EXIT

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000 ingress root:
# the ingress serves the static frontend and returns 200 for / even when the agent-server is down.
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
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "digest-agent-canvas-ci"
$hostPort = 18080

# Pull the image if the runner doesn't already have it. The published image is
# public, so no login is needed. A non-interactive session can trip over a
# configured Docker credential helper (ghcr is unauthenticated here), so pull
# with an isolated, empty Docker config that has no credsStore/credHelpers.
# TODO: remove this self-provisioning once the runners ship the image by default.
$imgId = docker images -q $image
if (-not $imgId) {
  Write-Host "Image $image not present; pulling..."
  $dockerCfg = Join-Path $env:TEMP "digest-docker-cfg"
  New-Item -ItemType Directory -Force -Path $dockerCfg | Out-Null
  '{}' | Set-Content -Path (Join-Path $dockerCfg "config.json") -Encoding ascii
  docker --config $dockerCfg pull $image
  if ($LASTEXITCODE -ne 0) { throw "docker pull failed for $image" }
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
## 4. Configurar o LLM Local na Interface

No primeiro arranque, o Agent Canvas abre um fluxo de integração.
Nesse fluxo:

1. Mantenha **OpenHands** selecionado como agente e clique em **Next**.
2. Em **Set up your LLM**, selecione **Advanced**.
3. Mantenha **Authentication** definido como **API key**.
4. Defina **Custom Model** como `openai/Qwen3.6-35B-A3B-GGUF`.
5. Defina **Base URL** como `http://127.0.0.1:13305/api/v1`.
6. Em **API Key**, introduza qualquer valor de substituição não vazio, como `lemonade-local`. O Lemonade não requer uma chave real, mas o cliente OpenHands precisa de um valor para enviar.

<!-- @os:windows -->
> **Windows (Docker):** o Agent Server é executado dentro do contentor, pelo que deve definir **Base URL** como `http://host.docker.internal:13305/api/v1` em vez de `http://127.0.0.1:13305/api/v1`.
> A partir do interior do contentor, `127.0.0.1` refere-se ao próprio contentor; `host.docker.internal` permite aceder ao Lemonade em execução no anfitrião Windows, e o Docker Desktop fornece automaticamente esse nome de anfitrião.
<!-- @os:end -->

Os campos de ligação devem ter o seguinte aspeto.
O campo da chave de API é mascarado pela interface.

![Definições avançadas do LLM no primeiro uso do Agent Canvas com o modelo Lemonade e o URL base local](assets/01-llm-advanced-settings.png)

Depois selecione **All** e defina os campos adicionais para modelos locais:

1. Percorra até **Custom Tokenizer** e defina-o como `Qwen/Qwen3.6-35B-A3B`.
2. Percorra até **LiteLLM Extra Body** e defina-o como `{"enable_thinking": true}`.
3. Clique em **Next**.

![Separador All do LLM no primeiro uso do Agent Canvas com o tokenizador personalizado Qwen](assets/02-llm-all-tokenizer-settings.png)

![Separador All do LLM no primeiro uso do Agent Canvas com o corpo extra do LiteLLM configurado](assets/03-llm-all-extra-body-settings.png)

As definições do LLM devem mostrar:

| Campo | Valor |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

O prefixo `openai/` indica ao LiteLLM para usar a formatação de pedidos compatível com OpenAI em relação ao endpoint do Lemonade.
O tokenizador personalizado é o tokenizador original do Hugging Face para o modelo GGUF; permite que o OpenHands conte os mesmos tokens do modelo de template de conversação (chat-template) que o servidor de modelo local vê.
O formulário atual de LLM de primeiro uso não mostra definições de condensador (condenser).
Se a sua versão do Agent Canvas expuser mais tarde definições de condensador em **Settings > LLM**, utilize `llm_summarizing` e defina o número máximo de tokens abaixo da janela de contexto do Lemonade, como `56000`.

## 5. Instalar os Servidores MCP do GitHub e Slack

Na interface do Agent Canvas, abra **Customize** (ou **Settings > MCP**) para adicionar os servidores MCP que fornecem ao agente as ferramentas para GitHub e Slack.
Os valores dos tokens são enviados apenas para o seu Agent Server local e são guardados como definições encriptadas.

<!-- @os:windows -->
> **Windows (Docker):** os comandos do servidor MCP `npx` abaixo são executados dentro do contentor, que já inclui o Node.js, pelo que nada de adicional é instalado no anfitrião.
> Como `.openhands` está montado, os servidores MCP e os seus tokens persistem entre reinícios do contentor.
<!-- @os:end -->

### Servidor MCP do GitHub

Adicione um novo servidor MCP com estas definições:

| Campo | Valor |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = o seu token do GitHub |

Utilize um token do GitHub com acesso de leitura ao repositório que pretende resumir.

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

Defina `SLACK_CHANNEL_IDS` como o ID do canal de resumo (o mesmo valor que `SLACK_DIGEST_CHANNEL`) para que o agente não precise de percorrer todos os canais do Slack.

Depois de adicionar ambos os servidores, utilize o botão **Test** em cada um para confirmar que se liga e anuncia ferramentas.
O servidor do GitHub deve listar ferramentas do GitHub, e o servidor do Slack deve listar ferramentas do Slack.

![Página MCP do Agent Canvas com os servidores do GitHub e Slack instalados](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Criar a Automação do Resumo

Na interface do Agent Canvas, abra a página **Automations** e crie uma nova automação:

1. Escolha **Create automation** e selecione o tipo **Prompt preset**.
2. Defina o **Name** como `GitHub Development Digest to Slack`.
3. Defina o **Prompt** com o seguinte texto, substituindo os marcadores de repositório e canal pelos seus valores:

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

4. Defina o **Trigger** como **Cron** com o calendário `0 9 * * 1-5` (9h nos dias úteis) e defina o **Timezone** para o seu fuso horário, por exemplo `America/New_York`.
5. Defina o **Timeout** como `900` segundos.
6. Guarde a automação.

A página de detalhes da automação mostra a nova automação com o seu acionador cron e o ponto de entrada de prompt preset gerado.

![Página de detalhes da automação do Agent Canvas após a criação](assets/05-automation-created.png)
## 7. Testar a Automação

Na página de detalhe da automação na interface do Agent Canvas:

1. Clique em **Run now** (ou **Dispatch**) para executar a automação uma vez, de imediato.
2. Observe a lista de execuções na mesma página. A execução mais recente deverá transitar para `COMPLETED`.
3. Abra o seu canal Slack de destino. Deverá conter o resumo gerado.

Não precisa de esperar que o agendamento cron seja acionado — **Run now** aciona uma execução a pedido, para que possa confirmar que o prompt, as ligações MCP e a publicação no Slack funcionam todos antes de depender do agendamento.

![Execução da automação do Agent Canvas concluída com sucesso](assets/06-automation-run-completed.png)

![Canal Slack a mostrar o resumo OpenHands gerado](assets/07-slackbot-message.png)

## Resolução de Problemas

<!-- @os:windows -->
- **A porta 8000 do Docker já está em uso:** mapeie uma porta de anfitrião diferente, por exemplo `docker run ... -p 8080:8000 ...`, e abra `http://localhost:8080/canvas`.
- **O `docker pull` falha com um erro de credenciais** (por exemplo, "A specified logon session does not exist"): execute o pull a partir de uma sessão interativa do Windows, ou faça o pré-pull da imagem. A imagem é pública, pelo que não é necessário `docker login`.
- **A interface carrega mas o backend está não funcional:** o primeiro arranque cria o ambiente do Agent Server dentro do contentor. Aguarde um minuto e atualize, depois verifique `docker logs <container>` para ver o progresso.
- **O Agent Canvas não consegue alcançar o Lemonade a partir do contentor:** defina o **Base URL** do LLM para `http://host.docker.internal:13305/api/v1` (não `127.0.0.1`), e confirme que o Lemonade está em execução no anfitrião Windows.
<!-- @os:end -->

- **O Lemonade está parado:** reinicie-o com o comando `lemonade run "${LEMONADE_MODEL}"` no passo 1, depois volte a executar a verificação de estado.
- **O `npm install -g` falha com um erro de permissões:** no Linux ou WSL, configure um diretório global npm pertencente ao utilizador, adicione-o ao seu ficheiro de arranque da shell, depois instale novamente o Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Se utilizar `zsh`, adicione a mesma linha `export PATH=...` a `~/.zshrc` em vez de `~/.bashrc`.
- **O Agent Canvas rejeita as definições do LLM após definir `custom_tokenizer`:** instale `transformers` no ambiente Python do Agent Server, reinicie o Agent Canvas se necessário, e tente novamente guardar as definições do LLM. O OpenHands requer o Transformers para carregar o modelo de chat do tokenizer quando `custom_tokenizer` está definido.
- **O Agent Canvas não consegue alcançar o Lemonade:** verifique `curl -fsS "${LEMONADE_BASE_URL}/health"` e confirme que o base URL introduzido no formulário de LLM de primeira utilização ou em **Settings > LLM** corresponde ao endpoint local em execução ou ao túnel HTTPS.
- **As definições do LLM não foram guardadas:** certifique-se de que clicou em **Next** depois de introduzir os valores. Reabra **Settings > LLM** para confirmar que os valores persistiram.
- **O GitHub MCP não consegue ver repositórios privados:** confirme que o token do GitHub tem acesso de leitura ao repositório de destino e que o botão **Test** do MCP em **Customize** anuncia ferramentas do GitHub.
- **O Slack consegue ler canais mas não consegue publicar:** convide a aplicação Slack para o canal de destino e confirme que o bot tem `chat:write`.
- **A automação lista demasiados canais Slack:** utilize um ID de canal Slack e defina `SLACK_CHANNEL_IDS` no servidor MCP do Slack em **Customize**.
- **A execução da automação falha ou excede o contexto:** confirme que o Lemonade foi iniciado com `ctx_size=65536`, confirme que o LLM do OpenHands tem `custom_tokenizer` definido, e utilize um repositório explícito com os conjuntos de resultados do GitHub limitados a 3 a 5 itens. Se a sua compilação do Agent Canvas expuser definições de condensador, defina o número máximo de tokens do condensador abaixo da janela de contexto do Lemonade.

## Próximos Passos

- Adicionar um resumo semanal apenas de lançamentos.
- Adicionar uma automação acionada por eventos do GitHub para alertas mais rápidos de PR ou push.
- Encaminhar o mesmo resumo para o Notion, Linear, ou outra ferramenta suportada por MCP.

## Recursos

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Documentação do Lemonade Server](https://lemonade-server.ai/docs)
- [Repositório de extensões do OpenHands](https://github.com/OpenHands/extensions)
- [Servidores do Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Pacote Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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
try { lemonade unload } catch {}
```
<!-- @test:end -->
<!-- @os:end -->