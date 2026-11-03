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

Os programadores passam muito tempo em pequenos ciclos recorrentes: rever pull requests etiquetados, responder a comentários no GitHub, triar novos problemas (issues), transformar tópicos do Slack em notas de standup ou acompanhamentos de incidentes, e acompanhar sinais de lançamento ou de investigação.
Cada ciclo é familiar, mas continua a exigir juízo: reunir o contexto certo, decidir o que é importante e publicar uma atualização clara onde a equipa já trabalha.

As [automações do OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) transformam esses ciclos em conversas de agente agendadas ou acionadas por eventos: execuções em que um agente de software de IA pode ler contexto, chamar ferramentas e produzir uma atualização.
Os modelos de automação partilhados no catálogo de extensões do OpenHands seguem este padrão para revisão de pull requests do GitHub, monitorização de repositórios, triagem de problemas no Linear, retrospetivas de incidentes, resumos de standup no Slack e briefings de investigação: uma automação é ativada, utiliza integrações configuradas como o GitHub ou o Slack para obter contexto, raciocina sobre esse contexto com um modelo de linguagem de grande escala (LLM) e escreve um resultado de volta.

O [Agent Canvas](https://github.com/OpenHands/agent-canvas) é o plano de controlo local para criar e testar essas automações.
Neste guia, executa um OpenHands Agent Server, o processo de backend que executa as conversas do agente, e liga o agente a serviços externos como o GitHub e o Slack.

Para manter o fluxo de trabalho no seu sistema AMD, o agente comunica com um modelo local servido pelo Lemonade Server.
O Lemonade expõe esse modelo através de uma API compatível com OpenAI, pelo que o Agent Canvas o pode configurar como um endpoint remoto no estilo OpenAI, enquanto o modelo, o prompt e o contexto do fluxo de trabalho permanecem locais.

Neste guia, vai construir uma automação concreta: um resumo de desenvolvimento agendado de GitHub para Slack.
Utiliza o GitHub para inspecionar a atividade recente do repositório, o Slack para publicar o resumo, chamadas à API do Agent Canvas para configurar e testar a automação, e o Lemonade para executar o LLM localmente.

![Diagrama de arquitetura a mostrar o GitHub MCP, a automação do OpenHands, o Lemonade Server e o Slack MCP](assets/00-architecture-overview.png)

## O Que Vai Aprender

- Como iniciar o Lemonade Server e verificar se um modelo local responde a pedidos de chat
- Como iniciar o Agent Canvas e apontar o seu Agent Server para um LLM local
- Como instalar servidores Model Context Protocol (MCP) do GitHub e do Slack através da API do Agent Server
- Como criar e despoletar uma automação agendada do OpenHands que publica um resumo de desenvolvimento no Slack
- Como resolver os problemas mais comuns relacionados com o modelo local e com a automação

## Conceitos Fundamentais

| Conceito | O Que É | Onde Se Enquadra Neste Guia |
| --- | --- | --- |
| Lemonade Server | Uma plataforma local de serviço de LLM criada para hardware AMD que expõe uma API compatível com OpenAI. Os seus dados nunca saem da sua máquina. | Executa o modelo que alimenta o agente. |
| OpenHands Agent Server | O processo de backend que executa as conversas do agente OpenHands. | Aloja o agente, o seu perfil de LLM e os seus servidores MCP. |
| Agent Canvas | O plano de controlo local para o OpenHands que executa o Agent Server e uma UI para inspecionar as execuções do agente. | Inicia os backends e disponibiliza a API que utiliza. |
| Servidor MCP | Um servidor Model Context Protocol que fornece a um agente ferramentas para um serviço externo, como o GitHub ou o Slack. | Permite que o agente leia o GitHub e escreva no Slack. |
| Automação do OpenHands | Uma conversa de agente agendada ou acionada por eventos que obtém contexto, raciocina sobre ele e escreve um resultado algures. | O resumo de GitHub para Slack que vai construir aqui. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Os fluxos de trabalho de agentes de código beneficiam de um modelo maior e de uma janela de contexto maior.
> Utilize pelo menos 32 GB de memória do sistema e prefira 64 GB ou mais para modelos GGUF maiores.
<!-- @device:end -->

## Configurar a Memória

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

É necessário:

- O Lemonade Server instalado seguindo o [guia de instalação do Lemonade](https://lemonade-server.ai/docs/guide/install/) padrão.

<!-- @os:linux -->
- Node.js 22.12 ou posterior e `npm`, utilizados para instalar a CLI publicada do Agent Canvas e executar servidores MCP com `npx`.
- `uv`, o gestor de pacotes Python que o Agent Canvas utiliza para criar o ambiente do Agent Server. Se ainda não estiver instalado, instale-o a partir do [guia de instalação do uv](https://docs.astral.sh/uv/getting-started/installation/).
- Um pacote `@openhands/agent-canvas` publicado recentemente, com definições de agente baseadas em esquema, `LLMSummarizingCondenserSettings.max_tokens` e suporte para `custom_tokenizer` de LLM.
- O pacote Python `transformers` disponível no ambiente do Agent Server. É necessário para a contagem de tokens de modelos de chat (chat-template) quando `custom_tokenizer` está definido.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop para Windows](https://docs.docker.com/desktop/setup/install/windows-install/), instalado e em execução. No Windows, a stack do Agent Canvas é executada a partir da imagem Docker publicada, que inclui o Node.js, o `uv`, o `transformers` e o pacote `@openhands/agent-canvas`, pelo que não é necessário instalar estes componentes no anfitrião.
<!-- @os:end -->

- Um token do GitHub com acesso de leitura ao repositório que pretende resumir.
- Um token de bot do Slack (`xoxb-...`) com acesso `chat:write` e de leitura ao canal.
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
O modelo, o tokenizador e outras definições de LLM são introduzidos diretamente na interface do Agent Canvas UI em passos posteriores, pelo que os seus valores literais são apresentados diretamente onde são necessários.

Os seguintes valores são introduzidos na interface do Agent Canvas UI em passos posteriores.
Defina-os aqui para poder copiá-los mais tarde:

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
Wildcards amplos de organização podem devolver demasiado contexto MCP para modelos locais.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Iniciar o Lemonade Server

Inicie o modelo a partir do Lemonade CLI:

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
> Se o seu dispositivo tiver memória ou VRAM de GPU limitadas, escolha um modelo GGUF mais pequeno da biblioteca de modelos do Lemonade e utilize esse ID de modelo (e o respetivo tokenizador correspondente) ao longo deste playbook.

> **Nota:** O primeiro `lemonade run` transfere o modelo caso ainda não esteja presente, o que pode demorar algum tempo consoante o tamanho do modelo e a sua ligação.

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
Abra esse URL no seu browser.
A porta não tem nada de especial—se a 8000 já estiver em uso, indique qualquer porta livre com `--port` (ou `-p`).
O backend local predefinido deverá aparecer como saudável no ecrã inicial.

> **Nota:** O primeiro arranque cria o ambiente Python gerido por `uv` do Agent Server, pelo que pode demorar alguns minutos até o backend reportar estado saudável.

O comando `agent-canvas` inicia em conjunto o servidor de agentes, o backend de automação e a interface web.
Só precisa deste único comando para executar o OpenHands localmente.
O resto deste playbook configura tudo através da interface do Agent Canvas no seu browser.
<!-- @os:end -->

<!-- @os:windows -->
No Windows, execute a imagem de contentor publicada do Agent Canvas com o Docker Desktop.
A imagem inclui o Agent Server, o backend de automação e a interface web, pelo que não precisa de instalar o Node.js, o `uv` nem a CLI no anfitrião.

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

Abra `http://localhost:8000/canvas` no seu browser.
Se a porta 8000 já estiver em uso, mapeie uma porta diferente no anfitrião, por exemplo `-p 8080:8000`, e abra antes `http://localhost:8080/canvas`.

> **Nota:** O primeiro arranque cria o ambiente do Agent Server dentro do contentor, pelo que pode demorar alguns minutos até o backend reportar estado saudável.

A montagem `.openhands` mantém o seu perfil de LLM, servidores MCP e automações persistentes entre reinícios do contentor.
O resto deste playbook configura tudo através da interface do Agent Canvas no seu browser em `http://localhost:8000/canvas`.
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

No primeiro arranque, o Agent Canvas abre um fluxo de integração (onboarding).
Nesse fluxo:

1. Mantenha **OpenHands** selecionado como agente e clique em **Next**.
2. Em **Set up your LLM**, selecione **Advanced**.
3. Mantenha **Authentication** definido como **API key**.
4. Defina **Custom Model** como `openai/Qwen3.6-35B-A3B-GGUF`.
5. Defina **Base URL** como `http://127.0.0.1:13305/api/v1`.
6. Em **API Key**, introduza qualquer valor de exemplo não vazio, como `lemonade-local`. O Lemonade não requer uma chave real, mas o cliente OpenHands precisa de um valor para enviar.

<!-- @os:windows -->
> **Windows (Docker):** o Agent Server é executado dentro do contentor, pelo que deve definir **Base URL** como `http://host.docker.internal:13305/api/v1` em vez de `http://127.0.0.1:13305/api/v1`.
> A partir de dentro do contentor, `127.0.0.1` refere-se ao próprio contentor; `host.docker.internal` permite alcançar o Lemonade em execução no anfitrião Windows, e o Docker Desktop disponibiliza esse nome de anfitrião automaticamente.
<!-- @os:end -->

Os campos de ligação devem ter o seguinte aspeto.
O campo da chave de API é ocultado pela UI.

![Definições avançadas de LLM do Agent Canvas na primeira utilização, com o modelo Lemonade e o URL base local](assets/01-llm-advanced-settings.png)

Depois, selecione **All** e defina os campos adicionais do modelo local:

1. Percorra até **Custom Tokenizer** e defina-o como `Qwen/Qwen3.6-35B-A3B`.
2. Percorra até **LiteLLM Extra Body** e defina-o como `{"enable_thinking": true}`.
3. Clique em **Next**.

![Separador All de LLM do Agent Canvas na primeira utilização, com o tokenizador personalizado Qwen](assets/02-llm-all-tokenizer-settings.png)

![Separador All de LLM do Agent Canvas na primeira utilização, com o corpo extra LiteLLM configurado](assets/03-llm-all-extra-body-settings.png)

As definições de LLM devem mostrar:

| Campo | Valor |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

O prefixo `openai/` indica ao LiteLLM para usar a formatação de pedidos compatível com OpenAI ao comunicar com o endpoint do Lemonade.
O tokenizador personalizado é o tokenizador original do Hugging Face para o modelo GGUF; permite que o OpenHands conte os mesmos tokens de modelo de conversação (chat-template) que o servidor de modelo local vê.
O formulário atual de LLM da primeira utilização não mostra definições de condensador (condenser).
Se a sua compilação do Agent Canvas expuser mais tarde definições de condensador em **Settings > LLM**, use `llm_summarizing` e defina o número máximo de tokens abaixo da janela de contexto do Lemonade, por exemplo `56000`.

## 5. Instalar os Servidores MCP do GitHub e do Slack

Na UI do Agent Canvas, abra **Customize** (ou **Settings > MCP**) para adicionar os servidores MCP que fornecem ao agente ferramentas para GitHub e Slack.
Os valores de token são enviados apenas para o seu Agent Server local e são guardados como definições encriptadas.

<!-- @os:windows -->
> **Windows (Docker):** os comandos do servidor MCP `npx` abaixo são executados dentro do contentor, que já inclui o Node.js, pelo que nada de adicional é instalado no anfitrião.
> Como `.openhands` está montado, os servidores MCP e os respetivos tokens persistem entre reinícios do contentor.
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

Defina `SLACK_CHANNEL_IDS` como o ID do canal de resumo (o mesmo valor que `SLACK_DIGEST_CHANNEL`), para que o agente não precise de percorrer todos os canais do Slack.

Depois de adicionar ambos os servidores, use o botão **Test** em cada um deles para confirmar que estabelecem ligação e anunciam ferramentas.
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
2. Defina o **Name** como `GitHub Development Digest to Slack`.
3. Defina o **Prompt** com o seguinte texto, substituindo os marcadores de posição do repositório e do canal pelos seus valores:

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

4. Defina o **Trigger** como **Cron** com o horário `0 9 * * 1-5` (9h nos dias úteis) e defina o **Timezone** para o seu fuso horário, por exemplo `America/New_York`.
5. Defina o **Timeout** como `900` segundos.
6. Guarde a automação.

A página de detalhes da automação mostra a nova automação com o respetivo acionador cron e o ponto de entrada de prompt preset gerado.

![Página de detalhes da automação do Agent Canvas após a criação](assets/05-automation-created.png)
## 7. Testar a Automação

A partir da página de detalhe da automação na Agent Canvas UI:

1. Clique em **Run now** (ou **Dispatch**) para executar a automação uma vez, imediatamente.
2. Observe a lista de execuções na mesma página. A execução mais recente deverá transitar para `COMPLETED`.
3. Abra o canal do Slack de destino. Deverá conter o digest gerado.

Não precisa de esperar que o cron schedule seja acionado—**Run now** aciona uma execução a pedido, para que possa confirmar que o prompt, as ligações MCP e a publicação no Slack funcionam todos antes de depender do agendamento.

![Agent Canvas automation run completed successfully](assets/06-automation-run-completed.png)

![Slack channel showing the generated OpenHands digest](assets/07-slackbot-message.png)

## Resolução de Problemas

<!-- @os:windows -->
- **A porta 8000 do Docker já está em uso:** mapeie uma porta de anfitrião diferente, por exemplo `docker run ... -p 8080:8000 ...`, e abra `http://localhost:8080/canvas`.
- **`docker pull` falha com um erro de credenciais** (por exemplo, "A specified logon session does not exist"): execute o pull a partir de uma sessão interativa do Windows, ou faça o pull da imagem antecipadamente. A imagem é pública, pelo que não é necessário `docker login`.
- **A UI carrega mas o backend está com problemas:** o primeiro arranque cria o ambiente do Agent Server dentro do contentor. Aguarde um minuto e atualize a página, depois verifique `docker logs <container>` para acompanhar o progresso.
- **O Agent Canvas não consegue aceder ao Lemonade a partir do contentor:** defina o **Base URL** do LLM como `http://host.docker.internal:13305/api/v1` (e não `127.0.0.1`), e confirme que o Lemonade está em execução no anfitrião Windows.
<!-- @os:end -->

- **O Lemonade está inativo:** reinicie-o com o comando `lemonade run "${LEMONADE_MODEL}"` do passo 1, depois volte a executar a verificação de saúde.
- **`npm install -g` falha com um erro de permissões:** no Linux ou WSL, configure um diretório global do npm pertencente ao utilizador, adicione-o ao ficheiro de arranque da sua shell e depois instale novamente o Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Se utilizar `zsh`, adicione a mesma linha `export PATH=...` a `~/.zshrc` em vez de `~/.bashrc`.
- **O Agent Canvas rejeita as definições do LLM após definir `custom_tokenizer`:** instale o `transformers` no ambiente Python do Agent Server, reinicie o Agent Canvas se necessário, e tente novamente guardar as definições do LLM. O OpenHands requer o Transformers para carregar o modelo de chat do tokenizador quando `custom_tokenizer` está definido.
- **O Agent Canvas não consegue aceder ao Lemonade:** verifique `curl -fsS "${LEMONADE_BASE_URL}/health"` e confirme que o base URL introduzido no formulário de LLM da primeira utilização ou em **Settings > LLM** corresponde ao endpoint local em execução ou ao túnel HTTPS.
- **As definições do LLM não foram guardadas:** certifique-se de que clicou em **Next** depois de introduzir os valores. Reabra **Settings > LLM** para confirmar que os valores foram guardados.
- **O GitHub MCP não consegue ver repositórios privados:** confirme que o token do GitHub tem acesso de leitura ao repositório de destino e que o botão **Test** do MCP em **Customize** apresenta as ferramentas do GitHub.
- **O Slack consegue ler canais mas não consegue publicar:** convide a app do Slack para o canal de destino e confirme que o bot tem `chat:write`.
- **A automação lista demasiados canais do Slack:** utilize um ID de canal do Slack e defina `SLACK_CHANNEL_IDS` no servidor MCP do Slack em **Customize**.
- **A execução da automação falha ou excede o contexto:** confirme que o Lemonade foi iniciado com `ctx_size=65536`, confirme que o LLM do OpenHands tem `custom_tokenizer` definido, e utilize um repositório explícito com conjuntos de resultados do GitHub limitados a 3 a 5 itens. Se a sua versão do Agent Canvas expuser definições de condenser, defina o número máximo de tokens do condenser abaixo da janela de contexto do Lemonade.

## Próximos Passos

- Adicionar um digest semanal apenas de releases.
- Adicionar uma automação acionada por eventos do GitHub para alertas mais rápidos de PR ou push.
- Encaminhar o mesmo digest para o Notion, Linear, ou outra ferramenta suportada por MCP.

## Recursos

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Documentação do Lemonade Server](https://lemonade-server.ai/docs)
- [Repositório de extensões do OpenHands](https://github.com/OpenHands/extensions)
- [Servidores do Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Pacote MCP do Slack](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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