<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinöversättning.** Den här sidan har automatiskt översatts från engelska och har inte granskats av en människa. Den kan innehålla fel, och vissa instruktioner, kommandon, nedladdningar, produkttillgänglighet eller annat innehåll kan variera beroende på språk eller region. Vid eventuella motsägelser eller avvikelser är det den ursprungliga engelska versionen av playbook som gäller och har företräde.
<!-- auto-translated-disclaimer:end -->

# Kör OpenClaw med Lemonade Server som backend

## Översikt

[**OpenClaw**](https://openclaw.ai/) är en autonom AI-agent som kan skriva och köra kod, hantera filer och arbeta igenom komplexa flerstegsuppgifter åt dig. Till skillnad från en chattassistent som bara svarar på frågor utför OpenClaw verkliga åtgärder på ditt system, vilket innebär att den behöver en snabb, kapabel AI-backend som kan hänga med i en krävande agentloop.

[**Lemonade Server**](https://lemonade-server.ai/) är den backenden. Det är en öppen källkods lokal inferensserver som kör GenAI-modeller direkt på din hårdvara och exponerar dem via det branschstandardiserade OpenAI-API:et.

Tillsammans bildar de en helt lokal AI-agentstack: Lemonade hanterar modellinferens, och OpenClaw tillhandahåller agentloopen som omvandlar modellresultat till verkliga åtgärder.

> **Innan du fortsätter:** OpenClaw är en mycket autonom AI-agent. Att ge en AI-agent åtkomst till ditt system kan leda till oförutsägbara eller oavsiktliga resultat. Fortsätt endast om du förstår riskerna och är bekväm med att autonom programvara agerar å dina vägnar.

---

## Vad du kommer att lära dig

I slutet av den här handledningen kommer du att kunna:

- Lära dig om **Lemonade Server**
- **Installera OpenClaw** och **ställa in den att använda Lemonade Server** som sin AI-backend.
- **Starta OpenClaw-gatewayen** och bekräfta att din agent är redo att arbeta.
- **Ansluta en kommunikationskanal** (Discord eller Telegram) så att du kan chatta med din agent från vilken enhet som helst.

---

<!-- @device:halo_box,halo,stx,krk -->
## Ställa in minneskonfigurationen

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Kontrollera om det finns programvaruuppdateringar

<!-- @require:software-update -->
<!-- @device:end -->

## Installera nödvändig programvara

<!-- @os:linux -->
- En dator med **Ubuntu 24.04+** eller en kompatibel Debian-baserad Linux-distribution med `apt-get`
- Minst **12 GB RAM** (64 GB+ rekommenderas för större modeller)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (Valfritt, för sandboxning av OpenClaw)
- **~10–30 GB ledigt diskutrymme** för modellvikter
<!-- @os:end -->

<!-- @os:windows -->
- En dator med **Windows 10/11**
- Minst **12 GB RAM** (64 GB+ rekommenderas för större modeller)
- **~10–30 GB ledigt diskutrymme** för modellvikter
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (Valfritt, för sandboxning av OpenClaw)
<!-- @os:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:nodejs,openclaw,lemonade-models-qwen3-35b-a3b -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Hämta och ladda den rekommenderade modellen

Den rekommenderade modellen för den här handledningen är **Qwen3.6-35B-A3B-GGUF** från Unsloth, en kraftfull MoE-modell med ett kontextfönster på 263k token som passar bra för agentarbetsbelastningar. Den här modellen använder UD-Q4_K_XL-kvantisering. Hämta den nu:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Ladda den sedan med ett stort kontextfönster och spara den inställningen för framtida körningar:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Modellen har som standard en kontextlängd på 262 144 token. Om du stöter på fel med slut på minne (OOM) kan du överväga att minska kontextfönstret. Eftersom Qwen3.6 utnyttjar utökad kontext för komplexa uppgifter rekommenderar vi dock att behålla en kontextlängd på minst 128K token för att bevara tankeförmågan.

> **Tips: Inaktivera tänkande för snabbare agentsvar:** Qwen3.6-35B-A3B körs som standard i tankeläge, vilket tillför fördröjning innan varje svar. För agentloopar ackumuleras denna overhead snabbt. Förrådet [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) tillhandahåller en färdig konfiguration som inaktiverar tänkande. För att använda den, hämta filen och importera den:
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

## Konfigurera WSL

Vi kör OpenClaw inuti WSL (Rekommenderas) och ansluter den till Lemonade som körs nativt på Windows. Detta ger dig en Linux-skalmiljö för OpenClaw samtidigt som Lemonades GPU-acceleration behålls på Windows-sidan.

### Installera WSL och Ubuntu

Öppna PowerShell som administratör och installera WSL-kärnan:

```powershell
wsl --install --no-distribution
```

Installera sedan Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Aktivera systemd i WSL

Kör detta inuti Ubuntu-terminalen:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Avsluta WSL och starta om det:

```powershell
exit
wsl --shutdown
wsl
```

### Brygga Lemonade från Windows till WSL

WSL2 körs i ett virtuellt nätverk. Lemonade på Windows binder till `127.0.0.1`, vilket WSL inte kan nå direkt. En Windows-portproxy vidarebefordrar trafik från WSL-gatewayens IP till Windows localhost.

**Hitta din WSL-gateway-IP** (kör inuti WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Lägg till portproxyn** (kör i PowerShell som administratör, ersätt `<WSL-Gateway-IP>` med din WSL-gateway-IP):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Obs: Om du stöter på felet `netsh: command not found`, prova att använda det explicita körbara namnet istället - `netsh.exe`

**Lägg till en brandväggsregel** (samma upphöjda PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Verifiera från WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Om du redan har laddat Qwen3.6-35B-A3B-GGUF-modellen i föregående steg bör du se JSON-utdata som detta:

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

#### Hålla bron igång efter en omstart

Regeln `netsh portproxy` överlever omstarter, men WSL-gatewayns IP kan ändras efter `wsl --shutdown` eller en omstart. När det händer pekar proxyn fortfarande på den gamla IP-adressen och Lemonade blir oåtkomlig från WSL. Om det inträffar, använd ett av alternativen nedan.

**Alternativ 1 (rekommenderas) — Reparera bron automatiskt.** För att slippa göra detta manuellt varje gång, använd en schemalagd aktivitet som kontrollerar bron vid varje uppstart och inloggning och bygger om den endast när gateway-IP:n har ändrats. Se [guiden för automatisk reparation av Lemonade WSL-bron](assets/RepairLemonadeWslBridge.md).

**Alternativ 2 — Reparera bron manuellt.** Hämta först den aktuella WSL-gateway-IP:n genom att köra detta inuti WSL:

```bash
ip route show default | awk '{print $3}' | head -1
```

Kopiera detta värde; du kommer att använda det i stället för `<new-WSL-Gateway-IP>` nedan.

Lista sedan de befintliga reglerna i en **upphöjd PowerShell** (kör som administratör), ta bort endast den inaktuella Lemonade-regeln och lägg till en ny med den aktuella IP-adressen:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

I utdata från `show all` är den inaktuella Lemonade-regeln posten vars anslutningsadress är `127.0.0.1` på port `13305`; dess lyssningsadress är din `<old-WSL-Gateway-IP>`. Om du tar bort via den adressen tas endast denna regel bort och eventuella andra port-proxy-regler på din maskin lämnas orörda.

Brandväggsregeln du lade till under installationen är bunden till port `13305` (inte IP-adressen), så den fortsätter att fungera och behöver inte återskapas.

> **Rekommendation:** För att undvika gateway-problem rekommenderar vi starkt följande skalkonfiguration:
> - **Windows-kommandon** bör köras i **PowerShell**
> - **WSL-distrokommandon** bör köras i en **Kommandotolk** (kör som **Administratör**)

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

## Installera och konfigurera OpenClaw

### Installera OpenClaw
<!-- @os:windows -->
> Kör kommandona i detta avsnitt inuti din **WSL-terminal**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Flaggan `--no-onboard` hoppar över den interaktiva installationsguiden, du kommer att konfigurera modellbackenden manuellt i nästa steg, vilket ger dig exakt kontroll över vilken modell och server som används.

Öppna en ny terminal och bekräfta installationen:

```bash
openclaw --version
```

> **Tips:** Om du ser `command not found` efter installationen, lägg till npm:s globala bin-katalog i din PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> För att göra detta permanent, lägg till raden ovan i din `~/.bashrc`- eller `~/.zshrc`-fil.

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


### Konfigurera OpenClaw för att använda Lemonade

Kör OpenClaws icke-interaktiva introduktion.
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

Detta kommando skriver OpenClaws konfiguration till `~/.openclaw/openclaw.json`.

> **OpenClaw-kontextfönstrets storlek:** OpenClaws komprimering (compaction) utlöses när `contextTokens > contextWindow − reserveTokens`. Standardvärdet för `reserveTokensFloor` är 20 000 token, ett golv som åsidosätter `reserveTokens` när det är lägre, så varje modellkontext under cirka 37k kommer att utlösa en oändlig komprimeringsloop. Ange en låg reserv och inaktivera golvet en gång i din konfiguration så gäller det för varje modell, ingen modellspecifik justering behövs:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` är ett *golv* (minimiskydd), inte själva reserven, att enbart ange golvet har ingen effekt. `reserveTokensFloor: 0` inaktiverar skyddet så att den lägre `reserveTokens` accepteras.
>
> **När du ska tillämpa detta:** Använd denna konfiguration om din modells effektiva kontextfönster är under cirka 37k, antingen för att modellen är liten (t.ex. 8k, 16k, 32k) eller för att du medvetet har begränsat den till ett lägre värde (t.ex. laddat en 128k-modell men ställt in kontexten till 16k i Lemonade). Utan detta går OpenClaw in i en oändlig komprimeringsloop vid uppstart.
>
> **Modeller med stort kontextfönster vid full kontext:** Du kan hoppa över detta helt. Standardvärdena fungerar bra, komprimering kommer att starta en bra bit innan fönstret fylls och modellen har gott om utrymme att generera långa svar. Om du ändå tillämpar det, var medveten om att `reserveTokens: 4096` begränsar svarslängden till cirka 4k token, vilket kan klippa av lång filgenerering eller detaljerade planer.
>
> **Var du ska lägga till detta:** Placera `compaction`-blocket inuti `agents.defaults` i din `openclaw.json` (vanligtvis på `~/.openclaw/openclaw.json`):
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
> Resten av din konfiguration (gateway, kanaler, modeller, etc.) förblir oförändrad, endast nyckeln `compaction` behöver läggas till.
### (Rekommenderas) Aktivera Docker-sandlådning

OpenClaw kan dirigera alla agentens fil- och kodåtgärder genom en isolerad Docker-container istället för att köra dem direkt på din värd. Detta begränsar skadeverkan av eventuella oavsiktliga åtgärder till sandlådan, utan att påverka din värds filsystem och nätverk.

Bygg sandlåde-avbildningen en gång (Docker måste vara installerat):

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

Kör detta för att lägga till nyckeln `sandbox` inuti det befintliga blocket `agents.defaults` i `~/.openclaw/openclaw.json`:

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

Sandlådecontainrar har **ingen nätverksåtkomst** som standard. Se [referensen för sandlådning](https://docs.openclaw.ai/gateway/sandboxing) för bind-monteringar och nätverksöverstyrningar.

> #### Felsökning: Docker-behörighet nekad
> 
> Om du får "permission denied" när du kör Docker-kommandon:
> 
> **Steg 1: Lägg till din användare i docker-gruppen**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **Steg 2: Om felet kvarstår, tillämpa den permanenta lösningen**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Starta sedan **om** ditt system.
> 
> **Snabb tillfällig lösning** (återställs efter omstart):
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
## (Rekommenderas) OpenClaw-integration med Firecrawl-tjänster

[Firecrawl](https://docs.firecrawl.dev/introduction) tillhandahåller en självhostad webbcrawlnings- och innehållsextraheringstjänst som kan kringgå dessa utmaningar och frigöra OpenClaw-automatiseringens fulla potential.

I denna installation körs OpenClaw som en uppsättning Docker-containrar som hanteras med Podman. För att förenkla livscykelhanteringen och den automatiska starten registrerar vi Firecrawl som en användarbaserad `systemd`-tjänst som orkestrerar den underliggande Podman Compose-stacken. Detta gör att OpenClaw kan starta gatewayen, stoppa och verifiera Firecrawl-tjänsten med standardkommandon för `systemctl --user` istället för att interagera direkt med containrarna.

För att hålla det enkelt har vi delat upp hela processen i fyra steg:

---

### 1. Registrera systemtjänsten
Navigera till systemd:s användarkonfigurationskatalog:
```bash
cd ~/.config/systemd/user
```
Skapa och öppna en ny fil som heter `firecrawl.service`.
```bash
nano firecrawl.service
```
Kopiera och klistra in följande konfiguration:
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
Vid denna punkt har tjänsten definierats men ännu inte registrerats hos `systemd`.
Se till att filnamnet exakt matchar det du skapade ovan, kör sedan:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Om det lyckas bör du se följande utdata:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

`default.target.wants/` innehåller symboliska länkar till tjänster som är konfigurerade att starta automatiskt.

### 2. Konfigurera Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) är idealisk för dem som behöver full kontroll över sin skrapnings- och databehandlingsmiljö, men innebär i gengäld ytterligare underhålls- och konfigurationsarbete.

Börja med att klona repot:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Skapa en `.env`-fil i katalogen `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Distribuera OpenClaw med Podman Compose

Innan du går vidare, se till att du har hämtat den senaste OpenClaw Docker-avbildningen:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
När det är klart, ladda ner OpenClaw Compose-filen [openclaw-compose.yaml](assets/openclaw-compose.yaml) och placera den i rotkatalogen `/firecrawl`:

> Denna konvention krävs för att `systemd` ska kunna hitta och starta tjänsten korrekt, enligt specifikationen i `WorkingDirectory=${HOME}/firecrawl`.

> Du kan alltid utöka stacken genom att lägga till fler Firecrawl-tjänster efter behov. Den fullständiga listan över tillgängliga tjänster finns i den officiella filen [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Starta OpenClaw-tjänsten via Firecrawl

Innan du överlämnar kontrollen till `systemd`, validera att allt fungerar korrekt genom att köra stacken manuellt:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Om allt är korrekt konfigurerat bör du se OpenClaw-containern starta upp, och din kommandoradsutdata bör se ut ungefär så här:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

När du har verifierat detta, ta ner stacken igen innan du fortsätter:
```bash
podman compose -f openclaw-compose.yaml down
```
Innan du startar tjänsten måste du se till att rätt ägarskap och behörigheter är inställda på katalogen `firecrawl` och dess fil `.env`.
Detta är nödvändigt för att tjänsten ska kunna skriva dina autentiseringsuppgifter vid start.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Nu när allt är validerat, starta tjänsten via `systemd`:
```bash
systemctl --user start firecrawl.service
```
[OpenClaw-åtgärderna](https://docs.openclaw.ai/) är tillgängliga inifrån den interaktiva containern, och webb-instrumentpanelen är tillgänglig på samma värd och port på http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Hämta din `OPENCLAW_GATEWAY_TOKEN`

När tjänsten är igång kommer du att märka att en ny katalog `.openclaw` har skapats i din hemkatalog (~/.openclaw). Denna katalog är låst som standard, så du måste låsa upp den för att hämta din gateway-token.

1. Bevilja åtkomst till katalogen:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Läs din gateway-token:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Leta reda på värdet för `OPENCLAW_GATEWAY_TOKEN` i utdatan.

3. Öppna gateway-instrumentpanelen i din webbläsare på http://127.0.0.1:18789. Klistra in din token när du uppmanas att autentisera.

För att stoppa tjänsten, kör:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Starta OpenClaw-gatewayen

Gatewayen är den OpenClaw-process som hanterar agentloopen och tillhandahåller instrumentpanelen:

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

För att öppna instrumentpanelen, kör följande i en andra terminal medan gatewayen fortfarande körs:

```bash
openclaw dashboard
```

Eftersom gatewayen binder till loopback autentiseras instrumentpanelen automatiskt när den öppnas från samma maskin – ingen token behöver anges och ingen enhetsgodkännande krävs för lokal åtkomst. Du bör se OpenClaw-instrumentpanelen med din Lemonade-modell listad som den aktiva backend.

> Om du har aktiverat sandboxning kan du verifiera det genom att be agenten att `run hostname` från instrumentpanelen. Om du ser ett kort container-ID istället för din maskins värdnamn fungerar sandboxen.

**Grattis, du har byggt en helt lokal AI-agentstack från grunden.**

> **Behöver du gateway-token?** Kör `openclaw dashboard --no-open` för att skriva ut instrumentpanelens URL med token inbäddad (det försöker även kopiera den till ditt urklipp). Alternativt finns token under `gateway.auth.token` i `~/.openclaw/openclaw.json`.

**Åtkomst till instrumentpanelen från en annan enhet (via SSH-tunnel)**

Om OpenClaw körs på en fjärrmaskin kan du nå dess instrumentpanel från din lokala maskin genom en SSH-tunnel. Tunneln vidarebefordrar gateway-porten (`18789`) så att din lokala webbläsare kan kommunicera med den fjärrbelägna gatewayen via `127.0.0.1`.

1. Från din **lokala maskin**, anslut till fjärrmaskinen en gång och godkänn fingeravtrycksfrågan så att värden läggs till i dina kända värdar:

   ```bash
   ssh user@<host-ip>
   ```

2. Fortfarande på din **lokala maskin**, öppna SSH-tunneln:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Obs:** Efter att du har angett ditt lösenord visar terminalen ingen utdata och verkar hänga sig. Detta är förväntat: flaggan `-N` säger åt SSH att inte köra något fjärrkommando, så den håller bara tunneln öppen. Låt denna terminal fortsätta köra.

3. På din **lokala maskin**, öppna en webbläsare och gå till `http://127.0.0.1:18789`.

4. På **fjärrmaskinen**, skriv ut gateway-token och klistra in den i webbläsaren för att logga in:

   ```bash
   openclaw dashboard --no-open
   ```

   Detta skriver ut instrumentpanelens URL med token inbäddad; kopiera token för att logga in. (Token finns även lagrad under `gateway.auth.token` i `~/.openclaw/openclaw.json`.)

> **Godkänna en fjärrenhet:** När du öppnar instrumentpanelen från en annan maskin eller telefon kan webbläsaren visa ett förfråknings-ID. På **fjärrmaskinen**, lista väntande förfrågningar:
> ```bash
> openclaw devices list
> ```
> Godkänn sedan den matchande förfrågan:
> ```bash
> openclaw devices approve <requestId>
> ```
> Detta behövs endast för fjärr- eller sekundära enheter; loopback-åtkomst från samma maskin autentiseras automatiskt. Se dokumentationen för [Fjärråtkomst](https://docs.openclaw.ai/gateway/remote) för mer information.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Valfritt: Anslut en kommunikationskanal

När gatewayen väl körs kan du nå din lokala agent från vilken enhet som helst. Välj det alternativ som passar din konfiguration. OpenClaw stödjer [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram), och andra kanaler, se hela listan på [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Alternativ A: Discord

Discord kräver en server där **du har administratörsåtkomst** för att lägga till en bot. Om du delar servrar men inte äger någon, använd Alternativ B (Telegram) istället.

#### Skapa ett Discord-konto och en server

Om du inte har ett Discord-konto, registrera dig på [discord.com](https://discord.com). Du behöver också en server där du är administratör, skapa en genom att klicka på **+**-ikonen i Discords sidofält och välja **Create My Own**. En privat server fungerar bra.

#### Skapa en Discord-applikation och bot

1. Gå till [Discord Developer Portal](https://discord.com/developers/applications) och klicka på **New Application**. Ge den ett namn (t.ex. "openclaw-bot").
2. I sidofältet, klicka på **Bot**. Ange ett användarnamn för boten.
3. Fortfarande på Bot-sidan, bläddra ner till **Privileged Gateway Intents** och aktivera:
   - **Message Content Intent** (krävs)
   - **Server Members Intent** (rekommenderas)
4. Bläddra upp igen och klicka på **Reset Token** för att generera din bot-token. Kopiera den.

#### Lägg till boten i din server

1. I sidofältet, klicka på **OAuth2/ URL Generator**.
2. Under **Scopes**, aktivera `bot` och `applications.commands`.
3. Under **Bot Permissions**, aktivera: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopiera den genererade URL:en, klistra in den i din webbläsare, välj din server och bekräfta. Boten bör nu synas i serverns medlemslista.

#### Samla in dina ID:n

Aktivera Developer Mode i Discord (**User Settings/ Advanced/ Developer Mode**), och gör sedan följande:
- Högerklicka på din serverikon: **Copy Server ID**
- Högerklicka på din egen avatar: **Copy User ID**

#### Tillåt DM från servermedlemmar

Högerklicka på din serverikon/ **Privacy Settings**/ växla på **Direct Messages**. Detta tillåter boten att skicka DM till dig, vilket krävs för parkopplingssteget.

#### Konfigurera OpenClaw för Discord

Lagra din bot-token som en miljövariabel, skapa sedan en enda patchfil som aktiverar Discord, refererar till token och tillåtlistar din server. Ersätt `<server_id>` och `<user_id>` med ID:na du samlade in ovan.

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

> **Förlita dig inte på att be agenten att konfigurera detta.** När sandboxning är aktiverad kan agenten inte skriva till `~/.openclaw/openclaw.json` inifrån sandboxen, använd istället CLI-kommandona ovan på värden.

Starta om gatewayen så att den läser in den nya kanalkonfigurationen:

```bash
openclaw gateway run --bind loopback --port 18789
```

Du bör se `logged in to discord as <bot-name>` i gatewayens utdata inom några sekunder.
#### Para ihop ditt Discord-konto

Skicka ett DM till boten i Discord. Den svarar med en kort parkopplingskod.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Godkänn den på maskinen som kör OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Parkopplingskoder slutar gälla efter en timme.

Du kan nu chatta med din agent direkt från Discord och avlasta uppgifter till din lokala hårdvara.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Alternativ B: Telegram

Telegram är enklare än Discord för de flesta användare, det kräver ingen server och ingen administratörsbehörighet.

#### Skapa en Telegram-bot

1. Öppna Telegram och skicka ett meddelande till **@BotFather**.
2. Skicka `/newbot` och följ instruktionerna. Spara boten-token som du får.

#### Konfigurera OpenClaw för Telegram

Lagra token som en miljövariabel:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Lägg till kanalkonfigurationen i `~/.openclaw/openclaw.json` (eller uppdatera den via instrumentpanelen):

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

Starta om gatewayen och skicka sedan ett meddelande till din bot i Telegram. Godkänn parkopplingen:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Parkopplingskoder slutar gälla efter en timme. Du kan nu chatta med din agent via Telegram-DM.

---

## Nästa steg

Nu när din agent kan ta emot kommandon från din telefon och agera på din lokala maskin finns det tre riktningar som är värda att utforska:

1. **Sammanfattare för aktiemarknaden**: Schemalägg OpenClaw att hämta data från finansiella API:er med fasta intervall, sammanfatta dagens rörelser med din lokala modell och skicka en sammanställning till din telefon varje morgon via den kanal du valt.

2. **Övervakning av finjustering**: Starta ett träningsjobb på distans via Telegram eller Discord, och låt sedan agenten följa träningsloggen och rapportera periodiska förlustvärden, GPU-användning och diskanvändning tillbaka till din telefon. Om körningen stannar upp eller VRAM-användningen ökar kraftigt får du reda på det omedelbart utan att behöva sitta vid maskinen.

3. **IoT med en lokal VLM**: Rikta en kamera mot din ytterdörr, kör en synmodell på Lemonade och låt OpenClaw analysera bilder på begäran eller vid en utlösare. Fråga "kom det några paket idag?" från din telefon och få ett rakt svar från din egen hårdvara.

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