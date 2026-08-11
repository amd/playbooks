<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente do inglês e não foi revisada por um ser humano. Ela pode conter erros, e determinadas instruções, comandos, downloads, disponibilidade de produtos ou outros conteúdos podem variar de acordo com o idioma ou a região. Em caso de qualquer inconsistência ou divergência, a versão original em inglês do playbook prevalecerá.
<!-- auto-translated-disclaimer:end -->

# Executando o OpenClaw com o Lemonade Server como backend

## Visão geral

[**OpenClaw**](https://openclaw.ai/) é um agente de IA autônomo capaz de escrever e executar código, gerenciar arquivos e realizar tarefas complexas de múltiplas etapas em seu nome. Diferente de um assistente de chat que apenas responde perguntas, o OpenClaw executa ações reais em seu sistema, o que significa que ele precisa de um backend de IA rápido e capaz, que consiga acompanhar o ritmo de um loop de agente exigente.

O [**Lemonade Server**](https://lemonade-server.ai/) é esse backend. Trata-se de um servidor de inferência local de código aberto que executa modelos de GenAI diretamente em seu hardware e os expõe por meio da API padrão da indústria, a OpenAI API.

Juntos, eles formam uma pilha de agente de IA totalmente local: o Lemonade cuida da inferência do modelo, e o OpenClaw fornece o loop de agente que transforma as saídas do modelo em ações reais.

> **Antes de continuar:** o OpenClaw é um agente de IA altamente autônomo. Conceder a qualquer agente de IA acesso ao seu sistema pode resultar em resultados imprevisíveis ou não intencionais. Prossiga somente se você entender os riscos e estiver confortável com um software autônomo agindo em seu nome.

---

## O que você vai aprender

Ao final deste playbook, você será capaz de:

- Conhecer o **Lemonade Server**
- **Instalar o OpenClaw** e **apontá-lo para o Lemonade Server** como seu backend de IA.
- **Iniciar o gateway do OpenClaw** e confirmar que seu agente está pronto para trabalhar.
- **Conectar um canal de comunicação** (Discord ou Telegram) para que você possa conversar com seu agente a partir de qualquer dispositivo.

---

## Definindo a Configuração de Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalando os Pré-requisitos de Software

<!-- @os:linux -->
- Um PC executando **Ubuntu 24.04+** ou uma distribuição Linux baseada em Debian compatível com `apt-get`
- Pelo menos **12 GB de RAM** (recomenda-se 64 GB+ para modelos maiores)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (Opcional, para fazer sandboxing do OpenClaw)
- **~10–30 GB de espaço livre em disco** para os pesos do modelo
<!-- @os:end -->

<!-- @os:windows -->
- Um PC executando **Windows 10/11**
- Pelo menos **12 GB de RAM** (recomenda-se 64 GB+ para modelos maiores)
- **~10–30 GB de espaço livre em disco** para os pesos do modelo
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (Opcional, para fazer sandboxing do OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Baixar e Carregar o Modelo Recomendado

O modelo recomendado para este playbook é o **Qwen3.6-35B-A3B-GGUF** da Unsloth, um forte modelo MoE com uma janela de contexto de 263 mil tokens, muito adequado para cargas de trabalho de agentes. Este modelo usa quantização UD-Q4_K_XL. Baixe-o agora:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Em seguida, carregue-o com uma janela de contexto grande e salve essa configuração para execuções futuras:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

O modelo tem um comprimento de contexto padrão de 262.144 tokens. Se você encontrar erros de falta de memória (OOM), considere reduzir a janela de contexto. No entanto, como o Qwen3.6 aproveita o contexto estendido para tarefas complexas, recomendamos manter um comprimento de contexto de pelo menos 128 mil tokens para preservar as capacidades de raciocínio.

> **Dica: desative o modo de raciocínio para respostas mais rápidas do agente:** o Qwen3.6-35B-A3B executa no modo de raciocínio (thinking mode) por padrão, o que adiciona latência antes de cada resposta. Em loops de agente, essa sobrecarga se acumula rapidamente. O repositório [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) fornece uma configuração pronta que desativa o raciocínio. Para usá-la, baixe o arquivo e importe-o:
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

Executamos o OpenClaw dentro do WSL (Recomendado) e o conectamos ao Lemonade em execução nativamente no Windows. Isso fornece um ambiente de shell Linux para o OpenClaw, mantendo a aceleração de GPU do Lemonade no lado do Windows.

### Instalar o WSL e o Ubuntu

Abra o PowerShell como Administrador e instale o kernel do WSL:

```powershell
wsl --install --no-distribution
```

Em seguida, instale o Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Habilitar o systemd no WSL

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

### Conectar (bridge) o Lemonade do Windows para dentro do WSL

O WSL2 é executado em uma rede virtual. O Lemonade no Windows se vincula a `127.0.0.1`, que o WSL não consegue alcançar diretamente. Um proxy de porta do Windows encaminha o tráfego do IP de gateway do WSL para o localhost do Windows.

**Encontre o IP de gateway do WSL** (execute dentro do WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Adicione o proxy de porta** (execute no PowerShell como Administrador, substituindo `<WSL-Gateway-IP>` pelo IP de gateway do seu WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Observação: se você encontrar um erro `netsh: command not found`, tente usar o nome explícito do executável `netsh.exe`

**Adicione uma regra de firewall** (mesmo PowerShell elevado):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Verifique a partir do WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Se você já carregou o modelo Qwen3.6-35B-A3B-GGUF na etapa anterior, deverá ver uma saída JSON como esta:

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

#### Mantendo a Ponte Funcionando Após uma Reinicialização

A regra `netsh portproxy` sobrevive a reinicializações, mas o IP do gateway do WSL pode mudar após um `wsl --shutdown` ou uma reinicialização. Quando isso acontece, o proxy ainda aponta para o IP antigo e o Lemonade se torna inacessível a partir do WSL. Se isso acontecer, use uma das opções abaixo.

**Opção 1 (recomendada) — Reparar a ponte automaticamente.** Para evitar fazer isso manualmente toda vez, use uma tarefa agendada que verifica a ponte a cada inicialização e login e a reconstrói apenas quando o IP do gateway mudou. Consulte o [guia de reparo automático da ponte WSL do Lemonade](assets/RepairLemonadeWslBridge.md).


**Opção 2 — Reparar a ponte manualmente.** Primeiro, obtenha o IP atual do gateway do WSL executando isto dentro do WSL:

```bash
ip route show default | awk '{print $3}' | head -1
```

Copie esse valor; você o usará no lugar de `<new-WSL-Gateway-IP>` abaixo.

Depois, em um **PowerShell elevado** (Executar como administrador), liste as regras existentes, exclua apenas a regra obsoleta do Lemonade e adicione uma nova com o IP atual:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

Na saída de `show all`, a regra obsoleta do Lemonade é a entrada cujo endereço de conexão é `127.0.0.1` na porta `13305`; seu endereço de escuta é o seu `<old-WSL-Gateway-IP>`. Excluir por esse endereço remove apenas essa regra e deixa quaisquer outras regras de port-proxy em sua máquina intocadas.

A regra de firewall que você adicionou durante a configuração está vinculada à porta `13305` (não ao IP), então ela continua funcionando e não precisa ser recriada.

> **Recomendação:** Para evitar problemas de gateway, sugerimos fortemente a seguinte configuração de shell:
> - **Comandos do Windows** devem ser executados no **PowerShell**
> - **Comandos da distro WSL** devem ser executados em um **Prompt de Comando** (executado como **Administrador**)

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
> Execute os comandos desta seção dentro do seu **terminal WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

A flag `--no-onboard` pula o assistente de configuração interativo, você configurará o backend do modelo manualmente na próxima etapa, o que oferece controle preciso sobre qual modelo e servidor são usados.

Abra um novo terminal e confirme a instalação:

```bash
openclaw --version
```

> **Dica:** Se você ver `command not found` após a instalação, adicione o diretório bin global do npm ao seu PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Para tornar isso permanente, adicione a linha acima ao seu arquivo `~/.bashrc` ou `~/.zshrc`.

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


### Configurar o OpenClaw para Usar o Lemonade

Execute o onboarding não interativo do OpenClaw.
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

Este comando grava a configuração do OpenClaw em `~/.openclaw/openclaw.json`.

> **Dimensionamento da janela de contexto do OpenClaw:** A compactação do OpenClaw é acionada quando `contextTokens > contextWindow − reserveTokens`. O padrão de `reserveTokensFloor` é 20.000 tokens, um piso que substitui `reserveTokens` quando este é menor, então qualquer contexto de modelo abaixo de ~37k acionará um loop infinito de compactação. Defina uma reserva baixa e desative o piso uma vez na sua configuração e isso se aplica a todos os modelos, sem necessidade de ajuste por modelo:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` é um *piso* (proteção mínima), não a reserva em si, definir apenas o piso não tem efeito. `reserveTokensFloor: 0` desativa a proteção para que o `reserveTokens` menor seja aceito.
>
> **Quando aplicar isso:** Use esta configuração se a janela de contexto efetiva do seu modelo for menor que ~37k, seja porque o modelo é pequeno (por exemplo, 8k, 16k, 32k) ou porque você limitou intencionalmente a um valor menor (por exemplo, carregando um modelo de 128k mas definindo o contexto para 16k no Lemonade). Sem isso, o OpenClaw entra em um loop infinito de compactação ao iniciar.
>
> **Modelos com contexto grande em contexto total:** Você pode pular isso completamente. Os padrões funcionam bem, a compactação será acionada bem antes de a janela se encher e o modelo tem espaço amplo para gerar respostas longas. Se você aplicar isso, esteja ciente de que `reserveTokens: 4096` limita o comprimento da resposta a ~4k tokens, o que pode cortar a geração de arquivos longos ou planos detalhados.
>
> **Onde adicionar isso:** Coloque o bloco `compaction` dentro de `agents.defaults` no seu `openclaw.json` (geralmente em `~/.openclaw/openclaw.json`):
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
> O resto da sua configuração (gateway, channels, models, etc.) permanece inalterado, apenas a chave `compaction` precisa ser adicionada.
### (Recomendado) Habilitar o Sandboxing do Docker

O OpenClaw pode rotear todas as operações de arquivo e código do agente por meio de um contêiner Docker isolado, em vez de executá-las diretamente no seu host. Isso limita o raio de impacto de qualquer ação não intencional ao sandbox, mantendo o sistema de arquivos e a rede do seu host intocados.

Construa a imagem do sandbox uma vez (o Docker deve estar instalado):

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

Os contêineres de sandbox **não têm acesso à rede** por padrão. Consulte a [referência de sandboxing](https://docs.openclaw.ai/gateway/sandboxing) para montagens de bind e substituições de rede.

> #### Solução de problemas: Permissão negada no Docker
> 
> Se você receber "permission denied" ao executar comandos do Docker:
> 
> **Etapa 1: Adicione seu usuário ao grupo docker**
> 
> ```bash
> sudo groupadd docker                    # Crie o grupo se necessário
> sudo usermod -aG docker $USER           # Adicione você mesmo ao grupo
> newgrp docker                           # Ative a alteração
> docker run hello-world                  # Teste
> ```
> 
> **Etapa 2: Se o erro persistir, aplique a correção permanente**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Em seguida, **reinicie** seu sistema.
> 
> **Correção temporária rápida** (é redefinida após a reinicialização):
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

O [Firecrawl](https://docs.firecrawl.dev/introduction) fornece um serviço de rastreamento e extração de conteúdo da web auto-hospedado que pode contornar esses desafios e desbloquear todo o potencial da automação do OpenClaw. 

Nesta configuração, o OpenClaw é executado como um conjunto de contêineres Docker gerenciados com Podman. Para simplificar o gerenciamento do ciclo de vida e a inicialização automática, registramos o Firecrawl como um serviço `systemd` no nível do usuário que orquestra a stack Podman Compose subjacente. Isso permite que o OpenClaw inicie o gateway, pare e verifique o serviço Firecrawl usando comandos `systemctl --user` padrão, em vez de interagir diretamente com os contêineres. 

Para manter as coisas simples, dividimos todo o processo em quatro etapas:

---

### 1. Registrar o serviço do sistema
Navegue até o diretório de configuração de usuário do systemd:
```bash
cd ~/.config/systemd/user
```
Crie e abra um novo arquivo chamado `firecrawl.service`.
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
Neste ponto, o serviço foi definido, mas ainda não registrado no `systemd`. 
Certifique-se de que o nome do arquivo corresponda exatamente ao que você criou acima e, em seguida, execute:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Se for bem-sucedido, você deverá ver a seguinte saída:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` contém links simbólicos para serviços configurados para iniciar automaticamente.

### 2. Configurar o Firecrawl

O [SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) é ideal para quem precisa de controle total sobre seus ambientes de scraping e processamento de dados, mas vem com o custo de esforços adicionais de manutenção e configuração.

Comece clonando o repositório:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Crie o `.env` no diretório raiz `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Implantar o OpenClaw com o Podman Compose

Antes de prosseguir, certifique-se de ter feito o pull da imagem Docker mais recente do OpenClaw:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Depois de fazer isso, baixe o arquivo Compose do OpenClaw [openclaw-compose.yaml](assets/openclaw-compose.yaml) e coloque-o no diretório raiz `/firecrawl`:

> Essa convenção é necessária para que o `systemd` localize e inicie o serviço corretamente, conforme especificado em `WorkingDirectory=${HOME}/firecrawl`.

> Você sempre pode expandir a stack adicionando serviços Firecrawl adicionais conforme necessário. A lista completa de serviços disponíveis pode ser encontrada no [docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) oficial do Firecrawl.

### 4. Iniciar o serviço OpenClaw através do Firecrawl 

Antes de entregar o controle ao `systemd`, valide se tudo funciona corretamente executando a stack manualmente:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Se tudo estiver configurado corretamente, você deverá ver o contêiner do OpenClaw subir, e a saída da sua linha de comando deverá ser semelhante a esta:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Após a verificação, derrube a stack novamente antes de prosseguir:
```bash
podman compose -f openclaw-compose.yaml down
```
Antes de iniciar o serviço, você deve garantir que a propriedade e as permissões corretas estejam definidas no diretório `firecrawl` e em seu arquivo `.env`. 
Isso é essencial para que o serviço grave suas credenciais na inicialização.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Agora que tudo foi validado, inicie o serviço por meio do `systemd`:
```bash
systemctl --user start firecrawl.service
```
[As Ações do OpenClaw](https://docs.openclaw.ai/) são acessíveis de dentro do contêiner interativo, e o Painel Web está disponível no mesmo host e porta em http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Obtendo seu `OPENCLAW_GATEWAY_TOKEN`

Assim que o serviço estiver em execução, você notará um novo diretório `.openclaw` criado na sua pasta home (~/.openclaw). Esse diretório é bloqueado por padrão, então você precisará desbloqueá-lo para recuperar seu token de gateway.

1. Conceda acesso ao diretório:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Leia seu token de gateway:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Localize o valor de `OPENCLAW_GATEWAY_TOKEN` na saída.

3. Abra o painel do gateway em seu navegador http://127.0.0.1:18789. Cole seu token quando solicitado para autenticar.

Para parar o serviço, execute:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Iniciar o OpenClaw Gateway

O gateway é o processo do OpenClaw que gerencia o loop do agente e disponibiliza o painel:

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

Para abrir o painel, execute isto em um segundo terminal enquanto o gateway ainda estiver em execução:

```bash
openclaw dashboard
```

Como o gateway se vincula ao loopback, o painel se autentica automaticamente quando aberto na mesma máquina, sem necessidade de inserir token ou aprovar dispositivo para acesso local. Você deve ver o painel do OpenClaw com o seu modelo Lemonade listado como o backend ativo.

> Se você ativou o sandboxing, pode verificar isso pedindo ao agente para `run hostname` a partir do painel. Se você vir um ID curto de container em vez do hostname da sua máquina, o sandbox está funcionando.

**Parabéns, você construiu uma stack de agente de IA totalmente local do zero.**

> **Precisa do token do gateway?** Execute `openclaw dashboard --no-open` para exibir a URL do painel com o token incorporado (ele também tenta copiá-lo para a sua área de transferência). Alternativamente, o token está em `gateway.auth.token` no arquivo `~/.openclaw/openclaw.json`.

**Acessando o Painel de Outro Dispositivo (via Túnel SSH)**

Se o OpenClaw estiver sendo executado em uma máquina remota, você pode acessar o painel a partir da sua máquina local através de um túnel SSH. O túnel encaminha a porta do gateway (`18789`) para que o seu navegador local possa se comunicar com o gateway remoto através de `127.0.0.1`.

1. Na sua **máquina local**, conecte-se à máquina remota uma vez e aceite o prompt de fingerprint para que o host seja adicionado aos seus known hosts:

   ```bash
   ssh user@<host-ip>
   ```

2. Ainda na sua **máquina local**, abra o túnel SSH:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Observação:** Depois que você inserir sua senha, o terminal não mostra nenhuma saída e parece travado. Isso é esperado: a flag `-N` diz ao SSH para não executar nenhum comando remoto, então ele simplesmente mantém o túnel aberto. Deixe este terminal em execução.

3. Na sua **máquina local**, abra um navegador e acesse `http://127.0.0.1:18789`.

4. Na **máquina remota**, exiba o token do gateway e cole-o no navegador para fazer login:

   ```bash
   openclaw dashboard --no-open
   ```

   Isso exibe a URL do painel com o token incorporado; copie o token para fazer login. (O token também é armazenado em `gateway.auth.token` no arquivo `~/.openclaw/openclaw.json`.)

> **Aprovando um dispositivo remoto:** Quando você abre o painel a partir de outra máquina ou telefone, o navegador pode exibir um ID de solicitação. Na **máquina remota**, liste as solicitações pendentes:
> ```bash
> openclaw devices list
> ```
> Em seguida, aprove a solicitação correspondente:
> ```bash
> openclaw devices approve <requestId>
> ```
> Isso só é necessário para dispositivos remotos ou secundários; o acesso via loopback na mesma máquina se autentica automaticamente. Consulte a documentação de [Acesso Remoto](https://docs.openclaw.ai/gateway/remote) para mais detalhes.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Opcional: Conectar um Canal de Comunicação

Depois que o gateway estiver em execução, você pode acessar seu agente local a partir de qualquer dispositivo. Escolha a opção que se adequa à sua configuração. O OpenClaw oferece suporte a [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) e outros canais, veja a lista completa em [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Opção A: Discord

O Discord requer um servidor onde **você tenha acesso de administrador** para adicionar um bot. Se você participa de servidores mas não é dono de nenhum, use a Opção B (Telegram) em vez disso.

#### Criar uma conta e um servidor no Discord

Se você não tem uma conta no Discord, cadastre-se em [discord.com](https://discord.com). Você também precisa de um servidor onde seja administrador; crie um clicando no ícone **+** na barra lateral do Discord e selecionando **Create My Own**. Um servidor privado serve.

#### Criar uma aplicação e um bot no Discord

1. Acesse o [Discord Developer Portal](https://discord.com/developers/applications) e clique em **New Application**. Dê um nome a ele (por exemplo, "openclaw-bot").
2. Na barra lateral, clique em **Bot**. Defina um nome de usuário para o bot.
3. Ainda na página Bot, role até **Privileged Gateway Intents** e ative:
   - **Message Content Intent** (obrigatório)
   - **Server Members Intent** (recomendado)
4. Role de volta para cima e clique em **Reset Token** para gerar o token do seu bot. Copie-o.

#### Adicionar o bot ao seu servidor

1. Na barra lateral, clique em **OAuth2/ URL Generator**.
2. Em **Scopes**, ative `bot` e `applications.commands`.
3. Em **Bot Permissions**, ative: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Copie a URL gerada, cole-a no seu navegador, selecione o seu servidor e confirme. O bot deve aparecer na lista de membros do seu servidor.

#### Coletar seus IDs

Ative o Modo Desenvolvedor no Discord (**User Settings/ Advanced/ Developer Mode**), depois:
- Clique com o botão direito no ícone do seu servidor: **Copy Server ID**
- Clique com o botão direito no seu próprio avatar: **Copy User ID**

#### Permitir DMs de membros do servidor

Clique com o botão direito no ícone do seu servidor/ **Privacy Settings**/ ative **Direct Messages**. Isso permite que o bot envie DMs para você, o que é necessário para a etapa de pareamento.

#### Configurar o OpenClaw para o Discord

Armazene o token do seu bot como uma variável de ambiente e, em seguida, crie um único arquivo de patch que ative o Discord, referencie o token e coloque seu servidor na lista de permissões. Substitua `<server_id>` e `<user_id>` pelos IDs coletados acima.

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

> **Não confie em pedir ao agente para configurar isso.** Quando o sandboxing está ativado, o agente não consegue gravar em `~/.openclaw/openclaw.json` de dentro do sandbox; use os comandos de CLI acima no host.

Reinicie o gateway para que ele carregue a nova configuração de canal:

```bash
openclaw gateway run --bind loopback --port 18789
```

Você deve ver `logged in to discord as <bot-name>` na saída do gateway em poucos segundos.
#### Pareie sua conta do Discord

Envie uma DM para o bot no Discord. Ele responderá com um código de pareamento curto.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Aprove-o na máquina que está executando o OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Os códigos de pareamento expiram após uma hora.

Agora você pode conversar com seu agente diretamente pelo Discord e transferir tarefas para seu hardware local.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Opção B: Telegram

O Telegram é mais simples que o Discord para a maioria dos usuários, pois não requer servidor nem acesso de administrador.

#### Criar um bot do Telegram

1. Abra o Telegram e envie uma mensagem para **@BotFather**.
2. Envie `/newbot` e siga as instruções. Guarde o token do bot fornecido.

#### Configurar o OpenClaw para o Telegram

Armazene o token como uma variável de ambiente:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Adicione a configuração do canal em `~/.openclaw/openclaw.json` (ou aplique a alteração pelo painel):

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

Reinicie o gateway e envie qualquer mensagem ao seu bot no Telegram. Aprove o pareamento:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Os códigos de pareamento expiram após uma hora. Agora você pode conversar com seu agente pela DM do Telegram.

---

## Próximos passos

Agora que seu agente pode receber comandos do seu celular e agir na sua máquina local, aqui estão três direções que vale a pena explorar:

1. **Resumidor do mercado de ações**: Programe o OpenClaw para buscar dados de APIs financeiras em um intervalo fixo, resumir as movimentações do dia com seu modelo local e enviar um resumo para o seu celular todas as manhãs pelo canal escolhido.

2. **Monitor de fine-tuning**: Inicie um trabalho de treinamento remotamente pelo Telegram ou Discord e deixe o agente acompanhar o log de treinamento, reportando periodicamente valores de perda, utilização da GPU e uso de disco de volta para o seu celular. Se a execução travar ou a VRAM apresentar picos, você fica sabendo imediatamente sem precisar estar na máquina.

3. **IoT com um VLM local**: Aponte uma câmera para a porta da frente, execute um modelo de visão no Lemonade e deixe o OpenClaw analisar os quadros sob demanda ou por um gatilho. Pergunte "chegou alguma encomenda hoje?" pelo seu celular e obtenha uma resposta direta do seu próprio hardware.

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