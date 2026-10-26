<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

# Pokrenite OpenClaw sa Lemonade Server kao pozadinskim sistemom

## Pregled

[**OpenClaw**](https://openclaw.ai/) je autonomni AI agent koji može da piše i pokreće kod, upravlja fajlovima i obavlja složene višestepene zadatke u vaše ime. Za razliku od chat asistenta koji samo odgovara na pitanja, OpenClaw preduzima stvarne akcije na vašem sistemu, što znači da mu je potreban brz, sposoban AI pozadinski sistem koji može da isprati zahtevnu petlju agenta.

[**Lemonade Server**](https://lemonade-server.ai/) je taj pozadinski sistem. To je open-source lokalni inferencijski server koji pokreće GenAI modele direktno na vašem hardveru i izlaže ih putem industrijski standardnog OpenAI API-ja.

Zajedno, oni čine potpuno lokalni AI agent stek: Lemonade se bavi inferencijom modela, a OpenClaw pruža petlju agenta koja pretvara izlaze modela u stvarne akcije.

> **Pre nego što nastavite:** OpenClaw je visoko autonomni AI agent. Davanje bilo kom AI agentu pristupa vašem sistemu može dovesti do nepredvidivih ili neželjenih ishoda. Nastavite samo ako razumete rizike i osećate se prijatno sa autonomnim softverom koji deluje u vaše ime.

---

## Šta ćete naučiti

Do kraja ovog vodiča bićete u mogućnosti da:

- Naučite o **Lemonade Server**-u
- **Instalirate OpenClaw** i **usmerite ga na Lemonade Server** kao njegov AI pozadinski sistem.
- **Pokrenete OpenClaw gateway** i potvrdite da je vaš agent spreman za rad.
- **Povežete komunikacioni kanal** (Discord ili Telegram) kako biste mogli da komunicirate sa svojim agentom sa bilo kog uređaja.

---

<!-- @device:halo_box,halo,stx,krk -->
## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Proverite ažuriranja softvera

<!-- @require:software-update -->
<!-- @device:end -->

## Instaliranje potrebnih softverskih preduslova

<!-- @os:linux -->
- Računar sa **Ubuntu 24.04+** ili kompatibilnom Debian-baziranom Linux distribucijom sa `apt-get`
- Najmanje **12 GB RAM-a** (preporučuje se 64 GB+ za veće modele)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (opciono, za izolaciju OpenClaw-a u sandbox okruženju)
- **~10–30 GB slobodnog prostora na disku** za težine modela
<!-- @os:end -->

<!-- @os:windows -->
- Računar sa **Windows 10/11**
- Najmanje **12 GB RAM-a** (preporučuje se 64 GB+ za veće modele)
- **~10–30 GB slobodnog prostora na disku** za težine modela
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (opciono, za izolaciju OpenClaw-a u sandbox okruženju)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Preuzmite i učitajte preporučeni model

Preporučeni model za ovaj vodič je **Qwen3.6-35B-A3B-GGUF** od Unsloth, snažan MoE model sa kontekstnim prozorom od 263k tokena koji je vrlo pogodan za radna opterećenja agenata. Ovaj model koristi UD-Q4_K_XL kvantizaciju. Preuzmite ga sada:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Zatim ga učitajte sa velikim kontekstnim prozorom i sačuvajte to podešavanje za buduća pokretanja:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Model ima podrazumevanu dužinu konteksta od 262.144 tokena. Ako naiđete na greške zbog nedostatka memorije (OOM), razmotrite smanjenje kontekstnog prozora. Međutim, pošto Qwen3.6 koristi proširen kontekst za složene zadatke, savetujemo da održavate dužinu konteksta od najmanje 128K tokena kako biste sačuvali sposobnosti razmišljanja.

> **Savet: Onemogućite razmišljanje za brže odgovore agenta:** Qwen3.6-35B-A3B podrazumevano radi u režimu razmišljanja, što dodaje kašnjenje pre svakog odgovora. Za petlje agenata ovaj dodatni teret se brzo gomila. Repozitorijum [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) pruža gotovu konfiguraciju koja onemogućava razmišljanje. Da biste je koristili, preuzmite fajl i uvezite ga:
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

Pokrećemo OpenClaw unutar WSL-a (preporučeno) i povezujemo ga sa Lemonade-om koji radi nativno na Windows-u. Ovo vam pruža Linux shell okruženje za OpenClaw dok se Lemonade-ovo GPU ubrzanje zadržava na Windows strani.

### Instalirajte WSL i Ubuntu

Otvorite PowerShell kao administrator i instalirajte WSL kernel:

```powershell
wsl --install --no-distribution
```

Zatim instalirajte Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Omogućite systemd u WSL-u

Pokrenite ovo unutar Ubuntu terminala:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Izađite iz WSL-a i ponovo ga pokrenite:

```powershell
exit
wsl --shutdown
wsl
```

### Premostite Lemonade sa Windows-a u WSL

WSL2 radi u virtuelnoj mreži. Lemonade na Windows-u se vezuje za `127.0.0.1`, kojoj WSL ne može direktno da pristupi. Windows port proxy prosleđuje saobraćaj sa WSL gateway IP adrese na Windows localhost.

**Pronađite svoju WSL gateway IP adresu** (pokrenite unutar WSL-a):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Dodajte port proxy** (pokrenite u PowerShell-u kao administrator, zamenjujući `<WSL-Gateway-IP>` sa vašom WSL gateway IP adresom):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Napomena: Ako naiđete na grešku `netsh: command not found`, pokušajte da umesto toga koristite eksplicitni naziv izvršne datoteke - `netsh.exe`

**Dodajte pravilo zaštitnog zida** (isti podignuti PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Proverite iz WSL-a**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Ako ste već učitali model Qwen3.6-35B-A3B-GGUF u prethodnom koraku, trebalo bi da vidite JSON izlaz poput ovog:

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

#### Održavanje mosta funkcionalnim nakon restarta

Pravilo `netsh portproxy` opstaje nakon restarta, ali se IP adresa WSL gateway-a može promeniti nakon `wsl --shutdown` ili restarta. Kada se to desi, proksi i dalje pokazuje na staru IP adresu i Lemonade postaje nedostupan iz WSL-a. Ako se to dogodi, koristite jednu od opcija ispod.

**Opcija 1 (preporučeno) — Automatska popravka mosta.** Da biste izbegli ručno ponavljanje ovog postupka svaki put, koristite zakazani zadatak koji proverava most pri svakom pokretanju i prijavljivanju i ponovo ga izgrađuje samo kada se IP adresa gateway-a promenila. Pogledajte [vodič za automatsku popravku Lemonade WSL mosta](assets/RepairLemonadeWslBridge.md).


**Opcija 2 — Ručna popravka mosta.** Prvo, dobijte trenutnu IP adresu WSL gateway-a pokretanjem sledećeg unutar WSL-a:

```bash
ip route show default | awk '{print $3}' | head -1
```

Kopirajte ovu vrednost; koristićete je umesto `<new-WSL-Gateway-IP>` ispod.

Zatim, u **elevated PowerShell-u** (Run as administrator), izlistajte postojeća pravila, obrišite samo zastarelo Lemonade pravilo, i dodajte novo sa trenutnom IP adresom:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

U izlazu komande `show all`, zastarelo Lemonade pravilo je unos čija je connect adresa `127.0.0.1` na portu `13305`; njegova listen adresa je vaš `<old-WSL-Gateway-IP>`. Brisanje po toj adresi uklanja samo ovo pravilo i ostavlja sva ostala port-proxy pravila na vašem računaru netaknuta.

Pravilo zaštitnog zida koje ste dodali tokom podešavanja je vezano za port `13305` (a ne za IP adresu), tako da nastavlja da radi i ne mora se ponovo kreirati.

> **Preporuka:** Da biste izbegli probleme sa gateway-om, snažno predlažemo sledeću konfiguraciju ljuske:
> - **Windows komande** treba izvršavati u **PowerShell-u**
> - **Komande WSL distribucije** treba izvršavati u **Command Prompt-u** (pokrenutom kao **Administrator**)

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

## Instalacija i konfigurisanje OpenClaw

### Instalacija OpenClaw
<!-- @os:windows -->
> Pokrenite komande iz ovog odeljka unutar vašeg **WSL terminala**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Oznaka `--no-onboard` preskače interaktivnog čarobnjaka za podešavanje, model backend ćete konfigurisati ručno u sledećem koraku, što vam daje preciznu kontrolu nad tim koji se model i server koriste.

Otvorite novi terminal i potvrdite instalaciju:

```bash
openclaw --version
```

> **Savet:** Ako nakon instalacije vidite `command not found`, dodajte npm-ov globalni bin direktorijum u vaš PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Da biste ovo učinili trajnim, dodajte gornju liniju u svoj `~/.bashrc` ili `~/.zshrc` fajl.

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


### Konfigurisanje OpenClaw za korišćenje Lemonade

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

> **Podešavanje veličine kontekstnog prozora za OpenClaw:** OpenClaw-ova kompakcija se aktivira kada `contextTokens > contextWindow − reserveTokens`. Podrazumevani `reserveTokensFloor` je 20.000 tokena, granica koja poništava `reserveTokens` kada je niža, tako da će bilo koji model sa kontekstom ispod ~37k izazvati beskonačnu petlju kompakcije. Postavite nisku rezervu i onemogućite granicu jednom u svojoj konfiguraciji i to će se primeniti na svaki model, bez potrebe za podešavanjem po modelu:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` je *donja granica* (minimalna zaštita), a ne sama rezerva, postavljanje samo granice nema efekta. `reserveTokensFloor: 0` onemogućava zaštitu tako da se niži `reserveTokens` prihvata.
>
> **Kada ovo primeniti:** Koristite ovu konfiguraciju ako je efektivni kontekstni prozor vašeg modela ispod ~37k, bilo zato što je model mali (npr. 8k, 16k, 32k) ili zato što ste ga namerno ograničili na nižu vrednost (npr. učitavate model od 128k, ali postavljate kontekst na 16k u Lemonade). Bez ovoga, OpenClaw ulazi u beskonačnu petlju kompakcije pri pokretanju.
>
> **Modeli sa velikim kontekstom na punom kontekstu:** Ovo možete potpuno preskočiti. Podrazumevane vrednosti rade dobro, kompakcija će se aktivirati mnogo pre nego što se prozor popuni i model ima dovoljno prostora za generisanje dugih odgovora. Ako ovo ipak primenite, imajte u vidu da `reserveTokens: 4096` ograničava dužinu odgovora na ~4k tokena, što može prekinuti generisanje dugog fajla ili detaljnih planova.
>
> **Gde ovo dodati:** Postavite blok `compaction` unutar `agents.defaults` u svom `openclaw.json` (obično na `~/.openclaw/openclaw.json`):
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
### (Preporučeno) Omogućavanje Docker sandboksinga

OpenClaw može da usmeri sve operacije agenta nad fajlovima i kodom kroz izolovani Docker kontejner umesto da ih pokreće direktno na vašem hostu. Ovo ograničava domet svake nenamerne akcije na sandboks, ostavljajući fajl sistem i mrežu vašeg hosta netaknutim.

Izgradite sandboks image jednom (Docker mora biti instaliran):

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

Sandboks kontejneri podrazumevano **nemaju pristup mreži**. Pogledajte [referencu za sandboksing](https://docs.openclaw.ai/gateway/sandboxing) za bind mount-ove i mrežna prepisivanja.

> #### Rešavanje problema: Docker Permission Denied
> 
> Ako dobijete grešku „permission denied“ prilikom pokretanja Docker komandi:
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
> **Korak 2: Ako se greška ponavlja, primenite trajno rešenje**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Zatim **restartujte** sistem.
> 
> **Brzo privremeno rešenje** (resetuje se posle restarta):
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
## (Preporučeno) OpenClaw integracija sa Firecrawl servisima

[Firecrawl](https://docs.firecrawl.dev/introduction) obezbeđuje samostalno hostovanu uslugu za veb-pretraživanje i izdvajanje sadržaja koja može da zaobiđe ove izazove i otključa pun potencijal OpenClaw automatizacije.

U ovoj konfiguraciji, OpenClaw se izvršava kao skup Docker kontejnera kojima upravlja Podman. Da bismo pojednostavili upravljanje životnim ciklusom i automatsko pokretanje, registrujemo Firecrawl kao `systemd` uslugu na nivou korisnika koja orkestrira odgovarajući Podman Compose stek. Ovo omogućava OpenClaw-u da pokrene gateway, zaustavi ga i proveri Firecrawl uslugu korišćenjem standardnih `systemctl --user` komandi umesto direktne interakcije sa kontejnerima.

Da bismo pojednostavili stvari, ceo proces smo podelili u četiri koraka:

---

### 1. Registrovanje sistemske usluge
Idite u direktorijum konfiguracije systemd korisnika:
```bash
cd ~/.config/systemd/user
```
Napravite i otvorite novi fajl pod imenom `firecrawl.service`.
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
U ovom trenutku, usluga je definisana, ali još uvek nije registrovana kod `systemd`. 
Uverite se da se ime fajla tačno poklapa sa onim koji ste napravili iznad, a zatim pokrenite:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Ako je uspešno, trebalo bi da vidite sledeći izlaz:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` sadrži simboličke linkove ka uslugama koje su konfigurisane da se automatski pokreću.

### 2. Konfigurisanje Firecrawl-a

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) je idealan za one kojima je potrebna potpuna kontrola nad okruženjem za prikupljanje i obradu podataka, ali dolazi uz kompromis dodatnog održavanja i konfigurisanja.

Počnite kloniranjem repozitorijuma:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Napravite fajl `.env` u direktorijumu `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Postavljanje OpenClaw-a pomoću Podman Compose-a

Pre nego što nastavite dalje, uverite se da ste povukli najnoviji OpenClaw Docker image:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Kada to obavite, preuzmite OpenClaw Compose fajl [openclaw-compose.yaml](assets/openclaw-compose.yaml) i postavite ga u koreni direktorijum `/firecrawl`:

> Ova konvencija je neophodna kako bi `systemd` mogao da pronađe i pokrene uslugu ispravno, kao što je navedeno u `WorkingDirectory=${HOME}/firecrawl`.

> Uvek možete proširiti stek dodavanjem dodatnih Firecrawl usluga po potrebi. Kompletan spisak dostupnih usluga možete pronaći u zvaničnom [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) fajlu.

### 4. Pokretanje OpenClaw usluge kroz Firecrawl 

Pre nego što predate kontrolu `systemd`-u, proverite da li sve radi ispravno tako što ćete ručno pokrenuti stek:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Ako je sve ispravno konfigurisano, trebalo bi da vidite da se OpenClaw kontejner podiže, a izlaz komandne linije bi trebalo da izgleda slično ovome:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Kada to proverite, ugasite stek pre nego što nastavite:
```bash
podman compose -f openclaw-compose.yaml down
```
Pre pokretanja usluge, morate obezbediti ispravno vlasništvo i dozvole nad direktorijumom `firecrawl` i njegovim `.env` fajlom. 
Ovo je neophodno kako bi usluga mogla da upiše vaše kredencijale prilikom pokretanja.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Sada kada je sve provereno, pokrenite uslugu kroz `systemd`:
```bash
systemctl --user start firecrawl.service
```
[OpenClaw akcije](https://docs.openclaw.ai/) su dostupne iz interaktivnog kontejnera, a Web Dashboard je dostupan na istom hostu i portu na adresi http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Dobijanje vašeg `OPENCLAW_GATEWAY_TOKEN`

Kada usluga bude pokrenuta i radi, primetićete novi direktorijum `.openclaw` kreiran u vašem home direktorijumu (~/.openclaw). Ovaj direktorijum je podrazumevano zaključan, pa ćete morati da ga otključate da biste dobili svoj gateway token.

1. Dodelite pristup direktorijumu:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Pročitajte svoj gateway token:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Pronađite vrednost `OPENCLAW_GATEWAY_TOKEN` u izlazu.

3. Otvorite gateway dashboard u vašem pretraživaču na http://127.0.0.1:18789. Nalepite svoj token kada bude zatraženo radi autentikacije.

Da biste zaustavili uslugu, pokrenite:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Pokretanje OpenClaw Gateway-a

Gateway je OpenClaw proces koji upravlja petljom agenta i servira kontrolnu tablu (dashboard):

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

Da biste otvorili kontrolnu tablu, pokrenite ovo u drugom terminalu dok gateway i dalje radi:

```bash
openclaw dashboard
```

Pošto se gateway povezuje na loopback, kontrolna tabla se automatski autentifikuje kada se otvori sa istog računara, nije potreban unos tokena niti odobrenje uređaja za lokalni pristup. Trebalo bi da vidite OpenClaw kontrolnu tablu sa vašim Lemonade modelom navedenim kao aktivnim bekendom.

> Ako ste omogućili sandboxing, možete to proveriti tako što ćete zatražiti od agenta da izvrši `run hostname` iz kontrolne table. Ako vidite kratak ID kontejnera umesto imena vašeg računara, sandbox radi ispravno.

**Čestitamo, izgradili ste potpuno lokalni AI agent stek od nule.**

> **Potreban vam je gateway token?** Pokrenite `openclaw dashboard --no-open` da biste ispisali URL kontrolne table sa ugrađenim tokenom (takođe pokušava da ga kopira u vaš clipboard). Alternativno, token se nalazi u `gateway.auth.token` u `~/.openclaw/openclaw.json`.

**Pristupanje kontrolnoj tabli sa drugog uređaja (putem SSH tunela)**

Ako OpenClaw radi na udaljenom računaru, možete pristupiti njegovoj kontrolnoj tabli sa vašeg lokalnog računara putem SSH tunela. Tunel prosleđuje gateway port (`18789`) tako da vaš lokalni pregledač može da komunicira sa udaljenim gateway-om preko `127.0.0.1`.

1. Sa vašeg **lokalnog računara**, povežite se jednom sa udaljenim računarom i prihvatite upit sa otiskom (fingerprint) kako bi host bio dodat u vaše poznate hostove:

   ```bash
   ssh user@<host-ip>
   ```

2. I dalje na vašem **lokalnom računaru**, otvorite SSH tunel:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Napomena:** Nakon što unesete lozinku, terminal ne prikazuje nikakav izlaz i deluje kao da je zaglavljen. Ovo je očekivano: `-N` flag govori SSH-u da ne pokreće nijednu udaljenu komandu, tako da on jednostavno drži tunel otvorenim. Ostavite ovaj terminal da radi.

3. Na vašem **lokalnom računaru**, otvorite pregledač i idite na `http://127.0.0.1:18789`.

4. Na **udaljenom računaru**, ispišite gateway token i nalepite ga u pregledač da biste se prijavili:

   ```bash
   openclaw dashboard --no-open
   ```

   Ovo ispisuje URL kontrolne table sa ugrađenim tokenom; kopirajte token da biste se prijavili. (Token je takođe sačuvan u `gateway.auth.token` u `~/.openclaw/openclaw.json`.)

> **Odobravanje udaljenog uređaja:** Kada otvorite kontrolnu tablu sa drugog računara ili telefona, pregledač može prikazati ID zahteva. Na **udaljenom računaru**, prikažite listu zahteva na čekanju:
> ```bash
> openclaw devices list
> ```
> Zatim odobrite odgovarajući zahtev:
> ```bash
> openclaw devices approve <requestId>
> ```
> Ovo je potrebno samo za udaljene ili sekundarne uređaje; loopback pristup sa istog računara se autentifikuje automatski. Za detalje pogledajte dokumentaciju [Remote Access](https://docs.openclaw.ai/gateway/remote).

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Opcionalno: Povežite kanal za komunikaciju

Kada gateway radi, možete pristupiti vašem lokalnom agentu sa bilo kog uređaja. Izaberite opciju koja odgovara vašoj konfiguraciji. OpenClaw podržava [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram), i druge kanale, pogledajte kompletnu listu na [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Opcija A: Discord

Discord zahteva server na kome **imate administratorski pristup** kako biste mogli da dodate bota. Ako delite servere ali ne posedujete nijedan, koristite Opciju B (Telegram) umesto ovoga.

#### Kreirajte Discord nalog i server

Ako nemate Discord nalog, registrujte se na [discord.com](https://discord.com). Takođe vam je potreban server na kome ste administrator, kreirajte ga klikom na ikonicu **+** u Discord bočnoj traci i izborom opcije **Create My Own**. Privatan server je sasvim dovoljan.

#### Kreirajte Discord aplikaciju i bota

1. Idite na [Discord Developer Portal](https://discord.com/developers/applications) i kliknite na **New Application**. Dodelite mu ime (npr. "openclaw-bot").
2. U bočnoj traci kliknite na **Bot**. Podesite korisničko ime za bota.
3. I dalje na stranici Bot, skrolujte do **Privileged Gateway Intents** i omogućite:
   - **Message Content Intent** (obavezno)
   - **Server Members Intent** (preporučeno)
4. Skrolujte nazad na vrh i kliknite na **Reset Token** da biste generisali token vašeg bota. Kopirajte ga.

#### Dodajte bota na vaš server

1. U bočnoj traci kliknite na **OAuth2/ URL Generator**.
2. Pod **Scopes**, omogućite `bot` i `applications.commands`.
3. Pod **Bot Permissions**, omogućite: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopirajte generisani URL, nalepite ga u pregledač, izaberite vaš server i potvrdite. Bot bi sada trebalo da se pojavi na listi članova vašeg servera.

#### Prikupite vaše ID-jeve

Omogućite Developer Mode u Discordu (**User Settings/ Advanced/ Developer Mode**), zatim:
- Desni klik na ikonicu vašeg servera: **Copy Server ID**
- Desni klik na vaš avatar: **Copy User ID**

#### Dozvolite DM-ove od članova servera

Desni klik na ikonicu vašeg servera/ **Privacy Settings**/ uključite **Direct Messages**. Ovo omogućava botu da vam pošalje direktnu poruku, što je neophodno za korak uparivanja.

#### Konfigurišite OpenClaw za Discord

Sačuvajte token vašeg bota kao promenljivu okruženja, zatim kreirajte jedinstvenu patch datoteku koja omogućava Discord, referiše na token i dodaje vaš server na dozvoljenu listu. Zamenite `<server_id>` i `<user_id>` sa ID-jevima prikupljenim iznad.

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

> **Nemojte se oslanjati na to da tražite od agenta da ovo konfiguriše.** Kada je sandboxing omogućen, agent ne može da piše u `~/.openclaw/openclaw.json` iz sandbox-a, umesto toga koristite gore navedene CLI komande na hostu.

Restartujte gateway kako bi preuzeo novu konfiguraciju kanala:

```bash
openclaw gateway run --bind loopback --port 18789
```

Trebalo bi da vidite `logged in to discord as <bot-name>` u izlazu gateway-a u roku od nekoliko sekundi.
#### Uparite svoj Discord nalog

Pošaljite botu privatnu poruku (DM) na Discord-u. On će odgovoriti kratkim kodom za uparivanje.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Odobrite ga na mašini na kojoj je pokrenut OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Kodovi za uparivanje ističu nakon jednog sata.

Sada možete direktno da ćaskate sa svojim agentom preko Discord-a i prebacujete zadatke na svoj lokalni hardver.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Opcija B: Telegram

Telegram je jednostavniji od Discord-a za većinu korisnika, jer ne zahteva ni server ni administratorski pristup.

#### Kreiranje Telegram bota

1. Otvorite Telegram i pošaljite poruku **@BotFather**-u.
2. Pošaljite `/newbot` i pratite uputstva. Sačuvajte token bota koji dobijete.

#### Konfigurisanje OpenClaw-a za Telegram

Sačuvajte token kao promenljivu okruženja:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Dodajte konfiguraciju kanala u `~/.openclaw/openclaw.json` (ili je izmenite preko kontrolne table):

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

Restartujte gateway, a zatim pošaljite svom botu bilo koju poruku na Telegram-u. Odobrite uparivanje:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Kodovi za uparivanje ističu nakon jednog sata. Sada možete da ćaskate sa svojim agentom preko Telegram direktnih poruka.

---

## Sledeći koraci

Sada kada vaš agent može da prima komande sa vašeg telefona i deluje na vašoj lokalnoj mašini, evo tri pravca koje vredi istražiti:

1. **Sumator berzanskih kretanja**: Zakažite OpenClaw da preuzima podatke sa finansijskih API-ja u fiksnom intervalu, sumira dnevna kretanja pomoću vašeg lokalnog modela i šalje pregled na vaš telefon svakog jutra preko izabranog kanala.

2. **Praćenje fino podešavanja (fine-tuning)**: Pokrenite zadatak treniranja daljinski preko Telegram-a ili Discord-a, a zatim neka agent prati log treniranja i izveštava periodično o vrednostima gubitka (loss), iskorišćenosti GPU-a i korišćenju diska nazad na vaš telefon. Ako se proces zaglavi ili VRAM naglo poraste, odmah ćete saznati bez potrebe da budete pored mašine.

3. **IOT sa lokalnim VLM-om**: Usmerite kameru ka svojim ulaznim vratima, pokrenite model za vid na Lemonade-u i neka OpenClaw analizira kadrove na zahtev ili prilikom okidača. Pitajte "da li je danas stigao neki paket?" sa svog telefona i dobićete direktan odgovor sa sopstvenog hardvera.

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