<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Rulați OpenClaw cu Lemonade Server ca backend

## Prezentare generală

[**OpenClaw**](https://openclaw.ai/) este un agent AI autonom care poate scrie și rula cod, gestiona fișiere și parcurge sarcini complexe în mai multe etape în numele dumneavoastră. Spre deosebire de un asistent de chat care doar răspunde la întrebări, OpenClaw efectuează acțiuni reale pe sistemul dumneavoastră, ceea ce înseamnă că are nevoie de un backend AI rapid și capabil, care să facă față unui ciclu de agent solicitant.

[**Lemonade Server**](https://lemonade-server.ai/) este acel backend. Este un server de inferență local open-source care rulează modele GenAI direct pe hardware-ul dumneavoastră și le expune printr-un API standard în industrie, compatibil cu OpenAI.

Împreună, formează un stack de agent AI complet local: Lemonade se ocupă de inferența modelului, iar OpenClaw oferă ciclul de agent care transformă rezultatele modelului în acțiuni reale.

> **Înainte de a continua:** OpenClaw este un agent AI extrem de autonom. Oferirea accesului la sistemul dumneavoastră oricărui agent AI poate duce la rezultate imprevizibile sau neintenționate. Continuați numai dacă înțelegeți riscurile și sunteți confortabil cu software autonom care acționează în numele dumneavoastră.

---

## Ce veți învăța

Până la finalul acestui ghid veți putea:

- Afla despre **Lemonade Server**
- **Instala OpenClaw** și **îl configura să folosească Lemonade Server** ca backend AI.
- **Porni gateway-ul OpenClaw** și confirma că agentul dumneavoastră este pregătit să lucreze.
- **Conecta un canal de comunicare** (Discord sau Telegram) pentru a putea discuta cu agentul dumneavoastră de pe orice dispozitiv.

---

## Configurarea memoriei

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificarea actualizărilor software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalarea cerințelor prealabile software

<!-- @os:linux -->
- Un PC care rulează **Ubuntu 24.04+** sau o distribuție Linux compatibilă bazată pe Debian, cu `apt-get`
- Cel puțin **12 GB de RAM** (64 GB+ recomandat pentru modele mai mari)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (Opțional, pentru izolarea (sandboxing) OpenClaw)

- **~10–30 GB spațiu liber pe disc** pentru ponderile modelului
<!-- @os:end -->
<!-- @os:windows -->
- Un PC care rulează **Windows 10/11**
- Cel puțin **12 GB de RAM** (64 GB+ recomandat pentru modele mai mari)
- **~10–30 GB spațiu liber pe disc** pentru ponderile modelului
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (Opțional, pentru izolarea (sandboxing) OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Descărcați și încărcați modelul recomandat

Modelul recomandat pentru acest ghid este **Qwen3.6-35B-A3B-GGUF** de la Unsloth, un model MoE puternic cu o fereastră de context de 263k tokeni, foarte potrivit pentru sarcinile de agent. Acest model folosește cuantizarea UD-Q4_K_XL. Descărcați-l acum:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Apoi încărcați-l cu o fereastră de context mare și salvați această setare pentru rulările viitoare:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Modelul are o lungime de context implicită de 262.144 tokeni. Dacă întâmpinați erori de memorie insuficientă (OOM), luați în considerare reducerea ferestrei de context. Totuși, deoarece Qwen3.6 folosește context extins pentru sarcini complexe, vă recomandăm să mențineți o lungime de context de cel puțin 128K tokeni pentru a păstra capacitățile de raționament.

> **Sfat: Dezactivați modul de raționament pentru răspunsuri mai rapide ale agentului:** Qwen3.6-35B-A3B rulează implicit în modul de raționament (thinking mode), ceea ce adaugă latență înainte de fiecare răspuns. Pentru ciclurile de agent, această suprasarcină se acumulează rapid. Depozitul [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) oferă o configurație gata făcută care dezactivează raționamentul. Pentru a o utiliza, descărcați fișierul și importați-l:
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

## Configurarea WSL

Rulăm OpenClaw în interiorul WSL (Recomandat) și îl conectăm la Lemonade, care rulează nativ pe Windows. Astfel obțineți un mediu shell Linux pentru OpenClaw, păstrând în același timp accelerarea GPU a Lemonade pe partea Windows.

### Instalați WSL și Ubuntu

Deschideți PowerShell ca Administrator și instalați kernelul WSL:

```powershell
wsl --install --no-distribution
```

Apoi instalați Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Activați systemd în WSL

Rulați această comandă în terminalul Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Reporniți WSL:

```powershell
wsl --shutdown
wsl
```

### Conectați (bridge) Lemonade de pe Windows în WSL

WSL2 rulează într-o rețea virtuală. Lemonade de pe Windows se leagă la `127.0.0.1`, la care WSL nu poate ajunge direct. Un proxy de port Windows redirecționează traficul de la IP-ul de gateway WSL către localhost-ul Windows.

**Găsiți IP-ul de gateway WSL** (rulați în interiorul WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Adăugați proxy-ul de port** (rulați în PowerShell ca Administrator, înlocuind `<WSL-Gateway-IP>` cu IP-ul dumneavoastră de gateway WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Adăugați o regulă de firewall** (același PowerShell ridicat):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Verificați din WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Dacă ați încărcat deja modelul Qwen3.6-35B-A3B-GGUF în pasul anterior, ar trebui să vedeți un rezultat JSON precum acesta:

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

> Regula `netsh portproxy` supraviețuiește repornirilor, dar IP-ul de gateway WSL se poate schimba după `wsl --shutdown`. Dacă Lemonade devine inaccesibil din WSL după o repornire, obțineți IP-ul de gateway actualizat și actualizați proxy-ul cu acest nou IP.

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

## Instalarea și configurarea OpenClaw

### Instalați OpenClaw
<!-- @os:windows -->
> Rulați comenzile din această secțiune în interiorul terminalului **WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Opțiunea `--no-onboard` omite asistentul interactiv de configurare; veți configura manual backend-ul modelului în pasul următor, ceea ce vă oferă control precis asupra modelului și serverului utilizate.

Deschideți un terminal nou și confirmați instalarea:

```bash
openclaw --version
```

> **Sfat:** Dacă vedeți `command not found` după instalare, adăugați directorul global bin al npm la PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Pentru a face acest lucru permanent, adăugați linia de mai sus în fișierul dumneavoastră `~/.bashrc` sau `~/.zshrc`.

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
### Configurați OpenClaw pentru a utiliza Lemonade

Rulați integrarea non-interactivă a OpenClaw.
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

Această comandă scrie configurația OpenClaw în `~/.openclaw/openclaw.json`.

> **Dimensionarea ferestrei de context OpenClaw:** Compactarea OpenClaw se declanșează atunci când `contextTokens > contextWindow − reserveTokens`. Valoarea implicită `reserveTokensFloor` este de 20.000 de token-uri, un prag minim care suprascrie `reserveTokens` atunci când acesta este mai mic, astfel încât orice context de model sub ~37k va declanșa o buclă infinită de compactare. Setați o rezervă mică și dezactivați pragul minim o singură dată în configurația voastră, iar aceasta se va aplica fiecărui model, fără a fi nevoie de ajustare pentru fiecare model în parte:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` reprezintă un *prag minim* (o valoare de siguranță), nu rezerva propriu-zisă; setarea doar a acestui prag nu are niciun efect. `reserveTokensFloor: 0` dezactivează garda, astfel încât valoarea mai mică `reserveTokens` este acceptată.
>
> **Când se aplică:** Utilizați această configurație dacă fereastra de context efectivă a modelului dumneavoastră este sub ~37k, fie deoarece modelul este mic (de ex. 8k, 16k, 32k), fie deoarece ați limitat intenționat contextul la o valoare mai mică (de ex. încărcați un model de 128k, dar setați contextul la 16k în Lemonade). Fără această setare, OpenClaw intră într-o buclă infinită de compactare la pornire.
>
> **Modele cu context mare, la context complet:** Puteți omite complet acest pas. Valorile implicite funcționează bine, compactarea se va declanșa cu mult înainte ca fereastra să se umple, iar modelul va avea spațiu suficient pentru a genera răspunsuri lungi. Dacă totuși aplicați această setare, rețineți că `reserveTokens: 4096` limitează lungimea răspunsului la ~4k token-uri, ceea ce poate trunchia generarea de fișiere lungi sau planuri detaliate.
>
> **Unde se adaugă:** Plasați blocul `compaction` în interiorul `agents.defaults` din fișierul `openclaw.json` (de obicei la `~/.openclaw/openclaw.json`):
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
> Restul configurației voastre (gateway, canale, modele etc.) rămâne neschimbat, este necesar să adăugați doar cheia `compaction`.

### (Recomandat) Activați sandboxing-ul Docker

OpenClaw poate direcționa toate operațiunile agentului asupra fișierelor și codului printr-un container Docker izolat, în loc să le execute direct pe sistemul gazdă. Acest lucru limitează raza de acțiune a oricărei acțiuni neintenționate la sandbox, lăsând sistemul de fișiere și rețeaua gazdei neatinse.

Construiți imaginea sandbox o singură dată (Docker trebuie să fie instalat):

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

Rulați această comandă pentru a adăuga cheia `sandbox` în interiorul blocului existent `agents.defaults` din `~/.openclaw/openclaw.json`:

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

Containerele sandbox **nu au acces la rețea** în mod implicit. Consultați [referința despre sandboxing](https://docs.openclaw.ai/gateway/sandboxing) pentru montări de volume și suprascrieri de rețea.

> #### Depanare: Permisiune Docker refuzată
> 
> Dacă primiți mesajul „permission denied” la rularea comenzilor Docker:
> 
> **Pasul 1: Adăugați utilizatorul vostru în grupul docker**
> 
> ```bash
> sudo groupadd docker                    # Creați grupul dacă este necesar
> sudo usermod -aG docker $USER           # Adăugați-vă în grup
> newgrp docker                           # Activați modificarea
> docker run hello-world                  # Testați
> ```
> 
> **Pasul 2: Dacă eroarea persistă, aplicați soluția permanentă**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Apoi **reporniți** sistemul.
> 
> **Soluție temporară rapidă** (se resetează după repornire):
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

### Porniți OpenClaw Gateway

Gateway-ul este procesul OpenClaw care gestionează bucla agentului și servește tabloul de bord (dashboard):

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

Pentru a deschide tabloul de bord, rulați această comandă într-un al doilea terminal, în timp ce gateway-ul rulează în continuare:

```bash
openclaw dashboard
```

Deoarece gateway-ul se leagă la loopback, tabloul de bord se autentifică automat atunci când este deschis de pe același sistem, fără a fi necesară introducerea unui token sau aprobarea dispozitivului pentru accesul local. Ar trebui să vedeți tabloul de bord OpenClaw cu modelul Lemonade afișat ca backend activ.

> Dacă ați activat sandboxing-ul, îl puteți verifica cerându-i agentului să `run hostname` din tabloul de bord. Dacă vedeți un ID scurt de container în loc de numele gazdei sistemului vostru, sandbox-ul funcționează.

**Felicitări, ați construit de la zero un stack complet local de agent AI.**

> **Aveți nevoie de token-ul gateway-ului?** Rulați `openclaw dashboard --no-open` pentru a afișa URL-ul tabloului de bord cu token-ul inclus (comanda încearcă, de asemenea, să îl copieze în clipboard). Alternativ, token-ul se află la `gateway.auth.token` în `~/.openclaw/openclaw.json`.
>
> **Aprobarea unui dispozitiv la distanță:** Când deschideți tabloul de bord de pe un al doilea sistem sau telefon, browserul afișează un ID de cerere. Pe sistemul pe care rulează gateway-ul, rulați:
> ```bash
> openclaw devices approve <requestId>
> ```
> Acest lucru este necesar doar pentru dispozitive la distanță sau secundare, accesul prin loopback de pe același sistem se autentifică automat.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Opțional: Conectați un canal de comunicare

Odată ce gateway-ul rulează, puteți accesa agentul vostru local de pe orice dispozitiv. Alegeți opțiunea care se potrivește configurației voastre. OpenClaw acceptă [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) și alte canale, consultați lista completă la [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Opțiunea A: Discord

Discord necesită un server pe care **aveți acces de administrator** pentru a adăuga un bot. Dacă folosiți servere partajate, dar nu dețineți unul, utilizați în schimb Opțiunea B (Telegram).
#### Creați un cont și un server Discord

Dacă nu aveți un cont Discord, înscrieți-vă la [discord.com](https://discord.com). De asemenea, aveți nevoie de un server pe care sunteți administrator; creați unul apăsând pe pictograma **+** din bara laterală Discord și selectând **Create My Own**. Un server privat este suficient.

#### Creați o aplicație și un bot Discord

1. Accesați [Discord Developer Portal](https://discord.com/developers/applications) și apăsați **New Application**. Dați-i un nume (de exemplu, „openclaw-bot”).
2. În bara laterală, apăsați **Bot**. Setați un nume de utilizator pentru bot.
3. Tot pe pagina Bot, derulați până la **Privileged Gateway Intents** și activați:
   - **Message Content Intent** (obligatoriu)
   - **Server Members Intent** (recomandat)
4. Derulați înapoi în sus și apăsați **Reset Token** pentru a genera tokenul botului. Copiați-l.

#### Adăugați botul pe serverul dumneavoastră

1. În bara laterală, apăsați **OAuth2/ URL Generator**.
2. Sub **Scopes**, activați `bot` și `applications.commands`.
3. Sub **Bot Permissions**, activați: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Copiați URL-ul generat, inserați-l în browser, selectați serverul și confirmați. Botul ar trebui să apară acum în lista de membri a serverului dumneavoastră.

#### Adunați ID-urile necesare

Activați Modul Dezvoltator în Discord (**User Settings/ Advanced/ Developer Mode**), apoi:
- Click dreapta pe pictograma serverului dumneavoastră: **Copy Server ID**
- Click dreapta pe propriul avatar: **Copy User ID**

#### Permiteți mesajele directe de la membrii serverului

Click dreapta pe pictograma serverului/ **Privacy Settings**/ activați **Direct Messages**. Acest lucru permite botului să vă trimită mesaje directe, ceea ce este necesar pentru etapa de asociere.

#### Configurați OpenClaw pentru Discord

Stocați tokenul botului ca variabilă de mediu, apoi creați un singur fișier patch care activează Discord, face referire la token și include serverul dumneavoastră în lista de acces. Înlocuiți `<server_id>` și `<user_id>` cu ID-urile adunate mai sus.

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

> **Nu vă bazați pe faptul că îi cereți agentului să configureze acest lucru.** Când sandboxing-ul este activat, agentul nu poate scrie în `~/.openclaw/openclaw.json` din interiorul sandbox-ului; folosiți în schimb comenzile CLI de mai sus pe mașina gazdă.

Reporniți gateway-ul astfel încât acesta să preia noua configurație a canalului:

```bash
openclaw gateway run --bind loopback --port 18789
```

Ar trebui să vedeți `logged in to discord as <bot-name>` în ieșirea gateway-ului în câteva secunde.

#### Asociați-vă contul Discord

Trimiteți un mesaj direct botului pe Discord. Acesta va răspunde cu un scurt cod de asociere.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Aprobați-l pe mașina pe care rulează OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Codurile de asociere expiră după o oră.

Acum puteți discuta cu agentul dumneavoastră direct din Discord și puteți delega sarcini către hardware-ul local.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Opțiunea B: Telegram

Telegram este mai simplu decât Discord pentru majoritatea utilizatorilor, nu necesită server și nici acces de administrator.

#### Creați un bot Telegram

1. Deschideți Telegram și trimiteți un mesaj către **@BotFather**.
2. Trimiteți `/newbot` și urmați instrucțiunile. Salvați tokenul botului pe care vi-l oferă.

#### Configurați OpenClaw pentru Telegram

Stocați tokenul ca variabilă de mediu:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Adăugați configurația canalului în `~/.openclaw/openclaw.json` (sau aplicați-o prin patch din dashboard):

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

Reporniți gateway-ul, apoi trimiteți botului dumneavoastră orice mesaj pe Telegram. Aprobați asocierea:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Codurile de asociere expiră după o oră. Acum puteți discuta cu agentul dumneavoastră prin mesaje directe pe Telegram.

---

## Pașii următori

Acum că agentul dumneavoastră poate primi comenzi de pe telefon și poate acționa pe mașina dumneavoastră locală, iată trei direcții demne de explorat:

1. **Sumarizator al pieței bursiere**: Programați OpenClaw să preia date de la API-uri financiare la un interval fix, să sumarizeze mișcările zilei cu modelul dumneavoastră local și să trimită un rezumat pe telefon în fiecare dimineață prin canalul ales.

2. **Monitor de fine-tuning**: Porniți un job de antrenare de la distanță prin Telegram sau Discord, apoi puneți agentul să urmărească jurnalul de antrenare și să raporteze periodic valorile de loss, utilizarea GPU-ului și utilizarea discului înapoi pe telefonul dumneavoastră. Dacă rularea se blochează sau VRAM-ul crește brusc, aflați imediat, fără să fie nevoie să fiți la mașină.

3. **IOT cu un VLM local**: Îndreptați o cameră spre ușa de la intrare, rulați un model de viziune pe Lemonade și puneți OpenClaw să analizeze cadrele la cerere sau la declanșarea unui trigger. Întrebați „au sosit colete azi?” de pe telefon și primiți un răspuns direct de la propriul hardware.