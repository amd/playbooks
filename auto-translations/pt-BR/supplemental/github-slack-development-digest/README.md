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
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Visão Geral

Os desenvolvedores gastam muito tempo em pequenos ciclos recorrentes: revisar pull requests rotuladas, responder comentários no GitHub, triar novas issues, transformar threads do Slack em notas de standup ou acompanhamentos de incidentes, e acompanhar sinais de lançamento ou pesquisa.
Cada ciclo é familiar, mas ainda exige julgamento: reunir o contexto certo, decidir o que importa e publicar uma atualização clara onde a equipe já trabalha.

[Automações do OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) transformam esses ciclos em conversas de agente agendadas ou acionadas por eventos: execuções em que um agente de software de IA pode ler contexto, chamar ferramentas e produzir uma atualização.
Os templates de automação compartilhados no catálogo de extensões do OpenHands seguem esse padrão para revisão de pull requests do GitHub, monitoramento de repositórios, triagem de issues do Linear, retrospectivas de incidentes, digests de standup do Slack e resumos de pesquisa: uma automação é acionada, usa integrações configuradas como GitHub ou Slack para buscar contexto, raciocina sobre esse contexto com um modelo de linguagem grande (LLM) e grava um resultado de volta.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) é o plano de controle local para construir e testar essas automações.
Neste guia prático, ele executa um OpenHands Agent Server, o processo de backend que executa as conversas do agente, e conecta o agente a serviços externos como GitHub e Slack.

Para manter o fluxo de trabalho no seu sistema AMD, o agente se comunica com um modelo local servido pelo Lemonade Server.
O Lemonade expõe esse modelo por meio de uma API compatível com OpenAI, de modo que o Agent Canvas pode configurá-lo como um endpoint remoto no estilo OpenAI, enquanto o modelo, o prompt e o contexto do fluxo de trabalho permanecem locais.

Neste guia prático, você construirá uma automação concreta: um digest agendado de desenvolvimento de GitHub para Slack.
Ele usa o GitHub para inspecionar a atividade recente do repositório, o Slack para publicar o digest, chamadas de API do Agent Canvas para configurar e testar a automação, e o Lemonade para executar o LLM localmente.

![Diagrama de arquitetura mostrando GitHub MCP, automação do OpenHands, Lemonade Server e Slack MCP](assets/00-architecture-overview.png)

## O Que Você Vai Aprender

- Como iniciar o Lemonade Server e verificar se um modelo local responde a solicitações de chat
- Como iniciar o Agent Canvas e apontar seu Agent Server para um LLM local
- Como instalar servidores do Model Context Protocol (MCP) do GitHub e do Slack por meio da API do Agent Server
- Como criar e disparar uma automação agendada do OpenHands que publica um digest de desenvolvimento no Slack
- Como solucionar as falhas mais comuns de modelo local e de automação

## Conceitos Principais

| Conceito | O que é | Onde se encaixa neste guia prático |
| --- | --- | --- |
| Lemonade Server | Uma plataforma de serviço de LLM local criada para hardware AMD que expõe uma API compatível com OpenAI. Seus dados nunca saem da sua máquina. | Executa o modelo que alimenta o agente. |
| OpenHands Agent Server | O processo de backend que executa as conversas do agente OpenHands. | Hospeda o agente, seu perfil de LLM e seus servidores MCP. |
| Agent Canvas | O plano de controle local para o OpenHands que executa o Agent Server e uma interface para inspecionar execuções do agente. | Inicia os backends e fornece a API que você chama. |
| Servidor MCP | Um servidor Model Context Protocol que fornece a um agente ferramentas para um serviço externo, como GitHub ou Slack. | Permite que o agente leia o GitHub e escreva no Slack. |
| Automação do OpenHands | Uma conversa de agente agendada ou acionada por eventos que busca contexto, raciocina sobre ele e grava um resultado em algum lugar. | O digest de GitHub para Slack que você constrói aqui. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Fluxos de trabalho de agente de codificação se beneficiam de um modelo e uma janela de contexto maiores.
> Use pelo menos 32 GB de memória do sistema e prefira 64 GB ou mais para modelos GGUF maiores.
<!-- @device:end -->

