<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente a partir do inglês e não foi revista por um humano. Pode conter erros, e determinadas instruções, comandos, transferências, disponibilidade de produtos ou outro conteúdo podem variar consoante o idioma ou a região. Em caso de qualquer inconsistência ou discrepância, prevalece a versão original em inglês do playbook.
<!-- auto-translated-disclaimer:end -->

# Executar o OpenClaw com o Lemonade Server como backend

## Descrição geral

[**OpenClaw**](https://openclaw.ai/) é um agente de IA autónomo que consegue escrever e executar código, gerir ficheiros e realizar tarefas complexas de várias etapas em seu nome. Ao contrário de um assistente de conversação que apenas responde a perguntas, o OpenClaw executa ações reais no seu sistema, o que significa que precisa de um backend de IA rápido e capaz que consiga acompanhar um ciclo de agente exigente.

O [**Lemonade Server**](https://lemonade-server.ai/) é esse backend. É um servidor de inferência local de código aberto que executa modelos de GenAI diretamente no seu hardware e os disponibiliza através da API padrão da indústria, a API OpenAI.

Juntos, formam uma pilha de agente de IA totalmente local: o Lemonade trata da inferência do modelo e o OpenClaw fornece o ciclo do agente que transforma os resultados do modelo em ações reais.

> **Antes de continuar:** o OpenClaw é um agente de IA altamente autónomo. Dar a qualquer agente de IA acesso ao seu sistema pode resultar em resultados imprevisíveis ou não pretendidos. Prossiga apenas se compreender os riscos e se sentir confortável com software autónomo a atuar em seu nome.

---

## O que vai aprender

No final deste guia, será capaz de:

- Conhecer o **Lemonade Server**
- **Instalar o OpenClaw** e **configurá-lo para utilizar o Lemonade Server** como o seu backend de IA.
- **Iniciar o gateway do OpenClaw** e confirmar que o seu agente está pronto a trabalhar.
- **Ligar um canal de comunicação** (Discord ou Telegram) para poder conversar com o seu agente a partir de qualquer dispositivo.

---

<!-- @device:halo_box,halo,stx,krk -->
## Definir a configuração de memória

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Verificar atualizações de software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalar os pré-requisitos de software

<!-- @os:linux -->
- Um PC com **Ubuntu 24.04+** ou uma distribuição Linux compatível baseada em Debian com `apt-get`
- Pelo menos **12 GB de RAM** (64 GB+ recomendados para modelos maiores)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (Opcional, para colocar o OpenClaw em sandbox)
- **~10–30 GB de espaço livre em disco** para os pesos do modelo
<!-- @os:end -->

<!-- @os:windows -->
- Um PC com **Windows 10/11**
- Pelo menos **12 GB de RAM** (64 GB+ recomendados para modelos maiores)
- **~10–30 GB de espaço livre em disco** para os pesos do modelo
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (Opcional, para colocar o OpenClaw em sandbox)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Obter e carregar o modelo recomendado

O modelo recomendado para este guia é o **Qwen3.6-35B-A3B-GGUF** da Unsloth, um modelo MoE robusto com uma janela de contexto de 263k tokens que é adequado para cargas de trabalho de agentes. Este modelo utiliza a quantização UD-Q4_K_XL. Obtenha-o agora:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Em seguida, carregue-o com uma janela de contexto grande e guarde essa definição para execuções futuras:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

O modelo tem um comprimento de contexto predefinido de 262 144 tokens. Se encontrar erros de falta de memória (OOM), considere reduzir a janela de contexto. No entanto, uma vez que o Qwen3.6 utiliza contexto alargado para tarefas complexas, recomendamos manter um comprimento de contexto de pelo menos 128K tokens para preservar as capacidades de raciocínio.

> **Sugestão: Desative o modo de raciocínio para respostas do agente mais rápidas:** o Qwen3.6-35B-A3B é executado no modo de raciocínio (thinking) por predefinição, o que adiciona latência antes de cada resposta. Em ciclos de agente, este overhead acumula-se rapidamente. O repositório [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) disponibiliza uma configuração pronta a usar que desativa o modo de raciocínio. Para a utilizar, transfira o ficheiro e importe-o:
>
> ```bash
> curl -LO https://raw.githubusercontent.com/lemonade-sdk/recipes/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json
> lemonade import Qwen3.6-35B-A3B-NoThinking.json
> ```

---

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
$entry = $parsed.data | Where-Object { $_.id -eq "${openclaw_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${openclaw_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${openclaw_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${openclaw_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${openclaw_model} is not saved with ctx_size=262144. Run: lemonade load ${openclaw_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${openclaw_model} is saved with ctx_size=262144"

$body = @{
  model = "${openclaw_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openclaw-lemonade-chat-body.json"
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
model_id = "${openclaw_model}"

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

ctx_size = entry.get("recipe_options", {}).get("ctx_size")
if ctx_size != 262144:
    print(f"Model {model_id} is not saved with ctx_size=262144. Run: lemonade load {model_id} --ctx-size 262144 --save-options")
    sys.exit(1)
print(f"OK: {model_id} is saved with ctx_size=262144")
PY

body='{
  "model": "${openclaw_model}",
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

## Configurar o WSL

Executamos o OpenClaw dentro do WSL (Recomendado) e ligamo-lo ao Lemonade a ser executado nativamente no Windows. Isto proporciona-lhe um ambiente de shell Linux para o OpenClaw, mantendo a aceleração por GPU do Lemonade no lado do Windows.

### Instalar o WSL e o Ubuntu

Abra o PowerShell como Administrador e instale o kernel do WSL:

```powershell
wsl --install --no-distribution
```

Em seguida, instale o Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Ativar o systemd no WSL

Execute isto dentro do terminal do Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Saia do WSL e reinicie-o:

```powershell
exit
wsl --shutdown
wsl
```

### Fazer a ponte do Lemonade do Windows para o WSL

O WSL2 é executado numa rede virtual. O Lemonade no Windows liga-se a `127.0.0.1`, ao qual o WSL não consegue aceder diretamente. Um proxy de porta do Windows encaminha o tráfego do IP de gateway do WSL para o localhost do Windows.

**Encontre o seu IP de gateway do WSL** (execute dentro do WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Adicione o proxy de porta** (execute no PowerShell como Administrador, substituindo `<WSL-Gateway-IP>` pelo seu IP de gateway do WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Nota: Se encontrar um erro `netsh: command not found`, tente utilizar o nome explícito do executável `netsh.exe`

**Adicione uma regra de firewall** (na mesma janela do PowerShell elevada):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Verifique a partir do WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Se já tiver carregado o modelo Qwen3.6-35B-A3B-GGUF no passo anterior, deverá ver uma saída JSON como esta:

```json
{
  "data": [
    {
      "checkpoint": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL",
      "checkpoints": {
        "main": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL"
      },
      "mmproj": "unsloth/Qwen3.6-35B-A3B-GGUF:mmproj-F16.gguf",
      ....
    }
  ],
  "object": "list"
}
```

#### Manter a Ponte a Funcionar Após um Reinício

A regra `netsh portproxy` sobrevive a reinícios, mas o IP da gateway do WSL pode mudar após um `wsl --shutdown` ou reinício. Quando isso acontece, o proxy continua a apontar para o IP antigo e o Lemonade torna-se inacessível a partir do WSL. Se isso acontecer, utilize uma das opções abaixo.

**Opção 1 (recomendada) — Reparar a ponte automaticamente.** Para evitar fazer isto manualmente todas as vezes, utilize uma tarefa agendada que verifica a ponte a cada arranque e início de sessão e a reconstrói apenas quando o IP da gateway mudou. Consulte o [guia de auto-reparação da ponte WSL do Lemonade](assets/RepairLemonadeWslBridge.md).


**Opção 2 — Reparar a ponte manualmente.** Primeiro, obtenha o IP atual da gateway do WSL executando isto dentro do WSL:

```bash
ip route show default | awk '{print $3}' | head -1
```

Copie este valor; irá utilizá-lo no lugar de `<new-WSL-Gateway-IP>` abaixo.

Depois, num **PowerShell elevado** (Executar como administrador), liste as regras existentes, elimine apenas a regra desatualizada do Lemonade e adicione uma nova com o IP atual:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

Na saída de `show all`, a regra desatualizada do Lemonade é a entrada cujo endereço de ligação é `127.0.0.1` na porta `13305`; o seu endereço de escuta é o seu `<old-WSL-Gateway-IP>`. Eliminar por esse endereço remove apenas esta regra e deixa quaisquer outras regras de port-proxy na sua máquina intactas.

A regra de firewall que adicionou durante a configuração está associada à porta `13305` (não ao IP), pelo que continua a funcionar e não precisa de ser recriada.

> **Recomendação:** Para evitar problemas de gateway, sugerimos vivamente a seguinte configuração de shell:
> - Os **comandos do Windows** devem ser executados no **PowerShell**
> - Os **comandos da distro WSL** devem ser executados numa **Command Prompt** (executada como **Administrador**)

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

echo "WSL gateway IP: $WINDOWS_HOST"

models_json="$(curl -fsS --max-time 5 "http://$WINDOWS_HOST:13305/api/v1/models")"

if [ -z "$models_json" ]; then
  echo "Could not reach Lemonade from WSL at http://$WINDOWS_HOST:13305/api/v1/models"
  echo "Check the Windows netsh portproxy and firewall rule from the README."
  exit 1
fi

echo "$models_json" | python3 -m json.tool >/dev/null
echo "OK: WSL can reach native Windows Lemonade through the bridge"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "wsl-lemonade-bridge-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "WSL Lemonade bridge test failed"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 

---
<!-- @os:end -->

## Instalar e Configurar o OpenClaw

### Instalar o OpenClaw
<!-- @os:windows -->
> Execute os comandos desta secção dentro do seu **terminal WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

A flag `--no-onboard` ignora o assistente de configuração interativo; irá configurar o backend do modelo manualmente no passo seguinte, o que lhe dá um controlo preciso sobre o modelo e servidor utilizados.

Abra um novo terminal e confirme a instalação:

```bash
openclaw --version
```

> **Dica:** Se vir `command not found` após a instalação, adicione o diretório bin global do npm ao seu PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Para tornar isto permanente, adicione a linha acima ao seu ficheiro `~/.bashrc` ou `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=openclaw-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


### Configurar o OpenClaw para Utilizar o Lemonade

Execute a integração não interativa do OpenClaw.
<!-- @os:linux -->
```bash
openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->
<!-- @os:windows -->
```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->

Este comando escreve a configuração do OpenClaw em `~/.openclaw/openclaw.json`.

> **Dimensionamento da janela de contexto do OpenClaw:** A compactação do OpenClaw é ativada quando `contextTokens > contextWindow − reserveTokens`. O `reserveTokensFloor` predefinido é de 20 000 tokens, um limite mínimo que substitui o `reserveTokens` quando este é inferior, pelo que qualquer contexto de modelo abaixo de ~37k irá desencadear um ciclo de compactação infinito. Defina uma reserva baixa e desative o limite mínimo uma vez na sua configuração e isso aplica-se a todos os modelos, sem ser necessário ajustar por modelo:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` é um *limite mínimo* (garantia mínima), não a reserva em si; definir apenas o limite mínimo não tem efeito. `reserveTokensFloor: 0` desativa a garantia para que o `reserveTokens` mais baixo seja aceite.
>
> **Quando aplicar isto:** Utilize esta configuração se a janela de contexto efetiva do seu modelo for inferior a ~37k, seja porque o modelo é pequeno (por exemplo, 8k, 16k, 32k) ou porque o limitou intencionalmente a um valor mais baixo (por exemplo, carregando um modelo de 128k mas definindo o contexto para 16k no Lemonade). Sem isto, o OpenClaw entra num ciclo de compactação infinito ao iniciar.
>
> **Modelos de contexto amplo em contexto total:** Pode ignorar isto completamente. As predefinições funcionam bem, a compactação será ativada bem antes de a janela ficar cheia e o modelo tem espaço suficiente para gerar respostas longas. Se aplicar isto mesmo assim, tenha em atenção que `reserveTokens: 4096` limita o comprimento da resposta a ~4k tokens, o que pode cortar a geração de ficheiros longos ou planos detalhados.
>
> **Onde adicionar isto:** Coloque o bloco `compaction` dentro de `agents.defaults` no seu `openclaw.json` (normalmente em `~/.openclaw/openclaw.json`):
>
> ```json
> {
>   "agents": {
>     "defaults": {
>       "workspace": "/home/<you>/.openclaw/workspace",
>       "model": {
>         "primary": "lemonade/<your-model-id>"
>       },
>       "compaction": {
>         "reserveTokens": 4096,
>         "reserveTokensFloor": 0
>       }
>     }
>   }
> }
> ```
>
> O resto da sua configuração (gateway, channels, models, etc.) permanece inalterado, apenas a chave `compaction` precisa de ser adicionada.
### (Recomendado) Ativar o Docker Sandboxing

O OpenClaw pode encaminhar todas as operações de ficheiros e código do agente através de um contentor Docker isolado em vez de as executar diretamente no seu anfitrião. Isto limita o raio de ação de qualquer ação não intencional à sandbox, mantendo o sistema de ficheiros e a rede do anfitrião intactos.

Crie a imagem da sandbox uma única vez (o Docker tem de estar instalado):

```bash
docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE
```

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

# Docker Desktop injects its WSL cli-tools a few seconds after the distro boots.
for i in $(seq 1 30); do
  docker version >/dev/null 2>&1 && break
  sleep 2
done
docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Execute isto para adicionar a chave `sandbox` dentro do bloco `agents.defaults` existente em `~/.openclaw/openclaw.json`:

```bash
cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5
openclaw config patch --file ./sandbox.patch.json5
```

Por predefinição, os contentores de sandbox **não têm acesso à rede**. Consulte a [referência de sandboxing](https://docs.openclaw.ai/gateway/sandboxing) para bind mounts e substituições de rede.

> #### Resolução de problemas: Permissão do Docker negada
> 
> Se receber "permission denied" ao executar comandos do Docker:
> 
> **Passo 1: Adicione o seu utilizador ao grupo docker**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **Passo 2: Se o erro persistir, aplique a correção permanente**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> De seguida, **reinicie** o seu sistema.
> 
> **Correção temporária rápida** (é reposta após reiniciar):
> ```bash
> sudo chmod 666 /var/run/docker.sock
> ```

<!-- @os:linux -->
<!-- @test:id=openclaw-onboard-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "127.0.0.1:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written"
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-onboard-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "$WINDOWS_HOST:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-onboard-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw onboarding failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"
$tmp = Join-Path $env:TEMP "openclaw-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox config patch failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
## (Recomendado) Integração do OpenClaw com os Serviços Firecrawl

O [Firecrawl](https://docs.firecrawl.dev/introduction) fornece um serviço de crawling web e extração de conteúdo auto-hospedado que consegue contornar estes desafios e libertar todo o potencial da automação do OpenClaw.

Nesta configuração, o OpenClaw é executado como um conjunto de contentores Docker geridos com o Podman. Para simplificar a gestão do ciclo de vida e o arranque automático, registamos o Firecrawl como um serviço `systemd` ao nível do utilizador que orquestra a stack subjacente do Podman Compose. Isto permite que o OpenClaw inicie o gateway, o pare e verifique o serviço Firecrawl utilizando comandos `systemctl --user` padrão, em vez de interagir diretamente com os contentores.

Para manter as coisas simples, dividimos todo o processo em quatro passos:

---

### 1. Registar o serviço de sistema
Navegue até ao diretório de configuração do systemd ao nível do utilizador:
```bash
cd ~/.config/systemd/user
```
Crie e abra um novo ficheiro chamado `firecrawl.service`.
```bash
nano firecrawl.service
```
Copie e cole a seguinte configuração:
```bash
[Unit]
Description=OpenClaw Firecrawl Service
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=%h/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman compose -f openclaw-compose.yaml config --quiet

# Generate token and write to .env file
ExecStartPre=/bin/bash -c 'chmod 644 %h/firecrawl/.env && echo "OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)" > %h/firecrawl/.env'

# Step 1: Start containers in detached mode
ExecStart=/usr/bin/podman compose -f openclaw-compose.yaml up -d --remove-orphans

# Step 2: Wait for container to be healthy/ready
ExecStartPost=/bin/sleep 5

# Step 3: Run onboarding inside container in detached mode
ExecStartPost=/usr/bin/podman exec -d openclaw_gateway /bin/bash -c "openclaw onboard \
    --non-interactive \
    --accept-risk \
    --mode local \
    --auth-choice skip \
    --gateway-auth token \
    --gateway-token "$OPENCLAW_GATEWAY_TOKEN" "

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f openclaw-compose.yaml down

[Install]
WantedBy=default.target
```
Neste momento, o serviço foi definido mas ainda não registado no `systemd`.
Certifique-se de que o nome do ficheiro corresponde exatamente ao que criou acima e, de seguida, execute:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Se for bem-sucedido, deverá ver a seguinte saída:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` contém ligações simbólicas para serviços que estão configurados para iniciar automaticamente.

### 2. Configurar o Firecrawl

O [SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) é ideal para quem precisa de controlo total sobre os seus ambientes de scraping e processamento de dados, mas tem como contrapartida um esforço adicional de manutenção e configuração.

Comece por clonar o repositório:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Crie um ficheiro `.env`, no diretório `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Implementar o OpenClaw com o Podman Compose

Antes de continuar, certifique-se de que já obteve a imagem Docker mais recente do OpenClaw:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Depois de concluído, transfira o ficheiro Compose do OpenClaw [openclaw-compose.yaml](assets/openclaw-compose.yaml) e coloque-o no diretório raiz `/firecrawl`:

> Esta convenção é necessária para que o `systemd` localize e inicie o serviço corretamente, conforme especificado em `WorkingDirectory=${HOME}/firecrawl`.

> Pode sempre expandir a stack adicionando serviços Firecrawl adicionais conforme necessário. A lista completa dos serviços disponíveis pode ser encontrada no [docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) oficial do Firecrawl.

### 4. Iniciar o serviço OpenClaw através do Firecrawl

Antes de entregar o controlo ao `systemd`, valide que tudo funciona corretamente executando a stack manualmente:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Se tudo estiver configurado corretamente, deverá ver o contentor OpenClaw a subir e a saída da sua linha de comandos deverá ter um aspeto semelhante a este:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Uma vez verificado, encerre a stack novamente antes de prosseguir:
```bash
podman compose -f openclaw-compose.yaml down
```
Antes de iniciar o serviço, deve garantir que a propriedade e as permissões corretas estão definidas no diretório `firecrawl` e no seu ficheiro `.env`.
Isto é essencial para que o serviço consiga escrever as suas credenciais no arranque.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Agora que tudo está validado, inicie o serviço através do `systemd`:
```bash
systemctl --user start firecrawl.service
```
As [Ações do OpenClaw](https://docs.openclaw.ai/) são acessíveis a partir do interior do contentor interativo, e o Painel Web está disponível no mesmo anfitrião e porta em http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Obter o seu `OPENCLAW_GATEWAY_TOKEN`

Assim que o serviço estiver em funcionamento, irá reparar num novo diretório `.openclaw` criado na sua pasta pessoal (~/.openclaw). Este diretório está bloqueado por predefinição, pelo que terá de o desbloquear para obter o seu token de gateway.

1. Conceda acesso ao diretório:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Leia o seu token de gateway:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Localize o valor de `OPENCLAW_GATEWAY_TOKEN` na saída.

3. Abra o painel do gateway no seu navegador em http://127.0.0.1:18789. Cole o seu token quando lhe for pedido para autenticar.

Para parar o serviço, execute:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Iniciar a Gateway OpenClaw

A gateway é o processo do OpenClaw que gere o ciclo do agente e disponibiliza o dashboard:

```bash
openclaw gateway run --bind loopback --port 18789
```

<!-- @os:linux -->
<!-- @test:id=openclaw-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

Para abrir o dashboard, execute isto num segundo terminal enquanto a gateway ainda estiver em execução:

```bash
openclaw dashboard
```

Uma vez que a gateway se liga ao loopback, o dashboard autentica-se automaticamente quando aberto a partir da mesma máquina, não sendo necessária a introdução de um token nem a aprovação de dispositivo para acesso local. Deverá ver o dashboard do OpenClaw com o seu modelo Lemonade listado como o backend ativo.

> Se tiver ativado o sandboxing, pode verificá-lo pedindo ao agente para `run hostname` a partir do dashboard. Se vir um ID de contentor curto em vez do nome de máquina real, o sandbox está a funcionar.

**Parabéns, construiu uma stack de agente de IA totalmente local, do zero.**

> **Precisa do token da gateway?** Execute `openclaw dashboard --no-open` para imprimir o URL do dashboard com o token incorporado (também tenta copiá-lo para a área de transferência). Em alternativa, o token encontra-se em `gateway.auth.token` no ficheiro `~/.openclaw/openclaw.json`.

**Aceder ao Dashboard a partir de Outro Dispositivo (via Túnel SSH)**

Se o OpenClaw estiver a ser executado numa máquina remota, pode aceder ao seu dashboard a partir da sua máquina local através de um túnel SSH. O túnel encaminha a porta da gateway (`18789`) para que o seu navegador local possa comunicar com a gateway remota através de `127.0.0.1`.

1. A partir da sua **máquina local**, ligue-se à máquina remota uma vez e aceite o pedido de fingerprint para que o anfitrião seja adicionado aos seus known hosts:

   ```bash
   ssh user@<host-ip>
   ```

2. Ainda na sua **máquina local**, abra o túnel SSH:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Nota:** Depois de introduzir a sua palavra-passe, o terminal não mostra qualquer output e parece estar bloqueado. Isto é esperado: a flag `-N` indica ao SSH para não executar nenhum comando remoto, pelo que este simplesmente mantém o túnel aberto. Deixe este terminal em execução.

3. Na sua **máquina local**, abra um navegador e aceda a `http://127.0.0.1:18789`.

4. Na **máquina remota**, imprima o token da gateway e cole-o no navegador para iniciar sessão:

   ```bash
   openclaw dashboard --no-open
   ```

   Isto imprime o URL do dashboard com o token incorporado; copie o token para iniciar sessão. (O token também está guardado em `gateway.auth.token` no ficheiro `~/.openclaw/openclaw.json`.)

> **Aprovar um dispositivo remoto:** Quando abre o dashboard a partir de outra máquina ou telemóvel, o navegador poderá mostrar um ID de pedido. Na **máquina remota**, liste os pedidos pendentes:
> ```bash
> openclaw devices list
> ```
> Depois aprove o pedido correspondente:
> ```bash
> openclaw devices approve <requestId>
> ```
> Isto só é necessário para dispositivos remotos ou secundários; o acesso via loopback a partir da mesma máquina autentica-se automaticamente. Consulte a documentação de [Acesso Remoto](https://docs.openclaw.ai/gateway/remote) para mais detalhes.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Opcional: Ligar um Canal de Comunicação

Assim que a gateway estiver em execução, pode aceder ao seu agente local a partir de qualquer dispositivo. Escolha a opção que se adequa à sua configuração. O OpenClaw suporta [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram), e outros canais; consulte a lista completa em [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Opção A: Discord

O Discord requer um servidor onde **tenha acesso de administrador** para adicionar um bot. Se partilha servidores mas não é dono de nenhum, utilize a Opção B (Telegram).

#### Criar uma conta e servidor Discord

Se não tiver uma conta Discord, registe-se em [discord.com](https://discord.com). Também precisa de um servidor onde seja administrador; crie um clicando no ícone **+** na barra lateral do Discord e selecionando **Create My Own**. Um servidor privado é suficiente.

#### Criar uma aplicação e bot no Discord

1. Aceda ao [Discord Developer Portal](https://discord.com/developers/applications) e clique em **New Application**. Dê-lhe um nome (por exemplo, "openclaw-bot").
2. Na barra lateral, clique em **Bot**. Defina um nome de utilizador para o bot.
3. Ainda na página Bot, desça até **Privileged Gateway Intents** e ative:
   - **Message Content Intent** (obrigatório)
   - **Server Members Intent** (recomendado)
4. Volte acima e clique em **Reset Token** para gerar o token do seu bot. Copie-o.

#### Adicionar o bot ao seu servidor

1. Na barra lateral, clique em **OAuth2/ URL Generator**.
2. Em **Scopes**, ative `bot` e `applications.commands`.
3. Em **Bot Permissions**, ative: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Copie o URL gerado, cole-o no seu navegador, selecione o seu servidor e confirme. O bot deverá agora aparecer na lista de membros do seu servidor.

#### Recolher os seus IDs

Ative o Modo de Desenvolvedor no Discord (**User Settings/ Advanced/ Developer Mode**) e, em seguida:
- Clique com o botão direito no ícone do seu servidor: **Copy Server ID**
- Clique com o botão direito no seu próprio avatar: **Copy User ID**

#### Permitir DMs de membros do servidor

Clique com o botão direito no ícone do seu servidor/ **Privacy Settings**/ ative a opção **Direct Messages**. Isto permite que o bot lhe envie mensagens diretas, o que é necessário para o passo de emparelhamento.

#### Configurar o OpenClaw para o Discord

Guarde o token do seu bot como uma variável de ambiente e, em seguida, crie um único ficheiro de patch que ative o Discord, faça referência ao token e coloque o seu servidor na allowlist. Substitua `<server_id>` e `<user_id>` pelos IDs recolhidos acima.

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"

cat > discord.patch.json5 <<JSON5
{
  channels: {
    discord: {
      enabled: true,
      token: { source: "env", provider: "default", id: "DISCORD_BOT_TOKEN" },
      dmPolicy: "pairing",
      groupPolicy: "allowlist",
      guilds: {
        "<server_id>": {
          requireMention: false,
          users: ["<user_id>"],
        },
      },
    },
  },
}
JSON5
openclaw config patch --file ./discord.patch.json5
```

> **Não confie em pedir ao agente para configurar isto.** Quando o sandboxing está ativado, o agente não consegue escrever em `~/.openclaw/openclaw.json` a partir de dentro do sandbox; utilize antes os comandos CLI acima no anfitrião.

Reinicie a gateway para que esta reconheça a nova configuração do canal:

```bash
openclaw gateway run --bind loopback --port 18789
```

Deverá ver `logged in to discord as <bot-name>` no output da gateway em poucos segundos.
#### Emparelhar a sua conta do Discord

Envie uma DM ao bot no Discord. Ele responderá com um código de emparelhamento curto.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Aprove-o na máquina que está a executar o OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Os códigos de emparelhamento expiram ao fim de uma hora.

Já pode conversar com o seu agente diretamente a partir do Discord e transferir tarefas para o seu hardware local.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Opção B: Telegram

O Telegram é mais simples do que o Discord para a maioria dos utilizadores, não requer servidor nem acesso de administrador.

#### Criar um bot do Telegram

1. Abra o Telegram e envie uma mensagem a **@BotFather**.
2. Envie `/newbot` e siga as instruções. Guarde o token do bot que lhe é fornecido.

#### Configurar o OpenClaw para o Telegram

Guarde o token como uma variável de ambiente:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Adicione a configuração do canal a `~/.openclaw/openclaw.json` (ou aplique-a através do painel):

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "YOUR_BOT_TOKEN",
      "dmPolicy": "pairing"
    }
  }
}
```

Reinicie o gateway e, em seguida, envie ao seu bot uma mensagem no Telegram. Aprove o emparelhamento:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Os códigos de emparelhamento expiram ao fim de uma hora. Já pode conversar com o seu agente através de DM no Telegram.

---

## Próximos passos

Agora que o seu agente pode receber comandos a partir do seu telemóvel e agir na sua máquina local, seguem-se três direções que vale a pena explorar:

1. **Resumidor do mercado de ações**: Agende o OpenClaw para obter dados de APIs financeiras a um intervalo fixo, resumir os movimentos do dia com o seu modelo local e enviar um resumo para o seu telemóvel todas as manhãs através do canal escolhido.

2. **Monitor de ajuste fino (fine-tuning)**: Inicie remotamente uma tarefa de treino via Telegram ou Discord e, em seguida, faça com que o agente acompanhe o registo de treino e reporte periodicamente valores de perda, utilização da GPU e uso de disco para o seu telemóvel. Se a execução parar ou o VRAM disparar, fica a saber imediatamente sem precisar de estar junto à máquina.

3. **IOT com um VLM local**: Aponte uma câmara para a sua porta de entrada, execute um modelo de visão no Lemonade e faça com que o OpenClaw analise fotogramas a pedido ou perante um gatilho. Pergunte "chegaram encomendas hoje?" a partir do seu telemóvel e obtenha uma resposta direta a partir do seu próprio hardware.

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