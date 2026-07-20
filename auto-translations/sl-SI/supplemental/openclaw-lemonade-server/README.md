<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Zaganjanje OpenClaw z Lemonade Server kot zaledjem

## Pregled

[**OpenClaw**](https://openclaw.ai/) je avtonomen agent umetne inteligence, ki lahko piše in izvaja kodo, upravlja z datotekami ter opravlja zapletena večstopenjska opravila v vašem imenu. Za razliko od klepetalnega pomočnika, ki zgolj odgovarja na vprašanja, OpenClaw na vašem sistemu dejansko izvaja dejanja, zato potrebuje hitro in zmogljivo zaledje umetne inteligence, ki lahko sledi zahtevni zanki agenta.

[**Lemonade Server**](https://lemonade-server.ai/) je prav to zaledje. Gre za odprtokodni lokalni strežnik za sklepanje, ki modele GenAI izvaja neposredno na vaši strojni opremi in jih izpostavlja prek standardnega API-ja OpenAI, uveljavljenega v panogi.

Skupaj tvorita popolnoma lokalen sklad agentov umetne inteligence: Lemonade skrbi za sklepanje modela, OpenClaw pa zagotavlja zanko agenta, ki izhode modela pretvori v dejanska dejanja.

> **Preden nadaljujete:** OpenClaw je zelo avtonomen agent umetne inteligence. Dodelitev dostopa do vašega sistema kateremu koli agentu umetne inteligence lahko privede do nepredvidljivih ali nenamernih posledic. Nadaljujte le, če razumete tveganja in vam ustreza, da v vašem imenu deluje avtonomna programska oprema.

---

## Kaj se boste naučili

Ob koncu tega vodnika boste zmogli:

- Spoznati **Lemonade Server**
- **Namestiti OpenClaw** in ga **usmeriti na Lemonade Server** kot svoje zaledje umetne inteligence.
- **Zagnati prehod (gateway) OpenClaw** in potrditi, da je vaš agent pripravljen za delo.
- **Povezati komunikacijski kanal** (Discord ali Telegram), da se boste lahko z agentom pogovarjali iz katere koli naprave.

---

## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev predpogojev programske opreme

<!-- @os:linux -->
- Računalnik z operacijskim sistemom **Ubuntu 24.04+** ali združljivo distribucijo Linuxa, ki temelji na Debianu, z ukazom `apt-get`
- Vsaj **12 GB pomnilnika RAM** (za večje modele priporočamo 64 GB ali več)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (izbirno, za peskovnik OpenClaw)

- **Približno 10–30 GB prostega prostora na disku** za uteži modela
<!-- @os:end -->
<!-- @os:windows -->
- Računalnik z operacijskim sistemom **Windows 10/11**
- Vsaj **12 GB pomnilnika RAM** (za večje modele priporočamo 64 GB ali več)
- **Približno 10–30 GB prostega prostora na disku** za uteži modela
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (izbirno, za peskovnik OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Prenesite in naložite priporočeni model

Priporočeni model za ta vodnik je **Qwen3.6-35B-A3B-GGUF** podjetja Unsloth, zmogljiv model MoE z oknom konteksta 263.000 žetonov, ki je zelo primeren za obremenitve agentov. Ta model uporablja kvantizacijo UD-Q4_K_XL. Prenesite ga zdaj:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Nato ga naložite z velikim oknom konteksta in to nastavitev shranite za prihodnje zagone:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Model ima privzeto dolžino konteksta 262.144 žetonov. Če naletite na napake zaradi pomanjkanja pomnilnika (OOM), razmislite o zmanjšanju okna konteksta. Ker pa Qwen3.6 za zapletena opravila izkorišča razširjen kontekst, priporočamo ohranitev dolžine konteksta vsaj 128 tisoč žetonov, da se ohranijo zmožnosti razmišljanja.

> **Nasvet: onemogočite razmišljanje za hitrejše odzive agenta:** Qwen3.6-35B-A3B privzeto deluje v načinu razmišljanja, kar pred vsakim odzivom doda zakasnitev. Pri zankah agenta se ta dodatni čas hitro nabira. Repozitorij [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) ponuja pripravljeno konfiguracijo, ki onemogoči razmišljanje. Če jo želite uporabiti, prenesite datoteko in jo uvozite:
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

## Namestitev sistema WSL

OpenClaw poganjamo znotraj WSL (priporočeno) in ga povežemo z Lemonade, ki se izvaja izvorno v operacijskem sistemu Windows. To vam zagotovi okolje lupine Linux za OpenClaw, hkrati pa ohrani pospeševanje GPU za Lemonade na strani Windows.

### Namestite WSL in Ubuntu

Odprite PowerShell kot skrbnik in namestite jedro WSL:

```powershell
wsl --install --no-distribution
```

Nato namestite Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Omogočite systemd v WSL

Zaženite to znotraj terminala Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Ponovno zaženite WSL:

```powershell
wsl --shutdown
wsl
```

### Premostite Lemonade iz Windows v WSL

WSL2 se izvaja v navideznem omrežju. Lemonade v operacijskem sistemu Windows se veže na `127.0.0.1`, do katerega WSL ne more neposredno dostopati. Posredniški vrata (port proxy) v operacijskem sistemu Windows preusmerijo promet z naslova IP prehoda WSL na lokalni gostitelj (localhost) v Windows.

**Poiščite svoj naslov IP prehoda WSL** (zaženite znotraj WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Dodajte posredniška vrata** (zaženite v PowerShellu kot skrbnik in zamenjajte `<WSL-Gateway-IP>` s svojim naslovom IP prehoda WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Dodajte pravilo požarnega zidu** (isti dvignjeni PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Preverite iz WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Če ste v prejšnjem koraku že naložili model Qwen3.6-35B-A3B-GGUF, bi morali videti izhod JSON, podoben temu:

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

> Pravilo `netsh portproxy` preživi ponovni zagon, vendar se naslov IP prehoda WSL lahko spremeni po ukazu `wsl --shutdown`. Če Lemonade po ponovnem zagonu ni več dosegljiv iz WSL, pridobite posodobljen naslov IP prehoda in z njim posodobite posredniška vrata.

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

## Namestite in konfigurirajte OpenClaw

### Namestite OpenClaw
<!-- @os:windows -->
> Ukaze v tem razdelku zaženite znotraj svojega **terminala WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Zastavica `--no-onboard` preskoči interaktivnega čarovnika za nastavitev; zaledje modela boste v naslednjem koraku konfigurirali ročno, kar vam omogoča natančen nadzor nad tem, kateri model in strežnik se uporabljata.

Odprite nov terminal in potrdite namestitev:

```bash
openclaw --version
```

> **Nasvet:** Če po namestitvi vidite sporočilo `command not found`, dodajte globalno binarno mapo npm v svojo spremenljivko PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Če želite to spremembo narediti trajno, zgornjo vrstico dodajte v svojo datoteko `~/.bashrc` ali `~/.zshrc`.

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
### Konfiguriranje OpenClaw za uporabo Lemonade

Zaženite neinteraktivni onboarding OpenClaw.
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

Ta ukaz zapiše konfiguracijo OpenClaw v `~/.openclaw/openclaw.json`.

> **Velikost kontekstnega okna OpenClaw:** Kompaktiranje pri OpenClaw se sproži, ko `contextTokens > contextWindow − reserveTokens`. Privzeta vrednost `reserveTokensFloor` je 20.000 žetonov, kar je spodnja meja, ki prepiše `reserveTokens`, kadar je ta nižji, zato bo vsak kontekst modela pod približno 37k sprožil neskončno zanko kompaktiranja. Nastavite nizko rezervo in enkrat v konfiguraciji onemogočite spodnjo mejo, nastavitev pa velja za vsak model, brez potrebe po prilagajanju za posamezen model:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` je *spodnja meja* (minimalna zaščita), ne rezerva sama, zato nastavitev samo spodnje meje ne bo imela učinka. `reserveTokensFloor: 0` onemogoči zaščito, tako da se sprejme nižja vrednost `reserveTokens`.
>
> **Kdaj to uporabiti:** To konfiguracijo uporabite, če je dejansko kontekstno okno vašega modela manjše od približno 37k, bodisi ker je model majhen (npr. 8k, 16k, 32k) bodisi ker ste namerno omejili kontekst na nižjo vrednost (npr. nalagate model s 128k, vendar v Lemonade nastavite kontekst na 16k). Brez tega bo OpenClaw ob zagonu vstopil v neskončno zanko kompaktiranja.
>
> **Modeli z velikim kontekstom pri polnem kontekstu:** To lahko preprosto preskočite. Privzete nastavitve delujejo dobro, kompaktiranje se sproži precej pred zapolnitvijo okna, model pa ima dovolj prostora za generiranje dolgih odgovorov. Če to vseeno uporabite, upoštevajte, da `reserveTokens: 4096` omeji dolžino odgovora na približno 4k žetonov, kar lahko prekine generiranje dolgih datotek ali podrobnih načrtov.
>
> **Kam to dodati:** Blok `compaction` postavite znotraj `agents.defaults` v vaši datoteki `openclaw.json` (običajno na `~/.openclaw/openclaw.json`):
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
> Preostanek konfiguracije (gateway, channels, models itd.) ostane nespremenjen, dodati je treba le ključ `compaction`.

### (Priporočeno) Omogočite peskovnik Docker

OpenClaw lahko vse datotečne in kodne operacije agenta usmeri skozi izoliran vsebnik Docker, namesto da jih izvaja neposredno na vašem gostitelju. To omeji doseg vsakega nenamernega dejanja na peskovnik, tako da datotečni sistem in omrežje gostitelja ostaneta nedotaknjena.

Zgradite sliko peskovnika enkrat (Docker mora biti nameščen):

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

Zaženite to, da dodate ključ `sandbox` znotraj obstoječega bloka `agents.defaults` v `~/.openclaw/openclaw.json`:

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

Vsebniki peskovnika privzeto **nimajo dostopa do omrežja**. Za priklope enot (bind mounts) in preglase omrežja glejte [referenco za peskovnik](https://docs.openclaw.ai/gateway/sandboxing).

> #### Odpravljanje težav: Docker Permission Denied
> 
> Če pri izvajanju ukazov Docker dobite sporočilo "permission denied":
> 
> **1. korak: Dodajte svojega uporabnika v skupino docker**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **2. korak: Če napaka vztraja, uveljavite trajno rešitev**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Nato **znova zaženite** sistem.
> 
> **Hitra začasna rešitev** (ponastavi se ob ponovnem zagonu):
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

### Zagon vmesnika OpenClaw Gateway

Gateway je proces OpenClaw, ki upravlja zanko agenta in strežuje nadzorno ploščo:

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

Za odprtje nadzorne plošče to zaženite v drugem terminalu, medtem ko gateway še vedno teče:

```bash
openclaw dashboard
```

Ker se gateway veže na povratno zanko (loopback), se nadzorna plošča ob odprtju z iste naprave samodejno preveri, zato za lokalni dostop ni potrebno vnašati žetona ali odobravati naprave. Prikazati bi se morala nadzorna plošča OpenClaw z vašim modelom Lemonade, navedenim kot aktivnim zaledjem.

> Če ste omogočili peskovnik, lahko to preverite tako, da agenta iz nadzorne plošče prosite, naj `run hostname`. Če se prikaže kratek ID vsebnika namesto imena gostitelja vašega računalnika, peskovnik deluje.

**Čestitamo, zgradili ste povsem lokalen sklad umetne inteligence za agente, popolnoma od začetka.**

> **Potrebujete žeton za gateway?** Zaženite `openclaw dashboard --no-open`, da izpišete URL nadzorne plošče z vgrajenim žetonom (poskusi ga tudi kopirati v odložišče). Alternativno je žeton na voljo pod `gateway.auth.token` v `~/.openclaw/openclaw.json`.
>
> **Odobritev oddaljene naprave:** Ko nadzorno ploščo odprete z druge naprave ali telefona, brskalnik prikaže ID zahteve. Nazaj na napravi, kjer teče gateway, zaženite:
> ```bash
> openclaw devices approve <requestId>
> ```
> To je potrebno le za oddaljene ali sekundarne naprave, dostop preko povratne zanke z iste naprave se samodejno preveri.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Neobvezno: Povezava komunikacijskega kanala

Ko gateway teče, lahko do svojega lokalnega agenta dostopate iz katere koli naprave. Izberite možnost, ki ustreza vaši nastavitvi. OpenClaw podpira [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) in druge kanale, celoten seznam si oglejte na [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Možnost A: Discord

Discord zahteva strežnik, na katerem imate **skrbniški dostop**, da lahko dodate bota. Če si strežnike delite, vendar niste njihov lastnik, namesto tega uporabite možnost B (Telegram).
#### Ustvarite Discord račun in strežnik

Če nimate Discord računa, se prijavite na [discord.com](https://discord.com). Potrebujete tudi strežnik, kjer ste skrbnik – ustvarite ga s klikom na ikono **+** v Discord stranski vrstici in izbiro **Create My Own**. Zasebni strežnik je povsem primeren.

#### Ustvarite Discord aplikacijo in bota

1. Pojdite na [Discord Developer Portal](https://discord.com/developers/applications) in kliknite **New Application**. Poimenujte jo (npr. »openclaw-bot«).
2. V stranski vrstici kliknite **Bot**. Nastavite uporabniško ime za bota.
3. Še vedno na strani Bot se pomaknite do **Privileged Gateway Intents** in omogočite:
   - **Message Content Intent** (obvezno)
   - **Server Members Intent** (priporočeno)
4. Pomaknite se nazaj gor in kliknite **Reset Token**, da ustvarite žeton za bota. Kopirajte ga.

#### Dodajte bota v svoj strežnik

1. V stranski vrstici kliknite **OAuth2/ URL Generator**.
2. Pod **Scopes** omogočite `bot` in `applications.commands`.
3. Pod **Bot Permissions** omogočite: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopirajte ustvarjeni URL, ga prilepite v brskalnik, izberite svoj strežnik in potrdite. Bot bi se moral zdaj pojaviti na seznamu članov vašega strežnika.

#### Zberite svoje ID-je

Omogočite Developer Mode v Discordu (**User Settings/ Advanced/ Developer Mode**), nato:
- Z desnim klikom na ikono strežnika: **Copy Server ID**
- Z desnim klikom na svoj avatar: **Copy User ID**

#### Dovolite zasebna sporočila od članov strežnika

Z desnim klikom na ikono strežnika/ **Privacy Settings**/ vklopite **Direct Messages**. To omogoči botu, da vam pošlje zasebno sporočilo, kar je potrebno za korak seznanjanja.

#### Konfigurirajte OpenClaw za Discord

Shranite žeton bota kot spremenljivko okolja, nato ustvarite eno samo patch datoteko, ki omogoči Discord, sklicuje se na žeton in na dovoljen seznam doda vaš strežnik. Zamenjajte `<server_id>` in `<user_id>` z ID-ji, zbranimi zgoraj.

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

> **Ne zanašajte se na to, da boste agentu naročili, naj to konfigurira.** Ko je sandboxing omogočen, agent iz peskovnika ne more pisati v `~/.openclaw/openclaw.json`; namesto tega uporabite zgornje ukaze CLI na gostitelju.

Znova zaženite gateway, da prevzame novo konfiguracijo kanala:

```bash
openclaw gateway run --bind loopback --port 18789
```

V nekaj sekundah bi morali v izpisu gatewaya videti `logged in to discord as <bot-name>`.

#### Seznanite svoj Discord račun

Pošljite botu zasebno sporočilo v Discordu. Odgovoril bo s kratko kodo za seznanjanje.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Potrdite jo na napravi, kjer teče OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Kode za seznanjanje potečejo po eni uri.

Zdaj se lahko s svojim agentom pogovarjate neposredno prek Discorda in naloge prepustite svoji lokalni strojni opremi.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Možnost B: Telegram

Telegram je za večino uporabnikov preprostejši kot Discord, saj ne zahteva strežnika ali skrbniškega dostopa.

#### Ustvarite Telegram bota

1. Odprite Telegram in pošljite sporočilo **@BotFather**.
2. Pošljite `/newbot` in sledite navodilom. Shranite žeton bota, ki ga prejmete.

#### Konfigurirajte OpenClaw za Telegram

Shranite žeton kot spremenljivko okolja:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Dodajte konfiguracijo kanala v `~/.openclaw/openclaw.json` (ali jo popravite prek nadzorne plošče):

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

Znova zaženite gateway, nato botu pošljite katerokoli sporočilo v Telegramu. Potrdite seznanjanje:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Kode za seznanjanje potečejo po eni uri. Zdaj se lahko s svojim agentom pogovarjate prek zasebnih sporočil na Telegramu.

---

## Naslednji koraki

Zdaj, ko lahko vaš agent prejema ukaze z vašega telefona in deluje na vašem lokalnem računalniku, so tu tri smeri, ki jih velja raziskati:

1. **Povzemalnik borznega trga**: Nastavite OpenClaw, da v določenih časovnih intervalih pridobiva podatke iz finančnih API-jev, s svojim lokalnim modelom povzame dnevna gibanja in vsako jutro pošlje povzetek na vaš telefon prek izbranega kanala.

2. **Nadzor fine nastavitve (fine-tuning)**: Sprožite učno opravilo na daljavo prek Telegrama ali Discorda, nato pa naj agent spremlja dnevnik učenja in vam na telefon periodično sporoča vrednosti izgube (loss), izkoriščenost GPE-ja in porabo diska. Če se izvajanje zatakne ali VRAM nenadoma naraste, boste to takoj izvedeli, ne da bi morali biti pri računalniku.

3. **IoT z lokalnim VLM**: Usmerite kamero na vhodna vrata, zaženite vizualni model na Lemonade in naj OpenClaw analizira slike na zahtevo ali ob sprožilcu. Vprašajte »Ali je danes prispel kakšen paket?« s svojega telefona in dobite neposreden odgovor iz svoje lastne strojne opreme.