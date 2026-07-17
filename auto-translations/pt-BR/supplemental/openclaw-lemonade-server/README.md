<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Execute o OpenClaw com o Lemonade Server como backend

## Visão Geral

[**OpenClaw**](https://openclaw.ai/) é um agente de IA autônomo que pode escrever e executar código, gerenciar arquivos e realizar tarefas complexas de múltiplas etapas em seu nome. Ao contrário de um assistente de chat que apenas responde perguntas, o OpenClaw executa ações reais no seu sistema, o que significa que ele precisa de um backend de IA rápido e capaz de acompanhar um loop de agente exigente.

[**Lemonade Server**](https://lemonade-server.ai/) é esse backend. É um servidor de inferência local de código aberto que executa modelos GenAI diretamente no seu hardware e os expõe por meio da API OpenAI padrão da indústria.

Juntos, eles formam uma pilha de agente de IA totalmente local: o Lemonade cuida da inferência do modelo, e o OpenClaw fornece o loop de agente que transforma as saídas do modelo em ações reais.

> **Antes de continuar:** O OpenClaw é um agente de IA altamente autônomo. Conceder a qualquer agente de IA acesso ao seu sistema pode resultar em resultados imprevisíveis ou não intencionais. Prossiga somente se você entender os riscos e estiver confortável com software autônomo agindo em seu nome.

---

## O Que Você Aprenderá

Ao final deste guia, você será capaz de:

- Aprender sobre o **Lemonade Server**
- **Instalar o OpenClaw** e **apontá-lo para o Lemonade Server** como seu backend de IA.
- **Iniciar o gateway do OpenClaw** e confirmar que seu agente está pronto para trabalhar.
- **Conectar um canal de comunicação** (Discord ou Telegram) para que você possa conversar com seu agente a partir de qualquer dispositivo.

---

## Configurando a Configuração de Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalando Pré-requisitos de Software

<!-- @os:linux -->
- Um PC executando **Ubuntu 24.04+** ou uma distribuição Linux baseada em Debian compatível com `apt-get`
- Pelo menos **12 GB de RAM** (64 GB+ recomendado para modelos maiores)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (Opcional, para isolar o OpenClaw em sandbox)

- **~10–30 GB de espaço livre em disco** para os pesos do modelo
<!-- @os:end -->
<!-- @os:windows -->
- Um PC executando **Windows 10/11**
- Pelo menos **12 GB de RAM** (64 GB+ recomendado para modelos maiores)
- **~10–30 GB de espaço livre em disco** para os pesos do modelo
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (Opcional, para isolar o OpenClaw em sandbox)
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

O modelo recomendado para este guia é o **Qwen3.6-35B-A3B-GGUF** da Unsloth, um modelo MoE robusto com uma janela de contexto de 263k tokens, bem adequado para cargas de trabalho de agentes. Este modelo usa quantização UD-Q4_K_XL. Baixe-o agora:

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

O modelo tem um comprimento de contexto padrão de 262.144 tokens. Se você encontrar erros de falta de memória (OOM), considere reduzir a janela de contexto. No entanto, como o Qwen3.6 aproveita o contexto estendido para tarefas complexas, recomendamos manter um comprimento de contexto de pelo menos 128K tokens para preservar as capacidades de raciocínio.

> **Dica: Desative o raciocínio para respostas de agente mais rápidas:** O Qwen3.6-35B-A3B é executado no modo de raciocínio por padrão, o que adiciona latência antes de cada resposta. Para loops de agente, essa sobrecarga se acumula rapidamente. O repositório [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) fornece uma configuração pronta que desativa o raciocínio. Para usá-la, baixe o arquivo e importe-o:
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

Executamos o OpenClaw dentro do WSL (Recomendado) e o conectamos ao Lemonade em execução nativa no Windows. Isso fornece um ambiente de shell Linux para o OpenClaw enquanto mantém a aceleração GPU do Lemonade no lado do Windows.

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

Execute isso dentro do terminal do Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Reinicie o WSL:

```powershell
wsl --shutdown
wsl
```

### Conectar o Lemonade do Windows ao WSL

O WSL2 é executado em uma rede virtual. O Lemonade no Windows se vincula a `127.0.0.1`, que o WSL não consegue acessar diretamente. Um proxy de porta do Windows encaminha o tráfego do IP do gateway WSL para o localhost do Windows.

**Encontre o IP do gateway WSL** (execute dentro do WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Adicione o proxy de porta** (execute no PowerShell como Administrador, substituindo `<WSL-Gateway-IP>` pelo IP do seu gateway WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

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

> A regra `netsh portproxy` sobrevive a reinicializações, mas o IP do gateway WSL pode mudar após `wsl --shutdown`. Se o Lemonade ficar inacessível a partir do WSL após uma reinicialização, obtenha o IP do gateway atualizado e atualize o proxy com esse novo IP.

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

O sinalizador `--no-onboard` ignora o assistente de configuração interativo; você configurará o backend do modelo manualmente na próxima etapa, o que lhe dá controle preciso sobre qual modelo e servidor são usados.

Abra um novo terminal e confirme a instalação:

```bash
openclaw --version
```

> **Dica:** Se você vir `command not found` após a instalação, adicione o diretório bin global do npm ao seu PATH:
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

> **Dimensionamento da janela de contexto do OpenClaw:** A compactação do OpenClaw é acionada quando `contextTokens > contextWindow − reserveTokens`. O `reserveTokensFloor` padrão é 20.000 tokens, um limite mínimo que substitui `reserveTokens` quando menor, portanto qualquer contexto de modelo abaixo de ~37k acionará um loop de compactação infinito. Defina uma reserva baixa e desative o limite mínimo uma vez em sua configuração e isso se aplica a todos os modelos, sem necessidade de ajuste por modelo:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` é um *limite mínimo* (guarda mínimo), não a reserva em si; definir apenas o limite mínimo não tem efeito. `reserveTokensFloor: 0` desativa a guarda para que o `reserveTokens` menor seja aceito.
>
> **Quando aplicar isso:** Use esta configuração se a janela de contexto efetiva do seu modelo estiver abaixo de ~37k, seja porque o modelo é pequeno (por exemplo, 8k, 16k, 32k) ou porque você o limitou intencionalmente a um valor menor (por exemplo, carregando um modelo de 128k mas definindo o contexto para 16k no Lemonade). Sem isso, o OpenClaw entra em um loop de compactação infinito na inicialização.
>
> **Modelos de contexto grande em contexto completo:** Você pode ignorar isso completamente. Os padrões funcionam bem; a compactação será acionada bem antes de a janela ser preenchida e o modelo tem espaço suficiente para gerar respostas longas. Se você aplicar isso, esteja ciente de que `reserveTokens: 4096` limita o comprimento da resposta a ~4k tokens, o que pode interromper a geração de arquivos longos ou planos detalhados.
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
> O restante da sua configuração (gateway, canais, modelos, etc.) permanece inalterado; apenas a chave `compaction` precisa ser adicionada.

### (Recomendado) Habilitar Sandboxing com Docker

O OpenClaw pode rotear todas as operações de arquivo e código do agente por meio de um contêiner Docker isolado, em vez de executá-las diretamente no seu host. Isso limita o impacto de qualquer ação não intencional ao sandbox, deixando o sistema de arquivos e a rede do host intocados.

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

Execute isso para adicionar a chave `sandbox` dentro do bloco `agents.defaults` existente em `~/.openclaw/openclaw.json`:

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

Os contêineres sandbox **não têm acesso à rede** por padrão. Consulte a [referência de sandboxing](https://docs.openclaw.ai/gateway/sandboxing) para montagens de bind e substituições de rede.

> #### Solução de Problemas: Permissão Negada no Docker
> 
> Se você receber "permission denied" ao executar comandos Docker:
> 
> **Etapa 1: Adicione seu usuário ao grupo docker**
> 
> ```bash
> sudo groupadd docker                    # Crie o grupo se necessário
> sudo usermod -aG docker $USER           # Adicione-se ao grupo
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
> Em seguida, **reinicie** o seu sistema.
> 
> **Correção temporária rápida** (redefine após reinicialização):
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

### Iniciar o Gateway do OpenClaw

O gateway é o processo do OpenClaw que gerencia o loop do agente e serve o painel:

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

Para abrir o painel, execute isso em um segundo terminal enquanto o gateway ainda estiver em execução:

```bash
openclaw dashboard
```

Como o gateway se vincula ao loopback, o painel se autentica automaticamente quando aberto na mesma máquina — nenhuma entrada de token ou aprovação de dispositivo é necessária para acesso local. Você deverá ver o painel do OpenClaw com seu modelo Lemonade listado como o backend ativo.

> Se você habilitou o sandboxing, pode verificá-lo pedindo ao agente para `run hostname` no painel. Se você vir um ID de contêiner curto em vez do nome do host da sua máquina, o sandbox está funcionando.

**Parabéns, você construiu uma pilha de agente de IA totalmente local do zero.**

> **Precisa do token do gateway?** Execute `openclaw dashboard --no-open` para imprimir a URL do painel com o token incorporado (ele também tenta copiá-lo para a área de transferência). Como alternativa, o token está em `gateway.auth.token` em `~/.openclaw/openclaw.json`.
>
> **Aprovando um dispositivo remoto:** Quando você abre o painel a partir de uma segunda máquina ou telefone, o navegador exibe um ID de solicitação. De volta à máquina que executa o gateway, execute:
> ```bash
> openclaw devices approve <requestId>
> ```
> Isso só é necessário para dispositivos remotos ou secundários; o acesso por loopback da mesma máquina é autenticado automaticamente.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Opcional: Conectar um Canal de Comunicação

Assim que o gateway estiver em execução, você pode acessar seu agente local a partir de qualquer dispositivo. Escolha a opção que se adapta à sua configuração. O OpenClaw suporta [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) e outros canais — consulte a lista completa em [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Opção A: Discord

O Discord requer um servidor onde **você tenha acesso de administrador** para adicionar um bot. Se você compartilha servidores, mas não possui nenhum, use a Opção B (Telegram).

#### Criar uma conta e servidor no Discord

Se você não tiver uma conta no Discord, cadastre-se em [discord.com](https://discord.com). Você também precisa de um servidor onde seja administrador — crie um clicando no ícone **+** na barra lateral do Discord e selecionando **Criar o Meu**. Um servidor privado é suficiente.

#### Criar um aplicativo e bot no Discord

1. Acesse o [Portal do Desenvolvedor do Discord](https://discord.com/developers/applications) e clique em **New Application**. Dê um nome a ele (por exemplo, "openclaw-bot").
2. Na barra lateral, clique em **Bot**. Defina um nome de usuário para o bot.
3. Ainda na página do Bot, role até **Privileged Gateway Intents** e habilite:
   - **Message Content Intent** (obrigatório)
   - **Server Members Intent** (recomendado)
4. Role de volta para cima e clique em **Reset Token** para gerar seu token de bot. Copie-o.

#### Adicionar o bot ao seu servidor

1. Na barra lateral, clique em **OAuth2/ URL Generator**.
2. Em **Scopes**, habilite `bot` e `applications.commands`.
3. Em **Bot Permissions**, habilite: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Copie a URL gerada, cole-a no seu navegador, selecione seu servidor e confirme. O bot agora deve aparecer na lista de membros do seu servidor.

#### Coletar seus IDs

Habilite o Modo Desenvolvedor no Discord (**Configurações do Usuário/ Avançado/ Modo Desenvolvedor**), depois:
- Clique com o botão direito no ícone do seu servidor: **Copiar ID do Servidor**
- Clique com o botão direito no seu avatar: **Copiar ID do Usuário**

#### Permitir DMs de membros do servidor

Clique com o botão direito no ícone do seu servidor/ **Configurações de Privacidade**/ ative **Mensagens Diretas**. Isso permite que o bot envie DMs para você, o que é necessário para a etapa de emparelhamento.

#### Configurar o OpenClaw para Discord

Armazene seu token de bot como uma variável de ambiente, depois crie um único arquivo de patch que habilita o Discord, referencia o token e coloca seu servidor na lista de permissões. Substitua `<server_id>` e `<user_id>` pelos IDs coletados acima.

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

> **Não confie em pedir ao agente para configurar isso.** Quando o sandboxing está habilitado, o agente não pode gravar em `~/.openclaw/openclaw.json` de dentro do sandbox — use os comandos CLI acima no host.

Reinicie o gateway para que ele reconheça a nova configuração de canal:

```bash
openclaw gateway run --bind loopback --port 18789
```

Você deverá ver `logged in to discord as <bot-name>` na saída do gateway em alguns segundos.

#### Emparelhar sua conta do Discord

Envie uma DM para o bot no Discord. Ele responderá com um código de emparelhamento curto.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Aprove-o na máquina que executa o OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Os códigos de emparelhamento expiram após uma hora.

Agora você pode conversar com seu agente diretamente pelo Discord e delegar tarefas ao seu hardware local.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Opção B: Telegram

O Telegram é mais simples do que o Discord para a maioria dos usuários — não requer servidor nem acesso de administrador.

#### Criar um bot no Telegram

1. Abra o Telegram e envie uma mensagem para **@BotFather**.
2. Envie `/newbot` e siga as instruções. Salve o token do bot que ele fornecer.

#### Configurar o OpenClaw para Telegram

Armazene o token como uma variável de ambiente:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Adicione a configuração do canal em `~/.openclaw/openclaw.json` (ou aplique o patch pelo painel):

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

Reinicie o gateway, depois envie qualquer mensagem para o seu bot no Telegram. Aprove o emparelhamento:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Os códigos de emparelhamento expiram após uma hora. Agora você pode conversar com seu agente via DM no Telegram.

---

## Próximos Passos

Agora que seu agente pode receber comandos do seu telefone e agir na sua máquina local, aqui estão três direções que vale a pena explorar:

1. **Resumidor do mercado de ações**: Agende o OpenClaw para buscar dados de APIs financeiras em um intervalo fixo, resumir os movimentos do dia com seu modelo local e enviar um resumo para o seu telefone toda manhã pelo canal escolhido.

2. **Monitor de ajuste fino**: Inicie um trabalho de treinamento remotamente via Telegram ou Discord, depois peça ao agente para monitorar o log de treinamento e reportar periodicamente os valores de perda, utilização de GPU e uso de disco para o seu telefone. Se a execução travar ou o VRAM disparar, você saberá imediatamente sem precisar estar na máquina.

3. **IOT com um VLM local**: Aponte uma câmera para a sua porta da frente, execute um modelo de visão no Lemonade e peça ao OpenClaw para analisar os frames sob demanda ou por gatilho. Pergunte "chegou algum pacote hoje?" pelo seu telefone e obtenha uma resposta direta do seu próprio hardware.