## Definindo a Configuração de Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verifique Se Há Atualizações de Software

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

Você precisa de:

- Lemonade Server instalado seguindo o [guia de instalação padrão do Lemonade](https://lemonade-server.ai/docs/guide/install/).

<!-- @os:linux -->
- Node.js 22.12 ou posterior e `npm`, usados para instalar o CLI publicado do Agent Canvas e executar servidores MCP com `npx`.
- `uv`, o gerenciador de pacotes Python que o Agent Canvas usa para construir o ambiente do Agent Server. Se ainda não estiver instalado, instale-o a partir do [guia de instalação do uv](https://docs.astral.sh/uv/getting-started/installation/).
- Um pacote `@openhands/agent-canvas` publicado recente, com configurações de agente orientadas por esquema, `LLMSummarizingCondenserSettings.max_tokens` e suporte a `custom_tokenizer` de LLM.
- O pacote Python `transformers` disponível no ambiente do Agent Server. Ele é necessário para a contagem de tokens de modelo de chat quando `custom_tokenizer` está definido.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop para Windows](https://docs.docker.com/desktop/setup/install/windows-install/), instalado e em execução. No Windows, a pilha do Agent Canvas é executada a partir da imagem Docker publicada, que empacota Node.js, `uv`, `transformers` e o pacote `@openhands/agent-canvas`, para que você não precise instalá-los na máquina host.
<!-- @os:end -->

- Um token do GitHub com acesso de leitura ao repositório que você deseja resumir.
- Um token de bot do Slack (`xoxb-...`) com acesso `chat:write` e acesso de leitura ao canal.
- Um ID de equipe do Slack (`T...`).
- Um ID de canal do Slack (`C...`) onde o digest deve ser publicado.

Convide o aplicativo do Slack para o canal de destino antes de testar a automação.
## Variáveis Usadas Neste Playbook

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

Essas duas variáveis são usadas pelos comandos de verificação abaixo.
O modelo, o tokenizador e as outras configurações de LLM são inseridos diretamente na interface do Agent Canvas em etapas posteriores, portanto seus valores literais são mostrados em linha onde você precisar deles.

Os valores a seguir são inseridos na interface do Agent Canvas em etapas posteriores.
Defina-os aqui para que você possa copiá-los posteriormente:

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

Use um valor explícito `owner/repo` para `GITHUB_REPO_FILTER`.
Curingas amplos de organização podem retornar contexto MCP demais para modelos locais.

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

> **Escolha um modelo que seja compatível com seu hardware.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) é um modelo robusto para este fluxo de trabalho, mas precisa de um pool de memória grande.
> Se o seu dispositivo tiver memória ou VRAM de GPU limitada, escolha um modelo GGUF menor na biblioteca de modelos do Lemonade e use esse ID de modelo (e seu tokenizador correspondente) ao longo deste playbook.

> **Nota:** O primeiro `lemonade run` baixa o modelo caso ele ainda não esteja presente, o que pode levar algum tempo dependendo do tamanho do modelo e da sua conexão.

O Lemonade expõe uma API compatível com a OpenAI em:

```text
http://127.0.0.1:13305/api/v1
```

Opcional: se o Agent Canvas ou o executor de automação não estiverem na mesma máquina, publique o endpoint do Lemonade por meio de um túnel seguro e use a URL HTTPS como a URL base do LLM.
O [ngrok](https://ngrok.com/) expõe uma porta local para a internet por meio de uma URL HTTPS segura; ele requer uma conta gratuita do ngrok, e você substitui `YOUR_NGROK_DOMAIN.ngrok-free.dev` pelo seu próprio domínio reservado:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Verificar o Modelo Local

Confirme que o Lemonade pode servir o modelo selecionado:

<!-- @os:linux -->
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
<!-- @os:end -->

<!-- @os:windows -->
```powershell
curl.exe -s "$env:LEMONADE_BASE_URL/models"
```

Em seguida, envie uma pequena solicitação de chat:

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
Instale o pacote publicado do Agent Canvas e inicie a pilha completa:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Se a instalação global do npm falhar com um erro de permissão, consulte a entrada de solução de problemas de permissões do npm abaixo.

Por padrão, o Agent Canvas é iniciado em `http://localhost:8000`.
Abra essa URL em seu navegador.
A porta não é especial—se a 8000 já estiver em uso, passe qualquer porta livre com `--port` (ou `-p`).
O backend local padrão deve aparecer como saudável na tela inicial.

> **Nota:** O primeiro lançamento constrói o ambiente Python gerenciado por `uv` do Agent Server, então pode levar alguns minutos antes que o backend reporte como saudável.

O comando `agent-canvas` inicia o servidor de agente, o backend de automação e o frontend web juntos.
Você só precisa deste único comando para executar o OpenHands localmente.
O restante deste playbook configura tudo por meio da interface do Agent Canvas no seu navegador.
<!-- @os:end -->

<!-- @os:windows -->
No Windows, execute a imagem de container publicada do Agent Canvas com o Docker Desktop.
A imagem empacota o Agent Server, o backend de automação e o frontend web, então você não instala Node.js, `uv` ou a CLI na máquina host.

Primeiro, crie as pastas de configuração e de espaço de trabalho que o container monta:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Baixe a imagem publicada (cerca de 6 GB; ela é pública, então não é necessário login):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Em seguida, inicie a pilha:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Abra `http://localhost:8000/canvas` em seu navegador.
Se a porta 8000 já estiver em uso, mapeie uma porta de host diferente, por exemplo `-p 8080:8000`, e abra `http://localhost:8080/canvas` em vez disso.

> **Nota:** O primeiro lançamento constrói o ambiente do Agent Server dentro do container, então pode levar alguns minutos antes que o backend reporte como saudável.

A montagem `.openhands` persiste seu perfil de LLM, servidores MCP e automações entre reinicializações do container.
O restante deste playbook configura tudo por meio da interface do Agent Canvas no seu navegador em `http://localhost:8000/canvas`.
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
## 4. Configurar o LLM Local na UI

Na primeira execução, o Agent Canvas abre um fluxo de integração (onboarding).
Nesse fluxo:

1. Mantenha **OpenHands** selecionado como o agente e clique em **Next**.
2. Em **Set up your LLM**, selecione **Advanced**.
3. Mantenha **Authentication** definido como **API key**.
4. Defina **Custom Model** como `openai/Qwen3.6-35B-A3B-GGUF`.
5. Defina **Base URL** como `http://127.0.0.1:13305/api/v1`.
6. Em **API Key**, insira qualquer valor de espaço reservado não vazio, como `lemonade-local`. O Lemonade não exige uma chave real, mas o cliente OpenHands precisa de um valor para enviar.

<!-- @os:windows -->
> **Windows (Docker):** o Agent Server é executado dentro do contêiner, então defina **Base URL** como `http://host.docker.internal:13305/api/v1` em vez de `http://127.0.0.1:13305/api/v1`.
> De dentro do contêiner, `127.0.0.1` é o próprio contêiner; `host.docker.internal` alcança o Lemonade em execução no host Windows, e o Docker Desktop fornece esse nome de host automaticamente.
<!-- @os:end -->

Os campos de conexão devem ficar assim.
O campo de chave de API é mascarado pela UI.

![Configurações avançadas de LLM na primeira utilização do Agent Canvas com o modelo Lemonade e a URL base local](assets/01-llm-advanced-settings.png)

Em seguida, selecione **All** e defina os campos extras de modelo local:

1. Role até **Custom Tokenizer** e defina-o como `Qwen/Qwen3.6-35B-A3B`.
2. Role até **LiteLLM Extra Body** e defina-o como `{"enable_thinking": true}`.
3. Clique em **Next**.

![Aba All de LLM na primeira utilização do Agent Canvas com o tokenizador personalizado Qwen](assets/02-llm-all-tokenizer-settings.png)

![Aba All de LLM na primeira utilização do Agent Canvas com o corpo extra do LiteLLM configurado](assets/03-llm-all-extra-body-settings.png)

As configurações de LLM devem mostrar:

| Campo | Valor |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

O prefixo `openai/` informa ao LiteLLM para usar a formatação de requisição compatível com OpenAI contra o endpoint do Lemonade.
O tokenizador personalizado é o tokenizador original do Hugging Face para o modelo GGUF; ele permite que o OpenHands conte os mesmos tokens de modelo de chat (chat-template) que o servidor de modelo local vê.
O formulário atual de LLM de primeiro uso não mostra configurações de condensador (condenser).
Se o seu build do Agent Canvas expuser configurações de condensador mais tarde em **Settings > LLM**, use `llm_summarizing` e defina o máximo de tokens abaixo da janela de contexto do Lemonade, como `56000`.

## 5. Instalar os Servidores MCP do GitHub e do Slack

Na UI do Agent Canvas, abra **Customize** (ou **Settings > MCP**) para adicionar os servidores MCP que dão ao agente ferramentas para o GitHub e o Slack.
Os valores de token são enviados apenas ao seu Agent Server local e são persistidos como configurações criptografadas.

<!-- @os:windows -->
> **Windows (Docker):** os comandos de servidor MCP `npx` abaixo são executados dentro do contêiner, que já inclui o Node.js, então nada extra é instalado no host.
> Como `.openhands` está montado, os servidores MCP e seus tokens persistem entre reinicializações do contêiner.
<!-- @os:end -->

### Servidor MCP do GitHub

Adicione um novo servidor MCP com estas configurações:

| Campo | Valor |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = seu token do GitHub |

Use um token do GitHub com acesso de leitura ao repositório que você deseja resumir.

### Servidor MCP do Slack

Adicione um segundo servidor MCP com estas configurações:

| Campo | Valor |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = o ID do canal de resumo (digest) |

Defina `SLACK_CHANNEL_IDS` como o ID do canal de resumo (digest) (o mesmo valor que `SLACK_DIGEST_CHANNEL`) para que o agente não precise percorrer todos os canais do Slack.

Depois de adicionar os dois servidores, use o botão **Test** em cada um deles para confirmar que ele se conecta e anuncia ferramentas.
O servidor do GitHub deve listar ferramentas do GitHub, e o servidor do Slack deve listar ferramentas do Slack.

![Página MCP do Agent Canvas com os servidores GitHub e Slack instalados](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Criar a Automação de Resumo (Digest)

Na UI do Agent Canvas, abra a página **Automations** e crie uma nova automação:

1. Escolha **Create automation** e selecione o tipo **Prompt preset**.
2. Defina **Name** como `GitHub Development Digest to Slack`.
3. Defina **Prompt** com o texto a seguir, substituindo os espaços reservados de repositório e canal pelos seus valores:

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

4. Defina **Trigger** como **Cron** com a programação `0 9 * * 1-5` (9h em dias úteis) e defina **Timezone** como seu fuso horário, por exemplo `America/New_York`.
5. Defina **Timeout** como `900` segundos.
6. Salve a automação.

A página de detalhes da automação mostra a nova automação com seu gatilho cron e o ponto de entrada de prompt preset gerado.

![Página de detalhes da automação do Agent Canvas após a criação](assets/05-automation-created.png)
## 7. Teste a Automação

Na página de detalhes da automação no Agent Canvas UI:

1. Clique em **Run now** (ou **Dispatch**) para executar a automação imediatamente, uma única vez.
2. Observe a lista de execuções na mesma página. A execução mais recente deve passar para `COMPLETED`.
3. Abra o canal do Slack de destino. Ele deve conter o digest gerado.

Não é necessário esperar o cron schedule disparar—**Run now** aciona uma execução sob demanda para que você possa confirmar que o prompt, as conexões MCP e a publicação no Slack funcionam corretamente antes de depender do agendamento.

![Execução de automação concluída com sucesso no Agent Canvas](assets/06-automation-run-completed.png)

![Canal do Slack exibindo o digest do OpenHands gerado](assets/07-slackbot-message.png)

## Solução de Problemas

<!-- @os:windows -->
- **A porta 8000 do Docker já está em uso:** mapeie uma porta de host diferente, por exemplo `docker run ... -p 8080:8000 ...`, e abra `http://localhost:8080/canvas`.
- **`docker pull` falha com um erro de credencial** (por exemplo, "A specified logon session does not exist"): execute o pull a partir de uma sessão interativa do Windows, ou faça o pré-pull da imagem. A imagem é pública, portanto nenhum `docker login` é necessário.
- **A UI carrega, mas o backend está instável:** a primeira inicialização constrói o ambiente do Agent Server dentro do contêiner. Aguarde um minuto e atualize a página, depois verifique `docker logs <container>` para acompanhar o progresso.
- **O Agent Canvas não consegue alcançar o Lemonade a partir do contêiner:** defina o **Base URL** do LLM como `http://host.docker.internal:13305/api/v1` (e não `127.0.0.1`), e confirme que o Lemonade está em execução no host Windows.
<!-- @os:end -->

- **O Lemonade está parado:** reinicie-o com o comando `lemonade run "${LEMONADE_MODEL}"` na etapa 1, depois execute novamente a verificação de integridade.
- **`npm install -g` falha com um erro de permissão:** no Linux ou WSL, configure um diretório global do npm pertencente ao usuário, adicione-o ao arquivo de inicialização do shell e instale o Agent Canvas novamente:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Se você usa `zsh`, adicione a mesma linha `export PATH=...` em `~/.zshrc` em vez de `~/.bashrc`.
- **O Agent Canvas rejeita as configurações do LLM após definir `custom_tokenizer`:** instale `transformers` no ambiente Python do Agent Server, reinicie o Agent Canvas se necessário e tente salvar novamente as configurações do LLM. O OpenHands requer o Transformers para carregar o template de chat do tokenizer quando `custom_tokenizer` está definido.
- **O Agent Canvas não consegue alcançar o Lemonade:** verifique `curl -fsS "${LEMONADE_BASE_URL}/health"` e confirme se o base URL inserido no formulário de LLM de primeiro uso ou em **Settings > LLM** corresponde ao endpoint local em execução ou ao túnel HTTPS.
- **As configurações do LLM não foram salvas:** certifique-se de ter clicado em **Next** após inserir os valores. Reabra **Settings > LLM** para confirmar que os valores persistiram.
- **O GitHub MCP não consegue ver repositórios privados:** confirme que o token do GitHub tem acesso de leitura ao repositório de destino e que o botão **Test** do MCP em **Customize** exibe as ferramentas do GitHub.
- **O Slack consegue ler canais, mas não consegue postar:** convide o app do Slack para o canal de destino e confirme que o bot possui `chat:write`.
- **A automação lista canais do Slack demais:** use um ID de canal do Slack e defina `SLACK_CHANNEL_IDS` no servidor Slack MCP em **Customize**.
- **A execução da automação falha ou excede o contexto:** confirme que o Lemonade foi iniciado com `ctx_size=65536`, confirme que o LLM do OpenHands tem `custom_tokenizer` definido, e use um repositório explícito com conjuntos de resultados do GitHub limitados a 3 a 5 itens. Se o seu build do Agent Canvas expuser configurações de condenser, defina o máximo de tokens do condenser abaixo da janela de contexto do Lemonade.

## Próximos Passos

- Adicione um digest semanal apenas para releases.
- Adicione uma automação acionada por evento do GitHub para alertas mais rápidos de PR ou push.
- Direcione o mesmo digest para o Notion, Linear ou outra ferramenta com suporte a MCP.

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