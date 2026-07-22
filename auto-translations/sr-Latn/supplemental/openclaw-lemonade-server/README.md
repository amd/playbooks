<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije pregledana od strane čoveka. Može sadržati greške, a pojedini koraci, komande, preuzimanja ili dostupnost proizvoda mogu se razlikovati u vašem jeziku ili regionu. Ako nešto izgleda netačno, smatrajte da je originalni engleski playbook merodavan izvor.
<!-- auto-translated-disclaimer:end -->

# Pokrenite OpenClaw sa Lemonade Server kao pozadinskim sistemom

## Pregled

[**OpenClaw**](https://openclaw.ai/) je autonomni AI agent koji može da piše i pokreće kod, upravlja fajlovima i obrađuje složene višestepene zadatke u vaše ime. Za razliku od chat asistenta koji samo odgovara na pitanja, OpenClaw preduzima stvarne akcije na vašem sistemu, što znači da mu je potreban brz i sposoban AI pozadinski sistem koji može da prati zahtevnu petlju agenta.

[**Lemonade Server**](https://lemonade-server.ai/) je taj pozadinski sistem. To je open-source lokalni inferencijski server koji pokreće GenAI modele direktno na vašem hardveru i izlaže ih putem industrijskog standarda OpenAI API-ja.

Zajedno, oni čine potpuno lokalni AI agent stek: Lemonade se bavi inferencijom modela, a OpenClaw obezbeđuje petlju agenta koja pretvara izlaze modela u stvarne akcije.

> **Pre nego što nastavite:** OpenClaw je veoma autonomni AI agent. Davanje bilo kom AI agentu pristupa vašem sistemu može dovesti do nepredvidivih ili nenamernih ishoda. Nastavite samo ako razumete rizike i osećate se prijatno sa autonomnim softverom koji deluje u vaše ime.

---

## Šta ćete naučiti

Do kraja ovog vodiča bićete u mogućnosti da:

- Naučite o **Lemonade Server**
- **Instalirate OpenClaw** i **usmerite ga na Lemonade Server** kao svoj AI pozadinski sistem.
- **Pokrenete OpenClaw gateway** i potvrdite da je vaš agent spreman za rad.
- **Povežete komunikacioni kanal** (Discord ili Telegram) kako biste mogli da ćaskate sa svojim agentom sa bilo kog uređaja.

---

## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Provera ažuriranja softvera

<!-- @require:software-update -->
<!-- @device:end -->

## Instaliranje softverskih preduslova

<!-- @os:linux -->
- Računar sa **Ubuntu 24.04+** ili kompatibilnom Debian distribucijom Linuxa sa `apt-get`
- Najmanje **12 GB RAM-a** (preporučuje se 64 GB+ za veće modele)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (opciono, za sandboxing OpenClaw)

- **~10–30 GB slobodnog prostora na disku** za težine modela
<!-- @os:end -->
<!-- @os:windows -->
- Računar sa **Windows 10/11**
- Najmanje **12 GB RAM-a** (preporučuje se 64 GB+ za veće modele)
- **~10–30 GB slobodnog prostora na disku** za težine modela
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (opciono, za sandboxing OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Preuzimanje i učitavanje preporučenog modela

Preporučeni model za ovaj vodič je **Qwen3.6-35B-A3B-GGUF** od Unsloth, snažan MoE model sa prozorom konteksta od 263k tokena koji je dobro prilagođen radnim opterećenjima agenata. Ovaj model koristi UD-Q4_K_XL kvantizaciju. Preuzmite ga sada:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Zatim ga učitajte sa velikim prozorom konteksta i sačuvajte to podešavanje za buduća pokretanja:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Model ima podrazumevanu dužinu konteksta od 262.144 tokena. Ako naiđete na greške zbog nedostatka memorije (OOM), razmotrite smanjenje prozora konteksta. Međutim, pošto Qwen3.6 koristi prošireni kontekst za složene zadatke, savetujemo da zadržite dužinu konteksta od najmanje 128K tokena kako bi se očuvale sposobnosti razmišljanja.

> **Savet: Onemogućite razmišljanje za brže odgovore agenta:** Qwen3.6-35B-A3B se podrazumevano pokreće u režimu razmišljanja, što dodaje kašnjenje pre svakog odgovora. Za petlje agenta ovo opterećenje se brzo nagomilava. Repozitorijum [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) pruža gotovu konfiguraciju koja onemogućava razmišljanje. Da biste je koristili, preuzmite fajl i uvezite ga:
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

## Podešavanje WSL-a

Pokrećemo OpenClaw unutar WSL-a (preporučeno) i povezujemo ga sa Lemonade koji se izvorno pokreće na Windows-u. Ovo vam daje Linux shell okruženje za OpenClaw, dok se GPU akceleracija Lemonade zadržava na strani Windows-a.

### Instaliranje WSL-a i Ubuntu-a

Otvorite PowerShell kao administrator i instalirajte WSL kernel:

```powershell
wsl --install --no-distribution
```

Zatim instalirajte Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Omogućavanje systemd u WSL-u

Pokrenite ovo unutar Ubuntu terminala:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Ponovo pokrenite WSL:

```powershell
wsl --shutdown
wsl
```

### Premošćavanje Lemonade sa Windows-a u WSL

WSL2 se izvršava u virtuelnoj mreži. Lemonade na Windows-u se povezuje na `127.0.0.1`, do čega WSL ne može direktno da dopre. Windows port proxy prosleđuje saobraćaj sa WSL gateway IP adrese na Windows localhost.

**Pronađite svoju WSL gateway IP adresu** (pokrenite unutar WSL-a):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Dodajte port proxy** (pokrenite u PowerShell-u kao administrator, zamenjujući `<WSL-Gateway-IP>` sa vašom WSL gateway IP adresom):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Dodajte pravilo firewall-a** (isti privilegovani PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Proverite iz WSL-a**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Ako ste već učitali Qwen3.6-35B-A3B-GGUF model u prethodnom koraku, trebalo bi da vidite JSON izlaz poput ovog:

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

> Pravilo `netsh portproxy` opstaje nakon ponovnog pokretanja, ali WSL gateway IP adresa se može promeniti nakon `wsl --shutdown`. Ako Lemonade postane nedostupan iz WSL-a nakon ponovnog pokretanja, dobijte ažuriranu gateway IP adresu i ažurirajte proxy sa ovom novom IP adresom.

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

## Instalacija i konfiguracija OpenClaw

### Instaliranje OpenClaw
<!-- @os:windows -->
> Pokrenite komande u ovom odeljku unutar vašeg **WSL terminala**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Oznaka `--no-onboard` preskače interaktivnog čarobnjaka za podešavanje, konfigurisaćete pozadinski model ručno u sledećem koraku, što vam daje precizniju kontrolu nad tim koji se model i server koriste.

Otvorite novi terminal i potvrdite instalaciju:

```bash
openclaw --version
```

> **Savet:** Ako vidite `command not found` nakon instalacije, dodajte npm-ov globalni bin direktorijum u vaš PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Da biste ovo učinili trajnim, dodajte gornju liniju u vaš `~/.bashrc` ili `~/.zshrc` fajl.

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
### Podešavanje OpenClaw-a za korišćenje Lemonade-a

Pokrenite OpenClaw-ovo neinteraktivno onboarding podešavanje.
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

Ova komanda upisuje OpenClaw-ovu konfiguraciju u `~/.openclaw/openclaw.json`.

> **Podešavanje veličine kontekstnog prozora za OpenClaw:** OpenClaw-ova kompakcija se pokreće kada `contextTokens > contextWindow − reserveTokens`. Podrazumevana vrednost `reserveTokensFloor` je 20.000 tokena, donja granica koja poništava `reserveTokens` kada je niža, tako da bilo koji kontekst modela ispod ~37k pokreće beskonačnu petlju kompakcije. Postavite nisku rezervu i onemogućite donju granicu jednom u vašoj konfiguraciji i to će se primeniti na svaki model, bez potrebe za podešavanjem po modelu:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` je *donja granica* (minimalna zaštita), a ne sama rezerva, postavljanje samo donje granice nema efekta. `reserveTokensFloor: 0` onemogućava zaštitu tako da se prihvata niža vrednost `reserveTokens`.
>
> **Kada ovo primeniti:** Koristite ovu konfiguraciju ako je efektivni kontekstni prozor vašeg modela ispod ~37k, bilo zato što je model mali (npr. 8k, 16k, 32k) ili zato što ste namerno ograničili kontekst na nižu vrednost (npr. učitavanje modela od 128k, ali podešavanje konteksta na 16k u Lemonade-u). Bez ovoga, OpenClaw ulazi u beskonačnu petlju kompakcije prilikom pokretanja.
>
> **Modeli velikog konteksta na punom kontekstu:** Ovo možete potpuno preskočiti. Podrazumevane vrednosti rade dobro, kompakcija će se pokrenuti mnogo pre nego što se prozor popuni, a model ima dovoljno prostora za generisanje dugih odgovora. Ako ipak primenite ovo, imajte na umu da `reserveTokens: 4096` ograničava dužinu odgovora na ~4k tokena, što može prekinuti generisanje dugih fajlova ili detaljnih planova.
>
> **Gde ovo dodati:** Postavite blok `compaction` unutar `agents.defaults` u vašem `openclaw.json` (obično na `~/.openclaw/openclaw.json`):
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
> Ostatak vaše konfiguracije (gateway, kanali, modeli, itd.) ostaje nepromenjen, potrebno je dodati samo ključ `compaction`.

### (Preporučeno) Omogućavanje Docker sandboxing-a

OpenClaw može da usmeri sve operacije nad fajlovima i kodom agenta kroz izolovani Docker kontejner umesto da ih izvršava direktno na vašem host sistemu. Ovo ograničava domet svake nenamerne radnje na sandbox, ostavljajući vaš host fajl sistem i mrežu netaknutim.

Izgradite sandbox image jednom (Docker mora biti instaliran):

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

Pokrenite ovo da biste dodali ključ `sandbox` unutar postojećeg bloka `agents.defaults` u `~/.openclaw/openclaw.json`:

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

Sandbox kontejneri podrazumevano **nemaju pristup mreži**. Pogledajte [referencu za sandboxing](https://docs.openclaw.ai/gateway/sandboxing) za bind mount-ove i mrežna prepisivanja.

> #### Rešavanje problema: Docker Permission Denied
> 
> Ako dobijete grešku „permission denied" prilikom pokretanja Docker komandi:
> 
> **Korak 1: Dodajte vašeg korisnika u docker grupu**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **Korak 2: Ako se greška i dalje javlja, primenite trajno rešenje**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Zatim **restartujte** vaš sistem.
> 
> **Brzo privremeno rešenje** (poništava se nakon restarta):
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
## (Preporučeno) Integracija OpenClaw-a sa Firecrawl uslugama

[Firecrawl](https://docs.firecrawl.dev/introduction) pruža samostalno hostovanu uslugu za pretraživanje veba i izdvajanje sadržaja koja može da zaobiđe ove izazove i otključa pun potencijal OpenClaw automatizacije.

U ovom podešavanju, OpenClaw radi kao skup Docker kontejnera kojima se upravlja pomoću Podman-a. Da bismo pojednostavili upravljanje životnim ciklusom i automatsko pokretanje, registrujemo Firecrawl kao `systemd` uslugu na nivou korisnika koja orkestrira osnovni Podman Compose stek. Ovo omogućava OpenClaw-u da pokrene gateway, zaustavi i proveri Firecrawl uslugu koristeći standardne `systemctl --user` komande umesto direktne interakcije sa kontejnerima.

Da bismo stvari pojednostavili, ceo proces smo podelili u četiri koraka:

---

### 1. Registrovanje sistemske usluge
Idite u direktorijum sa systemd korisničkom konfiguracijom:
```bash
cd ~/.config/systemd/user
```
Kreirajte i otvorite novi fajl pod nazivom `firecrawl.service`.
```bash
nano firecrawl.service
```
Kopirajte i nalepite sledeću konfiguraciju:
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
U ovom trenutku, usluga je definisana, ali još nije registrovana kod `systemd`.
Uverite se da naziv fajla tačno odgovara onom koji ste kreirali iznad, zatim pokrenite:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Ako je uspešno, trebalo bi da vidite sledeći izlaz:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` sadrži simboličke linkove ka uslugama koje su konfigurisane da se pokreću automatski.
### 2. Konfigurišite Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) je idealan za one kojima je potrebna potpuna kontrola nad okruženjima za scraping i obradu podataka, ali dolazi uz kompromis dodatnog održavanja i konfiguracije.

Počnite kloniranjem repozitorijuma:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Napravite `.env` u korenom direktorijumu `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Postavite OpenClaw pomoću Podman Compose

Pre nego što nastavite, uverite se da ste povukli najnoviju OpenClaw Docker sliku:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Kada to uradite, preuzmite OpenClaw Compose fajl [openclaw-compose.yaml](assets/openclaw-compose.yaml) i smestite ga u koreni direktorijum `/firecrawl`:

> Ova konvencija je neophodna da bi `systemd` mogao da pronađe i pokrene servis ispravno, kao što je navedeno u `WorkingDirectory=${HOME}/firecrawl`.

> Uvek možete proširiti stek dodavanjem dodatnih Firecrawl servisa po potrebi. Kompletnu listu dostupnih servisa možete pronaći u zvaničnom [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Pokrenite OpenClaw servis kroz Firecrawl 

Pre nego što prepustite kontrolu `systemd`-u, proverite da li sve radi ispravno tako što ćete ručno pokrenuti stek:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Ako je sve pravilno konfigurisano, trebalo bi da vidite da se OpenClaw kontejner pokreće, a izlaz na komandnoj liniji trebalo bi da izgleda ovako:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Kada to proverite, ugasite stek pre nego što nastavite dalje:
```bash
podman compose -f openclaw-compose.yaml down
```
Pre pokretanja servisa, morate se uveriti da su ispravno podešeni vlasništvo i dozvole za direktorijum `firecrawl` i njegov `.env` fajl. 
Ovo je neophodno da bi servis mogao da upiše vaše kredencijale prilikom pokretanja.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Sada kada je sve provereno, pokrenite servis kroz `systemd`:
```bash
systemctl --user start firecrawl.service
```
[OpenClaw akcije](https://docs.openclaw.ai/) su dostupne iz interaktivnog kontejnera, a Web kontrolna tabla je dostupna na istom hostu i portu na adresi http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Dobijanje vašeg `OPENCLAW_GATEWAY_TOKEN`-a

Kada servis bude pokrenut, primetićete novi direktorijum `.openclaw` kreiran u vašem home direktorijumu (~/.openclaw). Ovaj direktorijum je podrazumevano zaključan, pa ćete morati da ga otključate kako biste dobili svoj gateway token.

1. Odobrite pristup direktorijumu:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Pročitajte svoj gateway token:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Pronađite vrednost `OPENCLAW_GATEWAY_TOKEN` u izlazu.

3. Otvorite kontrolnu tablu gateway-a u svom pretraživaču na adresi http://127.0.0.1:18789. Nalepite svoj token kada budete upitani za autentifikaciju.

Da biste zaustavili servis, pokrenite:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Pokretanje OpenClaw gateway-a

Gateway je OpenClaw proces koji upravlja petljom agenta i servira kontrolnu tablu:

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

Da biste otvorili kontrolnu tablu, pokrenite ovo u drugom terminalu dok je gateway i dalje pokrenut:

```bash
openclaw dashboard
```

Pošto se gateway vezuje za loopback, kontrolna tabla se automatski autentifikuje kada se otvori sa istog računara, tako da nije potreban unos tokena niti odobrenje uređaja za lokalni pristup. Trebalo bi da vidite OpenClaw kontrolnu tablu sa vašim Lemonade modelom navedenim kao aktivnim bekendom.

> Ako ste omogućili sandboxing, možete to proveriti tako što ćete zatražiti od agenta da izvrši `run hostname` iz kontrolne table. Ako vidite kratki ID kontejnera umesto imena hosta vašeg računara, sandbox radi ispravno.

**Čestitamo, izgradili ste potpuno lokalni AI agent stek od nule.**

> **Potreban vam je gateway token?** Pokrenite `openclaw dashboard --no-open` da biste ispisali URL kontrolne table sa ugrađenim tokenom (takođe pokušava da ga kopira u vaš clipboard). Alternativno, token se nalazi na `gateway.auth.token` u `~/.openclaw/openclaw.json`.
>
> **Odobravanje udaljenog uređaja:** Kada otvorite kontrolnu tablu sa drugog računara ili telefona, pretraživač prikazuje ID zahteva. Na računaru na kojem je pokrenut gateway, pokrenite:
> ```bash
> openclaw devices approve <requestId>
> ```
> Ovo je potrebno samo za udaljene ili sekundarne uređaje, loopback pristup sa istog računara se automatski autentifikuje.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Opciono: Povežite komunikacioni kanal

Kada je gateway pokrenut, možete pristupiti svom lokalnom agentu sa bilo kog uređaja. Izaberite opciju koja odgovara vašem podešavanju. OpenClaw podržava [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram), i druge kanale, pogledajte kompletnu listu na [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Opcija A: Discord

Discord zahteva server na kojem **vi imate administratorski pristup** da biste dodali bota. Ako delite servere, ali ih ne posedujete, koristite Opciju B (Telegram) umesto ovoga.

#### Kreiranje Discord naloga i servera

Ako nemate Discord nalog, registrujte se na [discord.com](https://discord.com). Takođe vam je potreban server na kojem ste administrator, kreirajte ga klikom na ikonicu **+** u Discord bočnoj traci i izborom opcije **Create My Own**. Privatni server je sasvim dovoljan.

#### Kreiranje Discord aplikacije i bota

1. Idite na [Discord Developer Portal](https://discord.com/developers/applications) i kliknite na **New Application**. Dajte mu ime (npr. "openclaw-bot").
2. U bočnoj traci kliknite na **Bot**. Postavite korisničko ime za bota.
3. Na istoj Bot stranici, skrolujte do **Privileged Gateway Intents** i omogućite:
   - **Message Content Intent** (obavezno)
   - **Server Members Intent** (preporučeno)
4. Skrolujte nazad na vrh i kliknite na **Reset Token** da biste generisali token vašeg bota. Kopirajte ga.

#### Dodavanje bota na vaš server

1. U bočnoj traci kliknite na **OAuth2/ URL Generator**.
2. Pod **Scopes**, omogućite `bot` i `applications.commands`.
3. Pod **Bot Permissions**, omogućite: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopirajte generisani URL, nalepite ga u pretraživač, izaberite svoj server i potvrdite. Bot bi sada trebalo da se pojavi na listi članova vašeg servera.
#### Prikupite svoje ID-jeve

Omogućite Developer Mode u Discord-u (**User Settings/ Advanced/ Developer Mode**), zatim:
- Desni klik na ikonicu vašeg servera: **Copy Server ID**
- Desni klik na sopstveni avatar: **Copy User ID**

#### Dozvolite DM poruke od članova servera

Desni klik na ikonicu vašeg servera/ **Privacy Settings**/ uključite **Direct Messages**. Ovo omogućava botu da vam pošalje DM poruku, što je neophodno za korak uparivanja.

#### Konfigurišite OpenClaw za Discord

Sačuvajte token vašeg bota kao promenljivu okruženja, zatim kreirajte jednu patch datoteku koja omogućava Discord, referiše token i dodaje vaš server na listu dozvoljenih. Zamenite `<server_id>` i `<user_id>` sa ID-jevima prikupljenim iznad.

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

> **Nemojte se oslanjati na to da tražite od agenta da ovo konfiguriše.** Kada je sandboxing omogućen, agent ne može da piše u `~/.openclaw/openclaw.json` iznutra iz sandboxa, umesto toga koristite gore navedene CLI komande na hostu.

Ponovo pokrenite gateway kako bi preuzeo novu konfiguraciju kanala:

```bash
openclaw gateway run --bind loopback --port 18789
```

Trebalo bi da vidite `logged in to discord as <bot-name>` u izlazu gateway-a u roku od nekoliko sekundi.

#### Uparite svoj Discord nalog

Pošaljite DM poruku botu na Discord-u. On će odgovoriti kratkim kodom za uparivanje.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Odobrite to na mašini na kojoj radi OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Kodovi za uparivanje ističu nakon sat vremena.

Sada možete direktno da ćaskate sa svojim agentom iz Discord-a i prebacujete zadatke na svoj lokalni hardver.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Opcija B: Telegram

Telegram je jednostavniji od Discord-a za većinu korisnika, ne zahteva server niti administratorski pristup.

#### Kreirajte Telegram bota

1. Otvorite Telegram i pošaljite poruku **@BotFather**.
2. Pošaljite `/newbot` i pratite uputstva. Sačuvajte token bota koji dobijete.

#### Konfigurišite OpenClaw za Telegram

Sačuvajte token kao promenljivu okruženja:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Dodajte konfiguraciju kanala u `~/.openclaw/openclaw.json` (ili je patch-ujte preko dashboard-a):

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

Ponovo pokrenite gateway, zatim pošaljite vašem botu bilo koju poruku na Telegram-u. Odobrite uparivanje:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Kodovi za uparivanje ističu nakon sat vremena. Sada možete da ćaskate sa svojim agentom putem Telegram DM poruka.

---

## Sledeći koraci

Sada kada vaš agent može da prima komande sa vašeg telefona i deluje na vašoj lokalnoj mašini, evo tri pravca vredna istraživanja:

1. **Sumiranje berzanskog tržišta**: Zakažite OpenClaw da povlači podatke iz finansijskih API-jeva u fiksnom intervalu, sumira dnevna kretanja pomoću vašeg lokalnog modela i šalje pregled na vaš telefon svako jutro putem izabranog kanala.

2. **Praćenje fino-podešavanja (fine-tuning)**: Pokrenite trening posao daljinski putem Telegram-a ili Discord-a, zatim neka agent prati (tail) log treninga i izveštava periodično o vrednostima gubitka (loss), iskorišćenosti GPU-a i upotrebi diska nazad na vaš telefon. Ako se pokretanje zaustavi ili dođe do skoka VRAM-a, saznaćete odmah bez potrebe da budete pored mašine.

3. **IOT sa lokalnim VLM-om**: Usmerite kameru ka vašim ulaznim vratima, pokrenite vizuelni model na Lemonade-u i neka OpenClaw analizira kadrove na zahtev ili na osnovu okidača. Pitajte "da li su danas stigli neki paketi?" sa vašeg telefona i dobijte direktan odgovor sa sopstvenog hardvera.

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