<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

# Zaženite OpenClaw z Lemonade Server kot zaledjem

## Pregled

[**OpenClaw**](https://openclaw.ai/) je avtonomni agent umetne inteligence, ki lahko piše in izvaja kodo, upravlja datoteke ter samostojno opravlja zapletena večkoračna opravila. Za razliko od klepetalnega pomočnika, ki zgolj odgovarja na vprašanja, OpenClaw na vašem sistemu dejansko izvaja ukrepe, zato potrebuje hitro in zmogljivo zaledje umetne inteligence, ki lahko sledi zahtevni zanki agenta.

[**Lemonade Server**](https://lemonade-server.ai/) je to zaledje. Gre za odprtokodni lokalni strežnik za sklepanje, ki modele GenAI zažene neposredno na vaši strojni opremi in jih izpostavi prek industrijsko standardnega API-ja OpenAI.

Skupaj tvorita popolnoma lokalni sklad agenta umetne inteligence: Lemonade poskrbi za sklepanje modela, OpenClaw pa zagotavlja zanko agenta, ki izhode modela pretvori v dejanska dejanja.

> **Preden nadaljujete:** OpenClaw je zelo avtonomen agent umetne inteligence. Dodelitev dostopa do vašega sistema kateremu koli agentu umetne inteligence lahko privede do nepredvidljivih ali nenamernih posledic. Nadaljujte le, če razumete tveganja in vam ustreza, da v vašem imenu deluje avtonomna programska oprema.

---

## Kaj se boste naučili

Do konca tega vodnika boste znali:

- spoznati **Lemonade Server**,
- **namestiti OpenClaw** in ga **usmeriti na Lemonade Server** kot svoje zaledje umetne inteligence,
- **zagnati prehod (gateway) OpenClaw** in potrditi, da je vaš agent pripravljen za delo,
- **povezati komunikacijski kanal** (Discord ali Telegram), da se lahko z agentom pogovarjate s katere koli naprave.

---

## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev zahtevane programske opreme

<!-- @os:linux -->
- Računalnik z operacijskim sistemom **Ubuntu 24.04+** ali združljivo distribucijo Linuxa na osnovi Debiana z `apt-get`
- Vsaj **12 GB pomnilnika RAM** (priporočljivo 64 GB+ za večje modele)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (neobvezno, za peskovnik OpenClaw)
- **približno 10–30 GB prostega prostora na disku** za uteži modela
<!-- @os:end -->

<!-- @os:windows -->
- Računalnik z operacijskim sistemom **Windows 10/11**
- Vsaj **12 GB pomnilnika RAM** (priporočljivo 64 GB+ za večje modele)
- **približno 10–30 GB prostega prostora na disku** za uteži modela
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (neobvezno, za peskovnik OpenClaw)
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

Priporočeni model za ta vodnik je **Qwen3.6-35B-A3B-GGUF** podjetja Unsloth, zmogljiv model MoE z oknom konteksta 263k žetonov, ki je zelo primeren za obremenitve agentov. Ta model uporablja kvantizacijo UD-Q4_K_XL. Prenesite ga zdaj:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Nato ga naložite z velikim oknom konteksta in shranite to nastavitev za prihodnje zagone:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Model ima privzeto dolžino konteksta 262.144 žetonov. Če naletite na napake zaradi pomanjkanja pomnilnika (OOM), razmislite o zmanjšanju okna konteksta. Ker pa Qwen3.6 za zapletena opravila izkorišča razširjen kontekst, priporočamo ohranitev dolžine konteksta vsaj 128K žetonov, da se ohranijo zmožnosti razmišljanja.

> **Nasvet: onemogočite razmišljanje za hitrejše odzive agenta:** Qwen3.6-35B-A3B privzeto deluje v načinu razmišljanja, kar pred vsakim odzivom doda zakasnitev. Pri zankah agenta se ta dodatni čas hitro kopiči. Repozitorij [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) ponuja pripravljeno konfiguracijo, ki onemogoči razmišljanje. Če jo želite uporabiti, prenesite datoteko in jo uvozite:
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

## Nastavitev WSL

OpenClaw zaženemo znotraj WSL (priporočeno) in ga povežemo z Lemonade, ki teče izvorno v sistemu Windows. To vam zagotovi lupinsko okolje Linuxa za OpenClaw, hkrati pa ohrani pospeševanje GPU za Lemonade na strani sistema Windows.

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

Zaprite WSL in ga ponovno zaženite:

```powershell
exit
wsl --shutdown
wsl
```

### Premostite Lemonade iz sistema Windows v WSL

WSL2 teče v navideznem omrežju. Lemonade v sistemu Windows se veže na `127.0.0.1`, do katerega WSL ne more neposredno dostopati. Namestniški vrata (port proxy) sistema Windows posredujejo promet z naslova prehoda WSL na lokalni naslov sistema Windows.

**Poiščite naslov IP prehoda WSL** (zaženite znotraj WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Dodajte namestniška vrata** (zaženite v PowerShellu kot skrbnik, pri čemer `<WSL-Gateway-IP>` zamenjajte z naslovom IP vašega prehoda WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Opomba: Če naletite na napako `netsh: command not found`, poskusite namesto tega uporabiti izrecno ime izvedljive datoteke – `netsh.exe`

**Dodajte pravilo požarnega zidu** (isti povišani PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Preverite iz WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Če ste v prejšnjem koraku že naložili model Qwen3.6-35B-A3B-GGUF, bi morali videti izpis JSON, podoben temu:

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

#### Ohranjanje delovanja mostu po ponovnem zagonu

Pravilo `netsh portproxy` preživi ponovne zagone, vendar se IP prehoda (gateway) za WSL lahko spremeni po ukazu `wsl --shutdown` ali po ponovnem zagonu. Ko se to zgodi, proxy še vedno kaže na stari IP naslov in Lemonade postane nedosegljiv iz WSL. Če se to zgodi, uporabite eno od spodnjih možnosti.

**Možnost 1 (priporočeno) — samodejno popravi most.** Da se temu ne bi bilo treba posvečati ročno vsakič znova, uporabite načrtovano opravilo (scheduled task), ki preveri most ob vsakem zagonu in prijavi ter ga ponovno zgradi le, ko se IP prehoda spremeni. Glejte [Vodnik za samodejno popravilo Lemonade WSL mostu](assets/RepairLemonadeWslBridge.md).


**Možnost 2 — ročno popravi most.** Najprej pridobite trenutni IP prehoda WSL tako, da znotraj WSL zaženete:

```bash
ip route show default | awk '{print $3}' | head -1
```

Kopirajte to vrednost; uporabili jo boste namesto `<new-WSL-Gateway-IP>` spodaj.

Nato v **povišanem PowerShell** (zaženite kot skrbnik) izpišite obstoječa pravila, izbrišite le zastarelo pravilo za Lemonade in dodajte novo s trenutnim IP naslovom:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

V izpisu ukaza `show all` je zastarelo pravilo za Lemonade tisti vnos, katerega naslov povezave (connect address) je `127.0.0.1` na vratih `13305`; njegov naslov poslušanja (listen address) je vaš `<old-WSL-Gateway-IP>`. Brisanje glede na ta naslov odstrani samo to pravilo in ne vpliva na druga pravila portproxy na vašem računalniku.

Pravilo požarnega zidu, ki ste ga dodali med nastavitvijo, je vezano na vrata `13305` (ne na IP), zato še naprej deluje in ga ni treba znova ustvariti.

> **Priporočilo:** Da bi se izognili težavam s prehodom, toplo priporočamo naslednjo konfiguracijo lupine:
> - **Ukazi za Windows** naj se izvajajo v **PowerShell**
> - **Ukazi za WSL distribucijo** naj se izvajajo v **ukaznem pozivu (Command Prompt)** (zagnanem kot **skrbnik**)

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

## Namestitev in konfiguracija OpenClaw

### Namestitev OpenClaw
<!-- @os:windows -->
> Ukaze v tem razdelku zaženite znotraj svojega **terminala WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Zastavica `--no-onboard` preskoči interaktivnega čarovnika za nastavitev, model backend boste ročno konfigurirali v naslednjem koraku, kar vam omogoča natančen nadzor nad tem, kateri model in strežnik se uporabljata.

Odprite nov terminal in potrdite namestitev:

```bash
openclaw --version
```

> **Nasvet:** Če po namestitvi vidite sporočilo `command not found`, dodajte npm-ovo globalno mapo bin v svojo spremenljivko PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Da bo ta sprememba trajna, dodajte zgornjo vrstico v svojo datoteko `~/.bashrc` ali `~/.zshrc`.

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


### Konfiguracija OpenClaw za uporabo Lemonade

Zaženite neinteraktivno uvajanje (onboarding) za OpenClaw.
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

> **Določanje velikosti kontekstnega okna za OpenClaw:** Stiskanje (compaction) OpenClaw se sproži, ko `contextTokens > contextWindow − reserveTokens`. Privzeta vrednost `reserveTokensFloor` je 20.000 žetonov (tokens), spodnja meja, ki prevlada nad `reserveTokens`, kadar je ta nižja, zato bo vsak model s kontekstom pod približno 37 tisoč sprožil neskončno zanko stiskanja. Nastavite nizko rezervo in enkrat v svoji konfiguraciji onemogočite spodnjo mejo, in to velja za vsak model, brez potrebe po prilagajanju za posamezen model:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` je *spodnja meja* (minimalna zaščita), ne rezerva sama, zato nastavitev samo spodnje meje nima učinka. `reserveTokensFloor: 0` onemogoči zaščito, tako da je sprejeta nižja vrednost `reserveTokens`.
>
> **Kdaj to uporabiti:** To konfiguracijo uporabite, če je učinkovito kontekstno okno vašega modela manjše od približno 37 tisoč, bodisi ker je model majhen (npr. 8k, 16k, 32k) bodisi ker ste ga namenoma omejili na nižjo vrednost (npr. nalaganje 128k modela, vendar nastavitev konteksta na 16k v Lemonade). Brez tega OpenClaw ob zagonu vstopi v neskončno zanko stiskanja.
>
> **Modeli z velikim kontekstom pri polnem kontekstu:** To lahko v celoti preskočite. Privzete nastavitve delujejo dobro, stiskanje se sproži precej pred zapolnitvijo okna, model pa ima dovolj prostora za generiranje dolgih odgovorov. Če to vseeno uporabite, se zavedajte, da `reserveTokens: 4096` omeji dolžino odgovora na približno 4 tisoč žetonov, kar lahko prekine generiranje dolgih datotek ali podrobnih načrtov.
>
> **Kam to dodati:** Blok `compaction` postavite znotraj `agents.defaults` v svoji datoteki `openclaw.json` (običajno na `~/.openclaw/openclaw.json`):
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
> Preostanek vaše konfiguracije (gateway, channels, models itd.) ostane nespremenjen, dodati je treba le ključ `compaction`.
### (Priporočeno) Omogočite peskovnik Docker

OpenClaw lahko usmerja vse datotečne in kodne operacije agenta skozi izoliran vsebnik Docker, namesto da bi jih izvajal neposredno na vašem gostitelju. To omeji domet morebitnega nenamernega dejanja na peskovnik, tako da datotečni sistem in omrežje vašega gostitelja ostaneta nedotaknjena.

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

Zaženite naslednje, da dodate ključ `sandbox` znotraj obstoječega bloka `agents.defaults` v `~/.openclaw/openclaw.json`:

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

Vsebniki peskovnika privzeto **nimajo dostopa do omrežja**. Za vezavne priklope (bind mounts) in preglasitve omrežja glejte [referenco o peskovniku](https://docs.openclaw.ai/gateway/sandboxing).

> #### Odpravljanje težav: dostop Docker zavrnjen
> 
> Če pri zagonu ukazov Docker prejmete sporočilo »permission denied«:
> 
> **Korak 1: Dodajte svojega uporabnika v skupino docker**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **Korak 2: Če se napaka še vedno pojavlja, uporabite trajno rešitev**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Nato **znova zaženite** sistem.
> 
> **Hitra začasna rešitev** (ponastavi se po ponovnem zagonu):
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
## (Priporočeno) Integracija OpenClaw s storitvami Firecrawl

[Firecrawl](https://docs.firecrawl.dev/introduction) ponuja samostojno gostovano storitev za pajkanje po spletu in izvlečenje vsebine, ki lahko premosti te izzive in odklene poln potencial avtomatizacije OpenClaw. 

V tej postavitvi OpenClaw teče kot niz vsebnikov Docker, upravljanih s Podman. Za poenostavitev upravljanja življenjskega cikla in samodejnega zagona registriramo Firecrawl kot storitev `systemd` na ravni uporabnika, ki orkestrira spodnji sklad Podman Compose. To omogoča, da OpenClaw zažene prehod (gateway), ga ustavi in preveri storitev Firecrawl z uporabo standardnih ukazov `systemctl --user` namesto neposredne interakcije z vsebniki. 

Da bo stvar preprosta, smo celoten postopek razdelili na štiri korake:

---

### 1. Registracija sistemske storitve
Pomaknite se v mapo z uporabniško konfiguracijo systemd:
```bash
cd ~/.config/systemd/user
```
Ustvarite in odprite novo datoteko z imenom `firecrawl.service`.
```bash
nano firecrawl.service
```
Kopirajte in prilepite naslednjo konfiguracijo:
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
Na tej točki je storitev definirana, vendar še ni registrirana pri `systemd`. 
Poskrbite, da se ime datoteke natančno ujema s tistim, ki ste ga ustvarili zgoraj, nato zaženite:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Če je postopek uspešen, bi morali videti naslednji izpis:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` vsebuje simbolne povezave do storitev, ki so nastavljene za samodejni zagon.

### 2. Konfigurirajte Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) je idealen za tiste, ki potrebujejo popoln nadzor nad svojim okoljem za pajkanje in obdelavo podatkov, vendar prinaša dodatne zahteve po vzdrževanju in konfiguraciji.

Začnite s kloniranjem repozitorija:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Ustvarite `.env` v korenski mapi `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Uvedite OpenClaw s Podman Compose

Preden nadaljujete, se prepričajte, da ste povlekli najnovejšo sliko Docker za OpenClaw:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Ko je to opravljeno, prenesite datoteko Compose za OpenClaw [openclaw-compose.yaml](assets/openclaw-compose.yaml) in jo postavite v korensko mapo `/firecrawl`:

> Ta konvencija je potrebna, da `systemd` pravilno najde in zažene storitev, kot je določeno v `WorkingDirectory=${HOME}/firecrawl`.

> Sklad lahko kadar koli razširite z dodajanjem dodatnih storitev Firecrawl po potrebi. Celoten seznam razpoložljivih storitev najdete v uradni datoteki [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Zaženite storitev OpenClaw prek Firecrawl 

Preden nadzor prepustite `systemd`, preverite, da vse deluje pravilno, tako da sklad zaženete ročno:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Če je vse pravilno konfigurirano, bi morali videti, da se vsebnik OpenClaw zažene, izpis v ukazni vrstici pa naj bi bil podoben temu:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Ko ste preverili, sklad ponovno ustavite, preden nadaljujete:
```bash
podman compose -f openclaw-compose.yaml down
```
Preden zaženete storitev, morate zagotoviti pravilno lastništvo in dovoljenja za mapo `firecrawl` in njeno datoteko `.env`. 
To je nujno, da lahko storitev ob zagonu zapiše vaše poverilnice.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Zdaj, ko je vse preverjeno, zaženite storitev prek `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Dejanja OpenClaw](https://docs.openclaw.ai/) so dostopna znotraj interaktivnega vsebnika, nadzorna plošča (Web Dashboard) pa je na voljo na istem gostitelju in vratih na naslovu http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Pridobitev vašega žetona `OPENCLAW_GATEWAY_TOKEN`

Ko storitev deluje, boste v domači mapi opazili novo mapo `.openclaw` (~/.openclaw). Ta mapa je privzeto zaklenjena, zato jo morate odkleniti, da pridobite svoj žeton za prehod (gateway).

1. Dodelite dostop do mape:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Preberite svoj žeton za prehod:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
V izpisu poiščite vrednost `OPENCLAW_GATEWAY_TOKEN`.

3. Odprite nadzorno ploščo prehoda v brskalniku na naslovu http://127.0.0.1:18789. Ko boste pozvani k avtentikaciji, prilepite svoj žeton.

Za ustavitev storitve zaženite:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
# Zaženite prehod OpenClaw (OpenClaw Gateway)

Prehod je proces OpenClaw, ki upravlja zanko agenta in strežno nadzorno ploščo:

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

Za odprtje nadzorne plošče to zaženite v drugem terminalu, medtem ko prehod še vedno teče:

```bash
openclaw dashboard
```

Ker se prehod poveže na povratno zanko (loopback), se nadzorna plošča ob odprtju iz iste naprave samodejno avtenticira – za lokalni dostop ni potreben vnos žetona ali odobritev naprave. Videli bi morali nadzorno ploščo OpenClaw z vašim modelom Lemonade, navedenim kot aktivnim zaledjem (backend).

> Če ste omogočili peskovnik (sandboxing), lahko to preverite tako, da agenta iz nadzorne plošče prosite, naj `run hostname`. Če namesto imena gostitelja vaše naprave vidite kratek ID zabojnika, peskovnik deluje.

**Čestitamo, zgradili ste popolnoma lokalni sklad agentov AI povsem iz nič.**

> **Potrebujete žeton prehoda?** Zaženite `openclaw dashboard --no-open`, da izpišete URL nadzorne plošče z vgrajenim žetonom (poskuša ga tudi kopirati v odložišče). Žeton je sicer na voljo tudi pod `gateway.auth.token` v `~/.openclaw/openclaw.json`.

**Dostop do nadzorne plošče iz druge naprave (prek predora SSH)**

Če OpenClaw teče na oddaljeni napravi, lahko do njegove nadzorne plošče dostopate iz svoje lokalne naprave prek predora SSH. Predor posreduje vrata prehoda (`18789`), tako da lahko vaš lokalni brskalnik komunicira z oddaljenim prehodom prek `127.0.0.1`.

1. S svoje **lokalne naprave** se enkrat povežite z oddaljeno napravo in sprejmite poziv za prstni odtis, da se gostitelj doda med znane gostitelje:

   ```bash
   ssh user@<host-ip>
   ```

2. Še vedno na svoji **lokalni napravi** odprite predor SSH:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Opomba:** Po vnosu gesla terminal ne prikaže nobenega izpisa in se zdi, kot da je obtičal. To je pričakovano: zastavica `-N` ukazu SSH pove, naj ne zažene nobenega oddaljenega ukaza, tako da le drži predor odprt. Pustite ta terminal odprt.

3. Na svoji **lokalni napravi** odprite brskalnik in pojdite na `http://127.0.0.1:18789`.

4. Na **oddaljeni napravi** izpišite žeton prehoda in ga prilepite v brskalnik za prijavo:

   ```bash
   openclaw dashboard --no-open
   ```

   To izpiše URL nadzorne plošče z vgrajenim žetonom; kopirajte žeton za prijavo. (Žeton je shranjen tudi pod `gateway.auth.token` v `~/.openclaw/openclaw.json`.)

> **Odobritev oddaljene naprave:** Ko odprete nadzorno ploščo iz druge naprave ali telefona, lahko brskalnik prikaže ID zahteve. Na **oddaljeni napravi** izpišite čakajoče zahteve:
> ```bash
> openclaw devices list
> ```
> Nato odobrite ustrezno zahtevo:
> ```bash
> openclaw devices approve <requestId>
> ```
> To je potrebno le za oddaljene ali sekundarne naprave; dostop prek povratne zanke z iste naprave se avtenticira samodejno. Podrobnosti najdete v dokumentaciji [Oddaljeni dostop](https://docs.openclaw.ai/gateway/remote).

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Neobvezno: Povežite komunikacijski kanal

Ko prehod teče, lahko do svojega lokalnega agenta dostopate iz katere koli naprave. Izberite možnost, ki ustreza vaši nastavitvi. OpenClaw podpira [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) in druge kanale – celoten seznam si oglejte na [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Možnost A: Discord

Discord zahteva strežnik, kjer imate **skrbniški dostop**, da lahko dodate bota. Če si strežnike delite z drugimi, vendar ga sami ne lastite, namesto tega uporabite Možnost B (Telegram).

#### Ustvarite račun Discord in strežnik

Če nimate računa Discord, se prijavite na [discord.com](https://discord.com). Potrebujete tudi strežnik, kjer ste skrbnik – ustvarite ga tako, da kliknete ikono **+** v stranski vrstici Discord in izberete **Create My Own**. Zasebni strežnik je povsem v redu.

#### Ustvarite aplikacijo in bota Discord

1. Pojdite na [razvijalski portal Discord](https://discord.com/developers/applications) in kliknite **New Application**. Poimenujte ga (npr. »openclaw-bot«).
2. V stranski vrstici kliknite **Bot**. Nastavite uporabniško ime bota.
3. Še vedno na strani Bot se pomaknite do **Privileged Gateway Intents** in omogočite:
   - **Message Content Intent** (obvezno)
   - **Server Members Intent** (priporočeno)
4. Pomaknite se nazaj navzgor in kliknite **Reset Token**, da ustvarite žeton bota. Kopirajte ga.

#### Dodajte bota v svoj strežnik

1. V stranski vrstici kliknite **OAuth2/ URL Generator**.
2. Pod **Scopes** omogočite `bot` in `applications.commands`.
3. Pod **Bot Permissions** omogočite: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopirajte ustvarjeni URL, prilepite ga v brskalnik, izberite svoj strežnik in potrdite. Bot naj bi se zdaj pojavil na seznamu članov vašega strežnika.

#### Zberite svoje ID-je

V Discordu omogočite razvijalski način (**User Settings/ Advanced/ Developer Mode**), nato:
- Z desno tipko miške kliknite ikono svojega strežnika: **Copy Server ID**
- Z desno tipko miške kliknite svoj lastni avatar: **Copy User ID**

#### Dovolite zasebna sporočila (DM) od članov strežnika

Z desno tipko miške kliknite ikono svojega strežnika/ **Privacy Settings**/ preklopite na vklopljeno **Direct Messages**. To botu omogoči, da vam pošlje zasebno sporočilo, kar je potrebno za korak seznanjanja (pairing).

#### Konfigurirajte OpenClaw za Discord

Shranite žeton svojega bota kot spremenljivko okolja, nato ustvarite eno samo datoteko z popravkom (patch), ki omogoči Discord, sklicuje se na žeton in doda vaš strežnik na dovoljeni seznam. Zamenjajte `<server_id>` in `<user_id>` z ID-ji, zbranimi zgoraj.

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

> **Ne zanašajte se na to, da bi agenta prosili za konfiguracijo tega.** Ko je peskovnik (sandboxing) omogočen, agent iz peskovnika ne more pisati v `~/.openclaw/openclaw.json` – namesto tega na gostitelju uporabite zgornje ukaze CLI.

Znova zaženite prehod, da prevzame novo konfiguracijo kanala:

```bash
openclaw gateway run --bind loopback --port 18789
```

V izpisu prehoda bi morali v nekaj sekundah videti `logged in to discord as <bot-name>`.
#### Poveži svoj Discord račun

Pošlji zasebno sporočilo botu v Discordu. Odgovoril bo s kratko kodo za povezavo.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Odobri jo na napravi, na kateri teče OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Kode za povezavo potečejo po eni uri.

Zdaj se lahko pogovarjaš s svojim agentom neposredno prek Discorda in naloge prepustiš svoji lokalni strojni opremi.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Možnost B: Telegram

Telegram je za večino uporabnikov preprostejši od Discorda, saj ne zahteva strežnika ali skrbniškega dostopa.

#### Ustvari Telegram bota

1. Odpri Telegram in pošlji sporočilo **@BotFather**.
2. Pošlji `/newbot` in sledi navodilom. Shrani žeton bota, ki ga prejmeš.

#### Konfiguriraj OpenClaw za Telegram

Shrani žeton kot spremenljivko okolja:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Dodaj konfiguracijo kanala v `~/.openclaw/openclaw.json` (ali jo popravi prek nadzorne plošče):

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

Ponovno zaženi prehod (gateway), nato pošlji svojemu botu poljubno sporočilo v Telegramu. Odobri povezavo:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Kode za povezavo potečejo po eni uri. Zdaj se lahko s svojim agentom pogovarjaš prek zasebnih sporočil v Telegramu.

---

## Naslednji koraki

Zdaj, ko tvoj agent lahko prejema ukaze iz tvojega telefona in deluje na tvojem lokalnem računalniku, sledijo tri smeri, ki jih velja raziskati:

1. **Povzemalnik borznega trga**: Nastavi OpenClaw, da v fiksnih intervalih pridobiva podatke iz finančnih API-jev, povzame dnevna gibanja z lokalnim modelom in vsako jutro prek izbranega kanala pošlje povzetek na tvoj telefon.

2. **Nadzornik fine nastavitve (fine-tuning)**: Zaženi opravilo učenja na daljavo prek Telegrama ali Discorda, nato naj agent spremlja dnevnik učenja in ti na telefon periodično poroča vrednosti izgube, obremenitev GPE ter porabo diska. Če se izvajanje zatakne ali pride do skoka v porabi VRAM, boš takoj obveščen, ne da bi moral biti pri napravi.

3. **IoT z lokalnim VLM**: Usmeri kamero na svoja vhodna vrata, zaženi vizijski model na Lemonade in naj OpenClaw analizira sličice na zahtevo ali ob sprožilcu. Vprašaj "Ali je danes prispel kakšen paket?" s svojega telefona in dobi neposreden odgovor iz svoje lastne strojne opreme.

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