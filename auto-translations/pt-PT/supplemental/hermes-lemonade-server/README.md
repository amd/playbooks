<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente a partir do inglês e não foi revista por um humano. Pode conter erros, e determinadas instruções, comandos, transferências, disponibilidade de produtos ou outro conteúdo podem variar consoante o idioma ou a região. Em caso de qualquer inconsistência ou discrepância, prevalece a versão original em inglês do playbook.
<!-- auto-translated-disclaimer:end -->

# Executar o Hermes Agent Localmente com o Lemonade Server

## Visão geral

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) é um agente de IA de auto-aperfeiçoamento criado pela Nous Research. Tem um ciclo de aprendizagem integrado, cria competências a partir da experiência, constrói uma memória persistente sobre quem é o utilizador entre sessões, e pode executar automações agendadas em seu nome. Ao contrário de um simples assistente de conversação, o Hermes realiza ações reais: executa comandos de shell, escreve ficheiros, navega na web e delega fluxos de trabalho paralelos a subagentes.

[**Lemonade Server**](https://lemonade-server.ai/) é o motor de inferência local que o alimenta. É um servidor de código aberto que executa modelos de IA generativa diretamente no seu hardware AMD e os disponibiliza através da API padrão da indústria, a OpenAI API.

Em conjunto, formam uma pilha de agente de IA totalmente local: o Lemonade trata da inferência do modelo na sua GPU, e o Hermes fornece o ciclo do agente, a memória, as competências e a gateway de mensagens.

> **Antes de continuar:** o Hermes Agent é um agente de IA altamente autónomo. Dar a qualquer agente de IA acesso ao seu sistema pode resultar em resultados imprevisíveis ou não intencionais. Prossiga apenas se compreender os riscos e estiver confortável com software autónomo a agir em seu nome.

---

## O Que Vai Aprender

No final deste guia, será capaz de:

- **Instalar o Hermes Agent** e configurá-lo para usar o **Lemonade Server** como o seu motor de IA.
- **(Recomendado) Ativar o sandboxing com Docker/Podman** para isolar as ações do agente do seu sistema anfitrião.
- **Iniciar a gateway do Hermes** e confirmar que o seu agente está pronto.
- **Ligar um canal de comunicação** (Discord ou Telegram) para poder conversar com o seu agente a partir de qualquer dispositivo.

---

## Configurar a Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalar os Pré-requisitos de Software

<!-- @os:linux -->
- Um PC com **Ubuntu 24.04+** ou uma distribuição Linux compatível baseada em Debian com `apt-get`
- Pelo menos **12 GB de RAM** (64 GB+ recomendado para modelos maiores)
- **~10–30 GB de espaço livre em disco** para os pesos do modelo
- [Podman](https://podman.io/docs/installation) (Opcional, para sandboxing do Hermes Agent)
  ```bash 
  sudo apt-get install -y podman`
  ```
<!-- @os:end -->

<!-- @os:windows -->
- Um PC com **Windows 10/11**
- Pelo menos **12 GB de RAM** (64 GB+ recomendado para modelos maiores)
- **~10–30 GB de espaço livre em disco** para os pesos do modelo
- Podman (Opcional, para sandboxing do Hermes Agent). Instalar dentro do WSL:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> O Podman já vem pré-instalado na Halo Box e não é necessária qualquer configuração
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Obter e Carregar o Modelo Recomendado

O modelo recomendado para este guia é o **Qwen3.6-35B-A3B-GGUF** da Unsloth, um modelo MoE robusto com uma janela de contexto de 263k tokens, bem adequado a cargas de trabalho de agentes. Este modelo utiliza quantização UD-Q4_K_XL. Obtenha-o agora:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

De seguida, carregue-o com uma janela de contexto ampla e guarde essa definição para execuções futuras:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

O modelo tem um comprimento de contexto predefinido de 262.144 tokens. Se encontrar erros de falta de memória (OOM), considere reduzir a janela de contexto.

> **Dica: Desative o modo de pensamento para respostas de agente mais rápidas:** O Qwen3.6-35B-A3B executa por predefinição em modo de pensamento, o que acrescenta latência antes de cada resposta. Nos ciclos de agente, esta sobrecarga acumula-se rapidamente. O repositório [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) fornece uma configuração pronta que desativa o pensamento. Para a utilizar, transfira o ficheiro e importe-o:
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
$entry = $parsed.data | Where-Object { $_.id -eq "${hermes_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${hermes_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${hermes_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${hermes_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${hermes_model} is not saved with ctx_size=262144. Run: lemonade load ${hermes_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${hermes_model} is saved with ctx_size=262144"

$body = @{
  model = "${hermes_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "hermes-lemonade-chat-body.json"
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
model_id = "${hermes_model}"

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
  "model": "${hermes_model}",
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

Executamos o Hermes Agent dentro do WSL e ligamo-lo ao Lemonade que é executado nativamente no Windows. Isto proporciona um ambiente de shell Linux para o Hermes, mantendo a aceleração por GPU do Lemonade no lado do Windows.

### Instalar o WSL e o Ubuntu

Abra o PowerShell como Administrador e instale o kernel do WSL:

```powershell
wsl --install --no-distribution
```

De seguida, instale o Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Ativar o systemd no WSL

Execute o seguinte dentro do terminal do Ubuntu:

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

### Estabelecer uma ponte entre o Lemonade no Windows e o WSL

O WSL2 é executado numa rede virtual. O Lemonade no Windows associa-se ao `127.0.0.1`, ao qual o WSL não consegue aceder diretamente. Um proxy de porta do Windows encaminha o tráfego do IP de gateway do WSL para o localhost do Windows.

**Encontre o seu IP de gateway do WSL** (execute dentro do WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Adicione o proxy de porta** (execute no PowerShell como Administrador, substituindo `<WSL-Gateway-IP>` pelo seu IP de gateway do WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Adicione uma regra de firewall** (no mesmo PowerShell elevado):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Verifique a partir do WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Se já tiver carregado o modelo Qwen3.6-35B-A3B-GGUF no passo anterior, deverá ver uma saída JSON a listar o seu modelo carregado.

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

> A regra `netsh portproxy` sobrevive a reinícios, mas o IP de gateway do WSL pode mudar após um `wsl --shutdown`. Se o Lemonade se tornar inacessível a partir do WSL depois de um reinício, obtenha o IP de gateway atualizado e atualize o proxy com este novo IP.

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
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

## Instalar o Hermes Agent

<!-- @os:windows -->
> Execute os comandos desta secção dentro do seu **terminal WSL**, exceto quando indicado em contrário.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

A flag `--skip-setup` ignora o assistente de configuração interativo, para que possa configurar o motor do modelo manualmente no passo seguinte.

Recarregue a sua shell:

```bash
source ~/.bashrc
```

Confirme a instalação:

```bash
hermes --version
```

Execute um autodiagnóstico para verificar todas as dependências:

```bash
hermes doctor
```

> **Dica:** Se vir `command not found` após a instalação, adicione o Hermes ao seu PATH:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> Para tornar isto permanente, adicione a linha acima ao seu ficheiro `~/.bashrc` ou `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=hermes-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---
## Configurar o Hermes para Usar o Lemonade

O Hermes armazena a sua configuração de modelo em `~/.hermes/config.yaml`. Pode usar o seletor interativo `hermes model` ou escrever a configuração diretamente.

### Opção 1: Seletor interativo

<!-- @os:windows -->
> Execute o seguinte comando dentro do seu **terminal WSL**.
<!-- @os:end -->

<!-- @os:linux -->
```bash
hermes model
```
<!-- @os:end -->

<!-- @os:windows -->
```bash
hermes model
```
<!-- @os:end -->

Quando solicitado:

1. Selecione **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** utilize o IP da gateway do WSL: execute `ip route show default | awk '{print $3}' | head -1` dentro do WSL para o obter e, em seguida, introduza `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Auto-detect)
5. **Select model:** escolha `Qwen3.6-35B-A3B-GGUF` da lista
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (ou qualquer nome que preferir)

`hermes model` guarda tanto a seleção do modelo ativo como uma entrada nomeada em `custom_providers` que armazena o comprimento do contexto juntamente com o endpoint. O resultado em `~/.hermes/config.yaml` fica assim:

```yaml
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
```

### Opção 2: Escrever a configuração diretamente

<!-- @os:linux -->

```bash
mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->

Dentro do seu terminal WSL, obtenha o IP do anfitrião Windows e escreva a configuração:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"
if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration (Windows host)"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-lemonade-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes Lemonade config check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---

## (Recomendado) Ativar o Sandboxing com Podman

O Hermes Agent pode encaminhar todas as operações de shell e de ficheiros do agente através de um contentor isolado, em vez de as executar diretamente no seu anfitrião. Isto limita o raio de impacto de qualquer ação não intencional à sandbox, deixando o sistema de ficheiros e a rede do seu anfitrião intactos.

Construa uma imagem de sandbox leve:

<!-- @os:linux -->
```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @test:id=hermes-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
Entre no seu terminal WSL:

```powershell
wsl -d Ubuntu-24.04
```

Em seguida, construa uma imagem de sandbox leve:

```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @test:id=hermes-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Em seguida, configure o Hermes para usar o Podman como runtime de contentores e defina o backend do terminal:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> O `terminal.backend` continua a ser `docker`.
> `HERMES_DOCKER_BINARY` é o que indica ao Hermes para usar o Podman como runtime em vez disso.

<!-- @os:linux -->
<!-- @test:id=hermes-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

# The sandbox image must exist before Hermes can use it as the terminal backend.
podman image inspect hermes-sandbox:bookworm-slim >/dev/null

# Point Hermes at Podman as the container runtime (idempotent: drop any prior line first).
mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

# Append the terminal backend block (config.yaml is rewritten fresh by the model-config test each run, so this appends exactly once per run).
cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox config failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

O Hermes irá agora iniciar um contentor de sandbox persistente e encaminhar todas as chamadas de `terminal` e de ferramentas de ficheiros através dele. O contentor partilha o ciclo de vida do processo do Hermes, é reutilizado em todas as chamadas de ferramentas e é destruído quando o Hermes termina.

> **Verificar se a sandbox está a funcionar:** Inicie o Hermes (`hermes`) e peça-lhe para `run hostname` - deverá ver um ID de contentor curto em vez do nome de anfitrião da sua máquina. Também pode pedir-lhe para `rm -rf <path-to-a-dummy-file/folder>`: o Hermes irá confirmar a eliminação, mas a pasta continuará no seu anfitrião. O comando foi executado dentro do `$HOME` isolado do contentor, e não do seu.

> **Precisa de isolamento mais forte?** O Hermes também disponibiliza uma imagem Docker oficial (`nousresearch/hermes-agent`) que executa todo o processo do agente dentro de um contentor - gateway, ferramentas e tudo o resto. Consulte a [documentação Docker do Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/docker) para detalhes de configuração.

---

<!-- @os:linux -->
## (Recomendado) Integração do Hermes com Serviços Firecrawl

O Hermes consegue navegar e extrair conteúdo de sites web usando as suas ferramentas web integradas. No entanto, muitos sites web modernos utilizam sistemas de deteção de bots, que bloqueiam pedidos HTTP simples e devolvem páginas de desafio em vez do conteúdo real. Como resultado, o Hermes pode não conseguir extrair informação de forma fiável a partir destes sites.

Para ultrapassar esta limitação, o [Firecrawl](https://docs.firecrawl.dev/introduction) fornece um serviço de crawling web e extração de conteúdo auto-alojado que consegue contornar estes desafios e desbloquear todo o potencial da automação do Hermes.

Nesta configuração, o Firecrawl é executado como um conjunto de contentores Docker geridos com o Podman. Para simplificar a gestão do ciclo de vida e o arranque automático, registamos o Firecrawl como um serviço `systemd` ao nível do utilizador que orquestra a stack subjacente do Podman Compose. Isto permite que o Hermes inicie, pare e verifique o serviço Firecrawl usando comandos padrão `systemctl --user`, em vez de interagir diretamente com os contentores.

Para manter as coisas simples, dividimos todo o processo em quatro passos:

---

### 1. Registar o serviço do sistema
Navegue até ao diretório de configuração do utilizador do systemd:
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
Description=Firecrawl
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${HOME}/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman -f hermes-compose.yaml config --quiet

# Start containers in detached mode
ExecStart=/usr/bin/podman compose -f hermes-compose.yaml up -d --remove-orphans

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f hermes-compose.yaml down

[Install]
WantedBy=default.target

```
Neste ponto, o serviço foi definido, mas ainda não foi registado no `systemd`.
Certifique-se de que o nome do ficheiro corresponde exatamente ao que criou acima e, em seguida, execute:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Se for bem-sucedido, deverá ver a seguinte saída:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

`default.target.wants/` contém ligações simbólicas para serviços configurados para iniciar automaticamente.

### 2. Configurar o Firecrawl para o Seu Serviço

O [SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) é ideal para quem precisa de controlo total sobre os seus ambientes de scraping e processamento de dados, mas tem como contrapartida esforços adicionais de manutenção e configuração.

Comece por clonar o repositório:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Crie o `.env` no diretório raiz `/firecrawl`:
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY=""

# ===== Proxy =====
# PROXY_SERVER can be a full URL (e.g. http://0.1.2.3:1234) or just an IP and port combo (e.g. 0.1.2.3:1234)
# Do not uncomment PROXY_USERNAME and PROXY_PASSWORD if your proxy is unauthenticated
# PROXY_SERVER=
# PROXY_USERNAME=
# PROXY_PASSWORD=

# This key lets you access the queue admin panel. Change this if your deployment is publicly accessible.
BULL_AUTH_KEY=CHANGEME

# ===== System Resource Configuration =====
# Maximum CPU usage threshold (0.0-1.0). Worker will reject new jobs when CPU usage exceeds this value.
# Default: 0.8 (80%)
# MAX_CPU=0.8

# Maximum RAM usage threshold (0.0-1.0). Worker will reject new jobs when memory usage exceeds this value.
# Default: 0.8 (80%)
# MAX_RAM=0.8
```
> Defina `BULL_AUTH_KEY` com um segredo forte, especialmente em qualquer implementação acessível a partir de redes não fiáveis.
### 3. Implementar o Hermes através do Compose

Antes de continuar, certifique-se de que já obteve a imagem Docker mais recente do Hermes:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
Feito isso, transfira o ficheiro Compose do Hermes [hermes-compose.yaml](assets/hermes-compose.yaml) e coloque-o no diretório raiz `/firecrawl`:

> Esta convenção é necessária para que o `systemd` localize e inicie o serviço corretamente, conforme especificado em `WorkingDirectory=${HOME}/firecrawl`.

> Pode sempre expandir a stack adicionando serviços Firecrawl adicionais conforme necessário. A lista completa de serviços disponíveis pode ser consultada no [docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) oficial do Firecrawl.

### 4. Iniciar o serviço Hermes através do Firecrawl 

Antes de entregar o controlo ao `systemd`, verifique que tudo funciona corretamente executando a stack manualmente:
```bash
podman compose -f hermes-compose.yaml up -d
```
Se tudo estiver configurado corretamente, deverá ver o contentor Hermes a arrancar e a saída da sua linha de comandos deverá ser semelhante a esta:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

Após a verificação, encerre a stack antes de continuar:
```bash
podman compose -f hermes-compose.yaml down
```
Agora que tudo foi validado, inicie o serviço através do `systemd`:
```bash
systemctl --user start firecrawl.service
```
[A API do Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) está acessível a partir do contentor interativo, e o Painel Web está disponível no mesmo anfitrião e porta em http://127.0.0.1:9119.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

Para parar o serviço, execute:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

Inicie uma sessão CLI interativa diretamente: 

```bash
hermes
```

<!-- @os:linux -->
<!-- @test:id=hermes-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started successfully"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started inside WSL"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

**Parabéns, construiu uma stack de agente de IA totalmente local.**

### Painel Web

O Hermes inclui uma interface baseada no browser para gerir configurações, chaves de API, modelos, sessões, memória e tarefas cron. Abra um segundo terminal enquanto o gateway ou a CLI estiver em execução e inicie-o com:

```bash
hermes dashboard
```

Isto inicia um servidor local e abre `http://127.0.0.1:9119` no seu browser. Consulte a [documentação do painel](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard) para a referência completa das funcionalidades.
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## Opcional: Ligar um canal de comunicação

Uma vez o gateway em execução, pode aceder ao seu agente local a partir de qualquer dispositivo. O Hermes suporta [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram), entre outros

---

### Discord

O Discord requer um servidor onde **tenha acesso de administrador** para adicionar um bot. Se partilhar servidores mas não for proprietário de nenhum, utilize o Telegram.

#### Criar uma aplicação e um bot do Discord

1. Aceda ao [Portal de Programadores do Discord](https://discord.com/developers/applications) e clique em **New Application**. Dê-lhe um nome (por exemplo, "hermes-bot").
2. Na barra lateral, clique em **Bot**. Defina um nome de utilizador para o bot.
3. Ainda na página Bot, desça até **Privileged Gateway Intents** e ative:
   - **Message Content Intent** (obrigatório)
   - **Server Members Intent** (recomendado)
4. Volte a subir e clique em **Reset Token** para gerar o seu token de bot. Copie-o.

#### Adicionar o bot ao seu servidor

1. Na barra lateral, clique em **OAuth2 / URL Generator**.
2. Em **Scopes**, ative `bot` e `applications.commands`.
3. Em **Bot Permissions**, ative: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Copie o URL gerado, cole-o no seu browser, selecione o seu servidor e confirme.

#### Recolher os seus IDs e permitir DMs

Ative o Modo de Programador no Discord (**User Settings / Advanced / Developer Mode**) e, em seguida:
- Clique com o botão direito no ícone do seu servidor: **Copy Server ID**
- Clique com o botão direito no seu próprio avatar: **Copy User ID**

Clique com o botão direito no ícone do seu servidor / **Privacy Settings** / ative **Direct Messages**. Isto é necessário para o passo de emparelhamento.

#### Configurar o Hermes para o Discord

Adicione o seguinte ao ficheiro `~/.hermes/.env`:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

Depois inicie o gateway:

```bash
hermes gateway
```

O bot deverá ficar online no Discord em poucos segundos. Envie-lhe uma mensagem, seja uma DM ou num canal onde o bot tenha visibilidade.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Criar um bot do Telegram

1. Abra o Telegram e envie uma mensagem a **@BotFather**.
2. Envie `/newbot` e siga as instruções. Guarde o token do bot que lhe for fornecido.

#### Configurar o Hermes para o Telegram

Adicione o seguinte ao ficheiro `~/.hermes/.env`:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Não sabe qual é o seu ID de utilizador do Telegram?** Envie uma mensagem a [@userinfobot](https://t.me/userinfobot) no Telegram, ele responderá com o seu ID numérico.

Depois inicie o gateway:

```bash
hermes gateway
```

Envie qualquer mensagem ao seu bot no Telegram para testar. Já pode conversar com o seu agente através de DM no Telegram. Consulte o [guia completo de configuração do Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) para o modo webhook e opções avançadas.

---

## Próximos passos

Agora que o seu agente pode receber comandos a partir do telemóvel e agir na sua máquina local, aqui estão três direções que vale a pena explorar:

1. **Resumo de pesquisa automatizado**: Programe o Hermes para pesquisar na Web tópicos do seu interesse todas as manhãs, resumir os resultados com o seu modelo local e enviar um resumo para o seu telemóvel via Telegram ou Discord, tudo a funcionar no seu próprio hardware sem custos na nuvem.

2. **Revisão de código a pedido**: Aponte o Hermes para um repositório do GitHub, peça-lhe que reveja pull requests abertos e faça-o publicar comentários ou um resumo de volta no seu chat. Com o backend de terminal Docker, todas as operações git são executadas dentro da sandbox, mantendo o seu anfitrião limpo.

3. **Assistente de ficheiros local**: Dê ao Hermes acesso a um diretório de trabalho e peça-lhe que organize, renomeie, resuma ou transforme ficheiros a pedido a partir do seu telemóvel. Como o backend de terminal Docker confina todas as escritas ao espaço de trabalho da sandbox, operações destrutivas acidentais ficam contidas.